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

from openai import OpenAI
import re

def model(base_url, api_key, model_name, prompt):
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
        chat_completion = client.chat.completions.create(
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
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred in the 'model' function: {e}")
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

    except Exception as e:
        print(f"An error occurred in 'extract_sql_list': {e}")
        return []

def sql_generation(db_schema, question, skeletons, base_url, api_key, model_name):
    prompt = prompt_sql_generation.format(db_schema=db_schema, question=question, skeletons=skeletons)
    model_output = model(base_url, api_key, model_name, prompt)

    sql_list = extract_sql_list(model_output)

    return sql_list
