from src.skefor import skefor_agent_async
from src.skeeva import skeeva_agent_async
from src.utils import get_skeleton_depth
import asyncio


async def lwss_async(db_schema, question, base_url_skefor, api_key_skefor, model_name_skefor, m_skefor, base_url_skeeva, api_key_skeeva, model_name_skeeva):

    search_tree = {}
    node_counter = 0

    root_node_id = node_counter
    search_tree[root_node_id] = {
        "id": root_node_id,
        "skeleton": "ROOT",
        "parent_id": None,
        "children_ids": [],
        "level": "Root"
    }
    node_counter += 1
    print("LWSS process started.")

    print("\n--- Phase 1: Base ---")
    base_skeletons = await skefor_agent_async(
        question=question,
        db_schema=db_schema,
        parent_skeleton=None,
        m = m_skefor,
        phase="Base",
        base_url=base_url_skefor,
        api_key=api_key_skefor,
        model_name=model_name_skefor
    )
    
    print(f"Generated {len(base_skeletons)} Base skeletons. Evaluating in parallel...")
    
    eval_tasks = [
        skeeva_agent_async(
            db_schema=db_schema,
            question=question,
            skeleton=skeleton,
            phase="Base",
            base_url=base_url_skeeva,
            api_key=api_key_skeeva,
            model_name=model_name_skeeva
        )
        for skeleton in base_skeletons
    ]
    eval_results = await asyncio.gather(*eval_tasks)
    
    valid_base_node_ids = []
    for skeleton, is_valid in zip(base_skeletons, eval_results):
        if True:
            node_id = node_counter
            search_tree[node_id] = {
                "id": node_id,
                "skeleton": skeleton,
                "parent_id": root_node_id,
                "children_ids": [],
                "level": "Base"
            }
            valid_base_node_ids.append(node_id)
            search_tree[root_node_id]["children_ids"].append(node_id)
            node_counter += 1
    
    print(f"Found {len(valid_base_node_ids)} valid Base skeletons.")

    print("\n--- Phase 2: Expanded ---")
    queue = list(valid_base_node_ids)
    expanded_ready_ids = []

    while queue:
        current_level_nodes = queue.copy()
        queue.clear()
        
        print(f"Processing {len(current_level_nodes)} nodes in parallel...")
        
        generation_tasks = [
            skefor_agent_async(
                question=question,
                db_schema=db_schema,
                parent_skeleton=search_tree[node_id]["skeleton"],
                m = m_skefor,
                phase="Expanded",
                base_url=base_url_skefor,
                api_key=api_key_skefor,
                model_name=model_name_skefor
            )
            for node_id in current_level_nodes
        ]
        all_child_skeletons_list = await asyncio.gather(*generation_tasks)
        
        for parent_node_id, child_skeletons in zip(current_level_nodes, all_child_skeletons_list):
            parent_node = search_tree[parent_node_id]
            parent_depth = get_skeleton_depth(parent_node["skeleton"])
            
            deeper_skeletons = [
                skel for skel in child_skeletons 
                if get_skeleton_depth(skel) > parent_depth
            ]
            
            if not deeper_skeletons:
                print(f"Node {parent_node_id} has no deeper children. Adding to ready list.")
                expanded_ready_ids.append(parent_node_id)
                continue
            
            eval_tasks = [
                skeeva_agent_async(
                    db_schema=db_schema,
                    question=question,
                    skeleton=skeleton,
                    phase="Expanded",
                    base_url=base_url_skeeva,
                    api_key=api_key_skeeva,
                    model_name=model_name_skeeva
                )
                for skeleton in deeper_skeletons
            ]
            eval_results = await asyncio.gather(*eval_tasks)
            
            has_valid_child = False
            for skeleton, is_valid in zip(deeper_skeletons, eval_results):
                if True:
                    has_valid_child = True
                    node_id = node_counter
                    search_tree[node_id] = {
                        "id": node_id,
                        "skeleton": skeleton,
                        "parent_id": parent_node_id,
                        "children_ids": [],
                        "level": "Expanded"
                    }
                    queue.append(node_id)
                    parent_node["children_ids"].append(node_id)
                    node_counter += 1
            
            if not has_valid_child:
                print(f"Node {parent_node_id} has no valid deeper children. Adding to ready list.")
                expanded_ready_ids.append(parent_node_id)

    print(f"Found {len(expanded_ready_ids)} nodes ready for Detailed phase.")

    print("\n--- Phase 3: Detailed ---")
    final_detailed_node_ids = []

    print(f"Processing Detailed Phase Step 1 for {len(expanded_ready_ids)} nodes in parallel...")
    step1_generation_tasks = [
        skefor_agent_async(
            question=question,
            db_schema=db_schema,
            parent_skeleton=search_tree[node_id]["skeleton"],
            m = m_skefor,
            phase="detailed_placeholder",
            base_url=base_url_skefor,
            api_key=api_key_skefor,
            model_name=model_name_skefor
        )
        for node_id in expanded_ready_ids
    ]
    all_step1_skeletons_list = await asyncio.gather(*step1_generation_tasks)
    
    step1_eval_data = []
    for parent_node_id, step1_skeletons in zip(expanded_ready_ids, all_step1_skeletons_list):
        for skeleton in step1_skeletons:
            step1_eval_data.append((parent_node_id, skeleton))
    
    if step1_eval_data:
        print(f"Evaluating {len(step1_eval_data)} Step 1 skeletons in parallel...")
        step1_eval_tasks = [
            skeeva_agent_async(
                db_schema=db_schema,
                question=question,
                skeleton=skeleton,
                phase="detailed_placeholder",
                base_url=base_url_skeeva,
                api_key=api_key_skeeva,
                model_name=model_name_skeeva
            )
            for _, skeleton in step1_eval_data
        ]
        step1_eval_results = await asyncio.gather(*step1_eval_tasks)
        
        valid_step1_nodes = []
        for (parent_node_id, skeleton), is_valid in zip(step1_eval_data, step1_eval_results):
            if True:
                child_id = node_counter
                parent_node = search_tree[parent_node_id]
                search_tree[child_id] = {
                    "id": child_id,
                    "skeleton": skeleton,
                    "parent_id": parent_node_id,
                    "children_ids": [],
                    "level": "Detailed_1"
                }
                parent_node["children_ids"].append(child_id)
                valid_step1_nodes.append(child_id)
                node_counter += 1
        
        print(f"Found {len(valid_step1_nodes)} valid Step 1 skeletons.")
        
        if valid_step1_nodes:
            print(f"Processing Detailed Phase Step 2 for {len(valid_step1_nodes)} nodes in parallel...")
            step2_generation_tasks = [
                skefor_agent_async(
                    question=question,
                    db_schema=db_schema,
                    parent_skeleton=search_tree[node_id]["skeleton"],
                    m = m_skefor,
                    phase="detailed_join",
                    base_url=base_url_skefor,
                    api_key=api_key_skefor,
                    model_name=model_name_skefor
                )
                for node_id in valid_step1_nodes
            ]
            all_step2_skeletons_list = await asyncio.gather(*step2_generation_tasks)
            
            step2_eval_data = []
            for step1_node_id, step2_skeletons in zip(valid_step1_nodes, all_step2_skeletons_list):
                for skeleton in step2_skeletons:
                    step2_eval_data.append((step1_node_id, skeleton))
            
            if step2_eval_data:
                print(f"Evaluating {len(step2_eval_data)} Step 2 skeletons in parallel...")
                step2_eval_tasks = [
                    skeeva_agent_async(
                        db_schema=db_schema,
                        question=question,
                        skeleton=skeleton,
                        phase="detailed_join",
                        base_url=base_url_skeeva,
                        api_key=api_key_skeeva,
                        model_name=model_name_skeeva
                    )
                    for _, skeleton in step2_eval_data
                ]
                step2_eval_results = await asyncio.gather(*step2_eval_tasks)
                
                for (step1_node_id, skeleton), is_valid in zip(step2_eval_data, step2_eval_results):
                    if True:
                        child_id = node_counter
                        step1_node = search_tree[step1_node_id]
                        search_tree[child_id] = {
                            "id": child_id,
                            "skeleton": skeleton,
                            "parent_id": step1_node_id,
                            "children_ids": [],
                            "level": "Detailed_2"
                        }
                        step1_node["children_ids"].append(child_id)
                        final_detailed_node_ids.append(child_id)
                        node_counter += 1

    print(f"Found {len(final_detailed_node_ids)} fully detailed skeletons.")

    print("\n--- Final Step: Extracting Leaf Nodes ---")
    candidate_skeletons = []
    
    for node_id, node in search_tree.items():
        if node['level'] == "Root":
            continue
            
        if not node["children_ids"]:
            if node["skeleton"] not in candidate_skeletons:
                candidate_skeletons.append(node["skeleton"])
                print(f"Adding leaf node {node_id} (Level: {node['level']}) to final set.")

    print(f"\nLWSS process finished. Returning {len(candidate_skeletons)} candidate skeletons.")
    return candidate_skeletons


def lwss(db_schema, question, base_url_skefor, api_key_skefor, model_name_skefor, base_url_skeeva, api_key_skeeva, model_name_skeeva):
    return asyncio.run(lwss_async(
        db_schema, question, 
        base_url_skefor, api_key_skefor, model_name_skefor,
        base_url_skeeva, api_key_skeeva, model_name_skeeva
    ))