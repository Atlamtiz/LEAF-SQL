prompt_base_phase = """The SQL skeleton represents the logical structure of a SQL query. Please determine if the following SQL skeleton is correct.

**DB Schema:**
{db_schema}

**Question:**
{question}

**SQL Skeleton:**
{skeleton}

**Instructions:**
1.  Analyze the intent of the **Question**.
2.  Analyze the semantics of the **SQL Skeleton**.
3.  Determine if the skeleton's semantics contradict the question's intent.

**Note:**
This is a **Base-level** skeleton. It omits table join conditions, specific details of placeholders (like quantity, column names, or operators), and potentially deep nesting. As long as the skeleton does not have a clear semantic conflict with the question, it should be considered correct.

Finally, provide your answer in the format: ```True``` or ```False```."""

prompt_expanded_phase = """The SQL skeleton represents the logical structure of a SQL query. Please determine if the following SQL skeleton is correct.

**DB Schema:**
{db_schema}

**Question:**
{question}

**SQL Skeleton:**
{skeleton}

**Instructions:**
1.  Analyze the intent of the **Question**.
2.  Analyze the semantics of the **SQL Skeleton**.
3.  Determine if the skeleton's semantics contradict the question's intent.

**Note:**
This skeleton omits table join conditions and specific details of placeholders (like quantity, column names, or operators). 

Finally, provide your answer in the format: ```True``` or ```False```."""

prompt_detailed_phase_placeholder = """The SQL skeleton represents the logical structure of a SQL query. Please determine if the following SQL skeleton is correct.

**DB Schema:**
{db_schema}

**Question:**
{question}

**SQL Skeleton:**
{skeleton}

**Instructions:**
1.  Analyze the intent of the **Question**.
2.  Analyze the semantics of the **SQL Skeleton**.
3.  Determine if the skeleton's semantics contradict the question's intent.

**Note:**
This is a **Detail-level skeleton with specific placeholders**. It omits table join conditions. As long as the skeleton does not have a clear semantic conflict with the question, it should be considered correct.

Finally, provide your answer in the format: ```True``` or ```False```."""

prompt_detailed_phase_join = """The SQL skeleton represents the logical structure of a SQL query. Please determine if the following SQL skeleton is correct.

**DB Schema:**
{db_schema}

**Question:**
{question}

**SQL Skeleton:**
{skeleton}

**Instructions:**
1.  Analyze the intent of the **Question**.
2.  Analyze the semantics of the **SQL Skeleton**.
3.  Determine if the skeleton's semantics contradict the question's intent.

**Note:**
This is a **Detail-level skeleton** that represents the most complete query logic, including join conditions. Please perform a thorough check for any semantic conflicts with the question.

Finally, provide your answer in the format: ```True``` or ```False```."""

from openai import OpenAI, AsyncOpenAI
import re
import asyncio


def model(base_url, api_key, model_name, prompt):
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
        chat_completion = client.chat.completions.create(
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
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred in the 'model' function: {e}")
        return "" 


async def model_async(base_url, api_key, model_name, prompt):
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
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred in the 'model_async' function: {e}")
        return "" 


def extract_answer_from_response(response_text):
    pattern = r'```(True|False)```'
    
    match = re.search(pattern, response_text)
    
    if match:
        return match.group(1) 
    else:
        return None


def skeeva_agent(db_schema, question, skeleton, phase, base_url, api_key, model_name):
    if phase.lower() == "base":
        prompt = prompt_base_phase.format(db_schema=db_schema, question=question, skeleton=skeleton)

    elif phase.lower() == "expanded":
        prompt = prompt_expanded_phase.format(db_schema=db_schema, question=question, skeleton=skeleton)

    elif phase.lower() == "detailed_placeholder":
        prompt = prompt_detailed_phase_placeholder.format(db_schema=db_schema, question=question, skeleton=skeleton)

    elif phase.lower() == "detailed_join": 
        prompt = prompt_detailed_phase_join.format(db_schema=db_schema, question=question, skeleton=skeleton)
    else:
        print(f"Unknown phase: {phase}")
        return []
    
    model_output = model(base_url, api_key, model_name, prompt)

    everes = extract_answer_from_response(model_output)

    return everes


async def skeeva_agent_async(db_schema, question, skeleton, phase, base_url, api_key, model_name):
    if phase.lower() == "base":
        prompt = prompt_base_phase.format(db_schema=db_schema, question=question, skeleton=skeleton)

    elif phase.lower() == "expanded":
        prompt = prompt_expanded_phase.format(db_schema=db_schema, question=question, skeleton=skeleton)

    elif phase.lower() == "detailed_placeholder":
        prompt = prompt_detailed_phase_placeholder.format(db_schema=db_schema, question=question, skeleton=skeleton)

    elif phase.lower() == "detailed_join": 
        prompt = prompt_detailed_phase_join.format(db_schema=db_schema, question=question, skeleton=skeleton)
    else:
        print(f"Unknown phase: {phase}")
        return None
    
    model_output = await model_async(base_url, api_key, model_name, prompt)

    everes = extract_answer_from_response(model_output)

    return everes