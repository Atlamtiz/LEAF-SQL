import json
import asyncio
import os
import yaml
import time
import random
from collections import defaultdict
from tqdm.asyncio import tqdm
from src.lwss import lwss_async
from src.sqlgen import sql_generation_async
from src.get_db_schema import get_db_schema_w_fk
from src.result_selection import result_selection_async, execute_sql_async

async def worker_sql_gen(skeleton_queue, sql_queue, db_schema, question, config, stats, metrics):
    tasks = []
    
    async def process_skeleton(skeleton):
        try:
            if "sqlgen_start" not in metrics:
                metrics["sqlgen_start"] = time.time()
            
            sqls = await sql_generation_async(
                db_schema, question, skeleton, 
                config["base_url"], config["api_key"], config["model_name"], 
                stats
            )
            for sql in sqls:
                await sql_queue.put(sql)
            
            metrics["sqlgen_last_activity"] = time.time()
        except Exception:
            pass

    while True:
        skeleton = await skeleton_queue.get()
        if skeleton is None:
            break
        t = asyncio.create_task(process_skeleton(skeleton))
        tasks.append(t)
        skeleton_queue.task_done()
    
    if tasks:
        await asyncio.gather(*tasks)
    
    metrics["sqlgen_end"] = time.time()

async def worker_executor(sql_queue, execution_results, generated_sqls, db_path, stats, metrics):
    tasks = []
    
    async def process_sql(sql):
        try:
            if "rs_start" not in metrics:
                metrics["rs_start"] = time.time()
                
            res = await execute_sql_async(db_path, sql)
            execution_results[sql] = res
            generated_sqls.append(sql)
            
            metrics["rs_last_activity"] = time.time()
        except Exception:
            pass

    while True:
        sql = await sql_queue.get()
        if sql is None:
            break
        t = asyncio.create_task(process_sql(sql))
        tasks.append(t)
        sql_queue.task_done()
        
    if tasks:
        await asyncio.gather(*tasks)

async def process_item(data, paths, config, global_results):
    db_id = data["db_id"]
    question = data["question"]
    db_path = f"{paths['databases_path']}/{db_id}/{db_id}.sqlite"
    
    try:
        db_schema = get_db_schema_w_fk(db_path, db_id, paths["tables_path"])
    except Exception:
        return

    skefor_config = config["skefor_config"]
    skeeva_config = config["skeeva_config"]
    llm_call_config = config["llm_call_config"]
    
    api_keys = llm_call_config.get("api_keys", [])
    if not api_keys and "api_key" in llm_call_config:
        api_keys = [llm_call_config["api_key"]]
    
    current_api_key = random.choice(api_keys) if api_keys else "EMPTY"
    
    task_llm_config = llm_call_config.copy()
    task_llm_config["api_key"] = current_api_key
    
    stats = defaultdict(int)
    metrics = {}
    
    skeleton_queue = asyncio.Queue()
    sql_queue = asyncio.Queue()
    
    execution_results = {}
    generated_sqls = []
    
    start_total = time.time()
    
    sql_gen_task = asyncio.create_task(worker_sql_gen(
        skeleton_queue, sql_queue, db_schema, question, task_llm_config, stats, metrics
    ))
    
    executor_task = asyncio.create_task(worker_executor(
        sql_queue, execution_results, generated_sqls, db_path, stats, metrics
    ))
    
    metrics["lwss_start"] = time.time()
    try:
        await lwss_async(
            db_schema, question,
            skefor_config["base_url"], skefor_config["api_key"], skefor_config["model_name"], skefor_config["m"],
            skeeva_config["base_url"], skeeva_config["api_key"], skeeva_config["model_name"],
            output_queue=skeleton_queue, stats=stats
        )
    except Exception:
        pass
    metrics["lwss_end"] = time.time()
    
    await skeleton_queue.put(None)
    await sql_gen_task
    await sql_queue.put(None)
    await executor_task
    
    try:
        final_sql = await result_selection_async(
            db_path, db_schema, question, generated_sqls,
            llm_call_config["base_url"], current_api_key, llm_call_config["model_name"],
            execution_results=execution_results, stats=stats
        )
    except Exception:
        final_sql = "SELECT 'Error'"

    metrics["rs_end"] = time.time()
    
    end_total = time.time()
    
    lwss_duration = metrics.get("lwss_end", 0) - metrics.get("lwss_start", 0)
    if "lwss_time" in stats:
        lwss_duration = stats["lwss_time"]
    
    sqlgen_start = metrics.get("sqlgen_start", metrics.get("sqlgen_end", 0))
    sqlgen_end = metrics.get("sqlgen_end", 0)
    sqlgen_duration = sqlgen_end - sqlgen_start
    
    rs_start = metrics.get("rs_start", metrics.get("rs_end", 0))
    rs_end = metrics.get("rs_end", 0)
    rs_duration = rs_end - rs_start
    
    global_results.append({
        "db_id": db_id,
        "question": question,
        "final_sql": final_sql,
        "timings": {
            "lwss": lwss_duration,
            "sqlgen": sqlgen_duration,
            "result_selection": rs_duration,
            "total": end_total - start_total
        },
        "stats": dict(stats)
    })

async def main():
    with open('./config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    paths = config["paths"]
    
    with open(paths["dev_path"]) as f:
        dev_data = json.load(f)
        
    available_dbs = os.listdir(paths["databases_path"])
    valid_data = [d for d in dev_data if d["db_id"] in available_dbs]
    
    exec_config = config.get("execution_config", {})
    max_examples = exec_config.get("max_examples", 20)
    concurrency_limit = exec_config.get("concurrency_limit", 20)
    
    if max_examples == -1:
        selected_data = valid_data
        max_examples = len(selected_data)
    elif len(valid_data) < max_examples:
        selected_data = valid_data
    else:
        selected_data = random.sample(valid_data, max_examples)
        
    print(f"Selected {len(selected_data)} examples for processing. Concurrency Limit: {concurrency_limit}")
    
    global_results = []
    
    semaphore = asyncio.Semaphore(concurrency_limit)
    
    async def process_item_limited(data):
        async with semaphore:
            await process_item(data, paths, config, global_results)

    tasks = [process_item_limited(data) for data in selected_data]
    
    batch_start_time = time.time()
    
    for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing", unit="task"):
        await f
        
    batch_end_time = time.time()
    
    avg_timings = defaultdict(float)
    total_tokens = defaultdict(int)
    count = len(global_results)
    
    if count == 0:
        print("No results.")
        return

    for res in global_results:
        for k, v in res["timings"].items():
            avg_timings[k] += v
        for k, v in res["stats"].items():
            total_tokens[k] += v
            
    for k in avg_timings:
        avg_timings[k] /= count
    
    avg_tokens = {k: v / count for k, v in total_tokens.items()}
        
    total_batch_time = batch_end_time - batch_start_time
    throughput_per_task = total_batch_time / count if count > 0 else 0

    print(f"Total Batch Duration:   {total_batch_time:.2f} s")
    print(f"System Throughput:      {throughput_per_task:.2f} s/task (Amortized)")
    
    output_file = paths.get("output_path", "./outputs/final_results.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    formatted_results = []
    for res in global_results:
        formatted_results.append({
            "db_id": res["db_id"],
            "question": res["question"],
            "pre_sql": res["final_sql"]
        })

    with open(output_file, 'w') as f:
        json.dump(formatted_results, f, indent=4)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
