from src.skefor import skefor_agent_async
from src.skeeva import skeeva_agent_async
from src.utils import get_skeleton_depth
import asyncio


async def lwss_async(db_schema, question, base_url_skefor, api_key_skefor, model_name_skefor, m_skefor, base_url_skeeva, api_key_skeeva, model_name_skeeva, output_queue=None, stats=None):

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
    
    lwss_start_time = asyncio.get_running_loop().time()

    base_skeletons = await skefor_agent_async(
        question=question,
        db_schema=db_schema,
        parent_skeleton=None,
        m = m_skefor,
        phase="Base",
        base_url=base_url_skefor,
        api_key=api_key_skefor,
        model_name=model_name_skefor,
        stats=stats
    )
    
    eval_tasks = [
        skeeva_agent_async(
            db_schema=db_schema,
            question=question,
            skeleton=skeleton,
            phase="Base",
            base_url=base_url_skeeva,
            api_key=api_key_skeeva,
            model_name=model_name_skeeva,
            stats=stats
        )
        for skeleton in base_skeletons
    ]
    eval_results = await asyncio.gather(*eval_tasks)
    
    valid_base_node_ids = []
    for skeleton, is_valid in zip(base_skeletons, eval_results):
        if is_valid == "True":
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
    
    queue = list(valid_base_node_ids)
    expanded_ready_ids = []

    while queue:
        current_level_nodes = queue.copy()
        queue.clear()
        
        generation_tasks = [
            skefor_agent_async(
                question=question,
                db_schema=db_schema,
                parent_skeleton=search_tree[node_id]["skeleton"],
                m = m_skefor,
                phase="Expanded",
                base_url=base_url_skefor,
                api_key=api_key_skefor,
                model_name=model_name_skefor,
                stats=stats
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
                    model_name=model_name_skeeva,
                    stats=stats
                )
                for skeleton in deeper_skeletons
            ]
            eval_results = await asyncio.gather(*eval_tasks)
            
            has_valid_child = False
            for skeleton, is_valid in zip(deeper_skeletons, eval_results):
                if is_valid == "True":
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
                expanded_ready_ids.append(parent_node_id)

    final_detailed_node_ids = []

    step1_generation_tasks = [
        skefor_agent_async(
            question=question,
            db_schema=db_schema,
            parent_skeleton=search_tree[node_id]["skeleton"],
            m = m_skefor,
            phase="detailed_placeholder",
            base_url=base_url_skefor,
            api_key=api_key_skefor,
            model_name=model_name_skefor,
            stats=stats
        )
        for node_id in expanded_ready_ids
    ]
    all_step1_skeletons_list = await asyncio.gather(*step1_generation_tasks)
    
    step1_eval_data = []
    for parent_node_id, step1_skeletons in zip(expanded_ready_ids, all_step1_skeletons_list):
        for skeleton in step1_skeletons:
            step1_eval_data.append((parent_node_id, skeleton))
    
    if step1_eval_data:
        step1_eval_tasks = [
            skeeva_agent_async(
                db_schema=db_schema,
                question=question,
                skeleton=skeleton,
                phase="detailed_placeholder",
                base_url=base_url_skeeva,
                api_key=api_key_skeeva,
                model_name=model_name_skeeva,
                stats=stats
            )
            for _, skeleton in step1_eval_data
        ]
        step1_eval_results = await asyncio.gather(*step1_eval_tasks)
        
        valid_step1_nodes = []
        for (parent_node_id, skeleton), is_valid in zip(step1_eval_data, step1_eval_results):
            if is_valid == "True":
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
        
        if valid_step1_nodes:
            step2_generation_tasks = [
                skefor_agent_async(
                    question=question,
                    db_schema=db_schema,
                    parent_skeleton=search_tree[node_id]["skeleton"],
                    m = m_skefor,
                    phase="detailed_join",
                    base_url=base_url_skefor,
                    api_key=api_key_skefor,
                    model_name=model_name_skefor,
                    stats=stats
                )
                for node_id in valid_step1_nodes
            ]
            all_step2_skeletons_list = await asyncio.gather(*step2_generation_tasks)
            
            step2_eval_data = []
            for step1_node_id, step2_skeletons in zip(valid_step1_nodes, all_step2_skeletons_list):
                for skeleton in step2_skeletons:
                    step2_eval_data.append((step1_node_id, skeleton))
            
            if step2_eval_data:
                step2_eval_tasks = [
                    skeeva_agent_async(
                        db_schema=db_schema,
                        question=question,
                        skeleton=skeleton,
                        phase="detailed_join",
                        base_url=base_url_skeeva,
                        api_key=api_key_skeeva,
                        model_name=model_name_skeeva,
                        stats=stats
                    )
                    for _, skeleton in step2_eval_data
                ]
                step2_eval_results = await asyncio.gather(*step2_eval_tasks)
                
                pushed_skeletons = set()

                for (step1_node_id, skeleton), is_valid in zip(step2_eval_data, step2_eval_results):
                    if is_valid == "True":
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
                        
                        if output_queue and skeleton not in pushed_skeletons:
                            await output_queue.put(skeleton)
                            pushed_skeletons.add(skeleton)

    candidate_skeletons = []
    
    if 'pushed_skeletons' not in locals():
        pushed_skeletons = set()

    for node_id, node in search_tree.items():
        if node['level'] == "Root":
            continue
            
        if not node["children_ids"]:
            if node["skeleton"] not in candidate_skeletons:
                candidate_skeletons.append(node["skeleton"])
                
                if output_queue and node["skeleton"] not in pushed_skeletons:
                     await output_queue.put(node["skeleton"])
                     pushed_skeletons.add(node["skeleton"])

    if stats is not None:
        stats["lwss_time"] = asyncio.get_running_loop().time() - lwss_start_time
        
    return candidate_skeletons
