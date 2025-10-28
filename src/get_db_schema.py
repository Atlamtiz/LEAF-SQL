import os
from .schema_engine import SchemaEngine
from sqlalchemy import create_engine
import json
import re

def get_db_schema(db_path, db_id):

    abs_path = db_path
    db_engine = create_engine(f'sqlite:///{abs_path}')

    schema_engine = SchemaEngine(engine=db_engine, db_name=db_id)
    mschema = schema_engine.mschema
    mschema_str = mschema.to_mschema()
    # print(mschema_str)

    return (mschema_str)

def get_foreign_keys(db_id, tables_path):
    with open(tables_path, 'r') as f:
        tables_data = json.load(f)

    db = next((item for item in tables_data if item["db_id"] == db_id), None)
    if not db:
        return []
    
    table_map = db["table_names_original"]
    columns = db["column_names_original"]
    
    seen = set()
    result = []
    
    for fk_pair in db["foreign_keys"]:
        from_col = columns[fk_pair[0]]
        to_col = columns[fk_pair[1]]
        
        from_table_idx, from_col_name = from_col[0], from_col[1]
        to_table_idx, to_col_name = to_col[0], to_col[1]
        
        from_table = table_map[from_table_idx]
        to_table = table_map[to_table_idx]
        
        pair1 = (from_table, from_col_name)
        pair2 = (to_table, to_col_name)
        sorted_pairs = sorted([pair1, pair2])
        
        relation = f"{sorted_pairs[0][0]}.{sorted_pairs[0][1]}={sorted_pairs[1][0]}.{sorted_pairs[1][1]}"
        
        if relation not in seen:
            seen.add(relation)
            result.append(relation)
    
    sorted(result)
    return (', '.join(result))


def get_db_schema_w_fk(db_path, db_id, tables_data):

    fk = get_foreign_keys(db_id, tables_data)

    abs_path = db_path
    db_engine = create_engine(f'sqlite:///{abs_path}')

    schema_engine = SchemaEngine(engine=db_engine, db_name=db_id)
    mschema = schema_engine.mschema
    mschema_str = mschema.to_mschema()
    mschema_str = mschema_str + "\n" + fk
    mschema_str = mschema_str.replace("# Table: main.", "# Table: ")
    # print(mschema_str)


    return (mschema_str)

def add_column_comments(schema_str, json_path):
    with open(json_path, 'r')as f:
        json_comments = json.load(f)

    comment_dict = {}
    for key, value in json_comments.items():
        parts = key.split('|')
        if len(parts) != 3:
            continue
        db, table, column = parts
        normalized_key = f"{db.lower()}|{table.lower()}|{column.lower()}"
        comment_dict[normalized_key] = value.strip()

    output = []
    lines = schema_str.split('\n')
    i = 0
    db_id = None
    current_table = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('【DB_ID】'):
            db_id = stripped.split(maxsplit=1)[1].strip()
            output.append(line)
            i += 1
            continue

        if stripped.startswith('# Table:'):
            table_full = stripped.split(': ')[1].strip()
            current_table = table_full.split('.')[-1]  # Extract table name
            output.append(line)
            i += 1
            
            while i < len(lines) and lines[i].strip() != '[':
                output.append(lines[i])
                i += 1
            
            output.append(lines[i])
            i += 1

            while i < len(lines) and lines[i].strip() != ']':
                original_line = lines[i]
                stripped_col = original_line.strip()
                
                col_match = re.match(r'^\((.*?)\s*[:,]', stripped_col)
                column_name = col_match.group(1).strip() if col_match else None
                
                output.append(original_line.rstrip())
                
                if db_id and current_table and column_name:
                    lookup_key = f"{db_id.lower()}|{current_table.lower()}|{column_name.lower()}"
                    comment = comment_dict.get(lookup_key, None)
                    if comment:
                        output.append(f'    #{comment}')
                
                i += 1

            output.append(lines[i])
            current_table = None
            i += 1
        else:
            output.append(line)
            i += 1

    return '\n'.join(output).replace('##', '#').replace("Table: main.", "Table: ")
