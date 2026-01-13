prompt_result_selection = """You are an expert SQL analyst. Your task is to act as the judge to select the single most accurate SQL query that correctly answers the user's question.

Analyze the provided database schema, the user's question, and the competing candidates below. Each candidate includes a SQL query and its execution result.

【Database Schema】
{db_schema}

【Question】
{question}

======================================================================
{candidates_info}
======================================================================

**Instructions:**
1. Carefully analyze each candidate's SQL logic and execution result
2. Compare how well each result answers the user's question
3. Consider correctness, completeness, and accuracy of the results
4. Think step-by-step about which candidate best satisfies the question requirements

**Output Requirements:**
- First, briefly explain your reasoning (2-3 sentences max)
- Then output ONLY the selected SQL query
- The SQL should not contain any comments or explanations
- Use the exact format below:

**Reasoning:**
[Your brief analysis here]

**Selected SQL:**
```sql
"The complete SQL query"
```"""

import random
import re
from collections import defaultdict
from openai import OpenAI, AsyncOpenAI
import sqlite3
import time
import asyncio

def execute_sql(db_path, sql):    
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = lambda b: b.decode(errors='ignore')
        
        # Prevent long-running queries
        start_time = time.time()
        def progress_handler():
            if time.time() - start_time > 15:
                return 1
            return 0
        conn.set_progress_handler(progress_handler, 10000)
        
        cursor = conn.cursor()
        
        cursor.execute(sql)
        
        if time.time() - start_time > 15:
            return "execute timeout"
            
        result = cursor.fetchall()
        
        if not result:
            return "execute null"
        
        return str(result) 
    except sqlite3.Error as e:

        return "execute error"
    finally:
        if 'conn' in locals():
            conn.close()

async def execute_sql_async(db_path, sql):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, execute_sql, db_path, sql)

async def model_async(base_url, api_key, model_name, prompt, stats=None, module_name=None):
    try:
        client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
        chat_completion = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specializing in SQL skeleton generation."},
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

def extra_sql(model_output):
    match = re.search(r"```sql\n(.*?)\n```", model_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

async def result_selection_async(db_path, db_schema, question, candidate_sqls, base_url, api_key, model_name, execution_results=None, stats=None):
    if execution_results is None:
        tasks = [execute_sql_async(db_path, sql) for sql in candidate_sqls]
        results = await asyncio.gather(*tasks)
        execution_results = dict(zip(candidate_sqls, results))
    
    valid_groups = defaultdict(list)
    valid_results = {} 
    
    for sql, result in execution_results.items():
        if result not in ["execute error", "execute timeout", "execute null"]:
            valid_groups[result].append(sql)
            valid_results[sql] = result

    if not valid_groups:
        if not candidate_sqls:
            return "SELECT 'No valid SQL found'" # Handle empty case
        return random.choice(candidate_sqls)

    max_votes = 0
    for result in valid_groups:
        num_votes = len(valid_groups[result])
        if num_votes > max_votes:
            max_votes = num_votes
            
    winning_groups = [group for group in valid_groups.values() if len(group) == max_votes]

    if len(winning_groups) == 1:
        return random.choice(winning_groups[0])

    else:
        candidates_info_parts = []

        for group in winning_groups:
            representative_sql = group[0]
            result_str = valid_results[representative_sql]
            
            candidate_str = f"【SQL】:\n```sql\n{representative_sql}\n```\n【Result】:\n{result_str}"
            candidates_info_parts.append(candidate_str)
        
        candidates_info = "\n\n======================================================================\n\n".join(candidates_info_parts)
        
        prompt = prompt_result_selection.format(
            db_schema=db_schema, 
            question=question, 
            candidates_info=candidates_info
        )
        
        model_output = await model_async(base_url, api_key, model_name, prompt, stats, 'result_selection')
        
        final_sql = extra_sql(model_output)
        
        if not final_sql:
            all_winners = [sql for group in winning_groups for sql in group]
            return random.choice(all_winners)

        return final_sql


def result_selection(db_path, db_schema, question, candidate_sqls, base_url, api_key, model_name):
   # kept for compatibility if needed, but implementation removed to force async usage in main
   pass
