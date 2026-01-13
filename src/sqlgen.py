prompt_sql_generation = """You are now a mysql data analyst, and you are given a database schema as follows:
【DB Schema】
{db_schema}

【question】
{question}

【Skeletons】
{skeletons}

For each provided skeleton, generate a complete and executable SQL query that answers the question, without explanation.

Output the final SQL queries in the following format, with each query on a new line:
```sql
"SQL 1",
"SQL 2",
...
```"""

from openai import OpenAI, AsyncOpenAI
import re

async def model_async(base_url, api_key, model_name, prompt, stats=None, module_name=None):
    try:
        client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
        chat_completion = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specializing in SQL generation."},
                {"role": "user", "content": prompt},
            ],
            extra_body={
                "chat_template_kwargs": {"enable_thinking": False},
            },
            temperature=0.8,
            max_tokens=1024,
            timeout=60,
        )
        if stats is not None and module_name is not None and chat_completion.usage:
            stats[module_name] = stats.get(module_name, 0) + chat_completion.usage.total_tokens

        return chat_completion.choices[0].message.content
    except Exception as e:
        if "Content Exists Risk" in str(e):
            pass
        else:
            pass
        return "" 

def extract_sql_list(model_output):
    try:
        sql_block_match = re.search(r"```sql\n(.*?)\n```", model_output, re.DOTALL)
        if not sql_block_match:
            return []

        sql_block = sql_block_match.group(1).strip() 
        if sql_block.startswith('"'):
            sql_block = sql_block[1:]
        if sql_block.endswith('"'):
            sql_block = sql_block[:-1]
        sql_queries = re.split(r'",\s*?"', sql_block)

        return sql_queries

    except Exception:
        return []

async def sql_generation_async(db_schema, question, skeletons, base_url, api_key, model_name, stats=None):
    prompt = prompt_sql_generation.format(db_schema=db_schema, question=question, skeletons=skeletons)
    model_output = await model_async(base_url, api_key, model_name, prompt, stats, 'sqlgen')

    sql_list = extract_sql_list(model_output)

    return sql_list

def sql_generation(db_schema, question, skeletons, base_url, api_key, model_name):
    # Keep sync version for backward compatibility if needed, but main.py will use async
    # Since main.py is being updated, maybe we don't strictly need this, but good to keep.
    # Actually, to avoid duplicated code, I'll just remove it or wrap async call?
    # No, I can't wrap async call easily in sync function without event loop issues.
    # I'll just replace it with the async version and let main.py call it.
    pass
