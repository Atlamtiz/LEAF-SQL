import json
import asyncio
import os
import yaml  
from src.lwss import lwss_async
from src.sqlgen import sql_generation
from src.get_db_schema import get_db_schema_w_fk
from src.result_selection import result_selection

async def main():
    with open('./config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    skefor_config = config["skefor_config"]
    skeeva_config = config["skeeva_config"]
    llm_call_config = config["llm_call_config"]
    paths = config["paths"]

    output_dir = os.path.dirname(paths["output_path"])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(paths["dev_path"]) as f:
        dev_data = json.load(f)

    try:
        with open(paths["output_path"], 'r') as f:
            output_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        output_data = []
    
    processed_map = {(item['db_id'], item['question']): item for item in output_data}

    for index, data in enumerate(dev_data):
        if (data["db_id"], data["question"]) in processed_map:
            print(f"Skipping already processed item {index}: {data['db_id']}")
            continue
        print("="*80)
        print(f"Processing item {index}.")
        print("-"*80)
        db_id = data["db_id"]
        db_path = f"{paths['databases_path']}/{db_id}/{db_id}.sqlite"
        db_schema = get_db_schema_w_fk(db_path, db_id, paths["tables_path"])
        question = data["question"]

        candidate_skeletons = await lwss_async(
            db_schema,
            question,
            skefor_config["base_url"],
            skefor_config["api_key"],
            skefor_config["model_name"],
            skefor_config["m"],
            skeeva_config["base_url"],
            skeeva_config['api_key'],
            skeeva_config['model_name']
        )
        print("-"*80)
        print("candidate_skeletons")
        print(json.dumps(candidate_skeletons, indent=2, ensure_ascii=False))
        print("-"*80)

        candidate_sqls = sql_generation(
            db_schema,
            question,
            candidate_skeletons,
            llm_call_config["base_url"],
            llm_call_config["api_key"],
            llm_call_config["model_name"]
        )
        print("-"*80)
        print("candidate_sqls")
        print(json.dumps(candidate_sqls, indent=2, ensure_ascii=False))
        print("-"*80)

        final_sql = result_selection(
            db_path,
            db_schema,
            question,
            candidate_sqls,
            llm_call_config["base_url"],
            llm_call_config["api_key"],
            llm_call_config["model_name"]
        )
        print("-"*80)
        print("final sql")
        print(final_sql)
        print("="*80)

        result_entry = {
            "db_id": db_id,
            "question": question,
            "pre_sql": final_sql
        }
        processed_map[(db_id, question)] = result_entry
        
        with open(paths["output_path"], 'w', encoding='utf-8') as f:
            json.dump(list(processed_map.values()), f, indent=4, ensure_ascii=False)
            
    print(f"Processing finished. Results saved to {paths['output_path']}")


if __name__ == "__main__":
    asyncio.run(main())