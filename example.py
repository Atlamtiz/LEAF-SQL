import json
import asyncio
import os

from src.lwss_example import lwss_async
from src.sqlgen import sql_generation
from src.get_db_schema import get_db_schema_w_fk
from src.result_selection import result_selection

async def run_example():
    skefor_config = {
        "base_url": "https://api.deepseek.com",
        "api_key": "sk-f519411c441d41f4bfe95a66054e720f",
        "model_name": "deepseek-chat",
        "m": "2"
    }

    skeeva_config = {
        "base_url": "https://api.deepseek.com",
        "api_key": "sk-20b7bcf8d0fd4667949b2ff3a3360b7c",
        "model_name": "deepseek-chat"
    }

    llm_call_config = {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "sk-9e7d3ade1dcc4200a0e515935a956e9c",
        "model_name": "deepseek-chat"
    }

    paths = {
        "dev_path": "./example/dev.json",
        "databases_path": "./example",
        "tables_path": "./example/dev_tables.json",
        "output_path": "./outputs/example_sql_output.json"
    }

    output_dir = os.path.dirname(paths["output_path"])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        with open(paths["dev_path"]) as f:
            dev_data = json.load(f)
            if not dev_data:
                print(f"Error: The example file '{paths['dev_path']}' is empty.")
                return
            example_data = dev_data[0] 
    except FileNotFoundError:
        print(f"Error: The example file '{paths['dev_path']}' was not found.")
        print("Please make sure the './example' directory and its contents are set up correctly.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{paths['dev_path']}'.")
        return

    print("=" * 80)
    print("Starting example processing...")
    print("=" * 80)

    db_id = example_data["db_id"]
    question = example_data["question"]
    db_path = f"{paths['databases_path']}/{db_id}/{db_id}.sqlite"
    
    print(f"Database ID: {db_id}")
    print(f"Question: {question}")
    
    if not os.path.exists(db_path):
        print(f"\nError: Database file not found at '{db_path}'")
        return

    db_schema = get_db_schema_w_fk(db_path, db_id, paths["tables_path"])
    print(f"\nSuccessfully loaded schema for database: {db_id}")

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
    print("-" * 80)
    print("Step 1: Candidate Skeletons (from lwss_async)")
    print(json.dumps(candidate_skeletons, indent=2, ensure_ascii=False))
    print("-" * 80)

    candidate_sqls = sql_generation(
        db_schema,
        question,
        candidate_skeletons,
        llm_call_config["base_url"],
        llm_call_config["api_key"],
        llm_call_config["model_name"]
    )
    print("Step 2: Candidate SQLs (from sql_generation)")
    print(json.dumps(candidate_sqls, indent=2, ensure_ascii=False))
    print("-" * 80)

    final_sql = result_selection(
        db_path,
        db_schema,
        question,
        candidate_sqls,
        llm_call_config["base_url"],
        llm_call_config["api_key"],
        llm_call_config["model_name"]
    )
    print("Step 3: Final Selected SQL (from result_selection)")
    print(final_sql)
    print("=" * 80)

    result_entry = {
        "db_id": db_id,
        "question": question,
        "final_sql": final_sql
    }
    
    with open(paths["output_path"], 'w', encoding='utf-8') as f:
        json.dump([result_entry], f, indent=4, ensure_ascii=False)
        
    print(f"\nProcessing finished. Example result saved to: {paths['output_path']}")


if __name__ == "__main__":
    asyncio.run(run_example())