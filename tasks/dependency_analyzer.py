"""
Dependency analysis utilities for detecting circular dependencies
and managing task relationships.
"""


def detect_circular_dependencies(tasks):
    """
    Detect circular dependencies in a list of tasks.
    
    Args:
        tasks: List of task dictionaries with 'id' and 'dependencies' fields
        
    Returns:
        dict: {
            'has_circular': bool,
            'circular_chains': list of circular dependency chains,
            'warnings': list of warning messages
        }
    """
    # Build adjacency list for dependency graph
    graph = {}
    task_map = {}
    
    for task in tasks:
        task_id = task.get('id')
        if task_id:
            graph[task_id] = task.get('dependencies', [])
            task_map[task_id] = task
    
    # Find circular dependencies using DFS
    visited = set()
    rec_stack = set()
    circular_chains = []
    
    def dfs(node, path):
        if node not in graph:
            return False
            
        if node in rec_stack:
            # Found a cycle - extract the circular part
            cycle_start = path.index(node)
            circular_chain = path[cycle_start:] + [node]
            circular_chains.append(circular_chain)
            return True
            
        if node in visited:
            return False
            
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        # Check all dependencies
        for dependency in graph[node]:
            if dfs(dependency, path):
                # Don't return immediately - find all cycles
                pass
                
        rec_stack.remove(node)
        path.pop()
        return False
    
    # Check all nodes for cycles
    for task_id in graph:
        if task_id not in visited:
            dfs(task_id, [])
    
    # Generate warnings
    warnings = []
    if circular_chains:
        for chain in circular_chains:
            task_names = []
            for task_id in chain[:-1]:  # Exclude duplicate at end
                if task_id in task_map:
                    task_names.append(task_map[task_id].get('title', f'Task {task_id}'))
                else:
                    task_names.append(f'Task {task_id}')
            
            warnings.append(f"Circular dependency detected: {' → '.join(task_names)} → {task_names[0]}")
    
    return {
        'has_circular': len(circular_chains) > 0,
        'circular_chains': circular_chains,
        'warnings': warnings
    }


def get_dependency_order(tasks):
    """
    Get a valid execution order for tasks considering dependencies.
    Uses topological sort, handling circular dependencies gracefully.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        dict: {
            'ordered_tasks': list of tasks in dependency order,
            'circular_dependencies': circular dependency info,
            'warnings': list of warnings
        }
    """
    # First check for circular dependencies
    circular_info = detect_circular_dependencies(tasks)
    
    # Build graph
    graph = {}
    in_degree = {}
    task_map = {}
    
    for task in tasks:
        task_id = task.get('id')
        if task_id:
            graph[task_id] = task.get('dependencies', [])
            in_degree[task_id] = 0
            task_map[task_id] = task
    
    # Calculate in-degrees (how many tasks depend on each task)
    for task_id in graph:
        for dependency in graph[task_id]:
            if dependency in in_degree:
                in_degree[task_id] += 1  # The task that has dependencies gets higher in-degree
    
    # Topological sort using Kahn's algorithm
    queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
    ordered_task_ids = []
    
    while queue:
        current = queue.pop(0)
        ordered_task_ids.append(current)
        
        # Process tasks that depend on the current task
        for task_id in graph:
            if current in graph[task_id]:
                in_degree[task_id] -= 1
                if in_degree[task_id] == 0:
                    queue.append(task_id)
    
    # Convert back to task objects
    ordered_tasks = []
    for task_id in ordered_task_ids:
        if task_id in task_map:
            ordered_tasks.append(task_map[task_id])
    
    # Add any remaining tasks (those in circular dependencies)
    remaining_task_ids = set(task_map.keys()) - set(ordered_task_ids)
    for task_id in remaining_task_ids:
        ordered_tasks.append(task_map[task_id])
    
    warnings = circular_info['warnings'].copy()
    if remaining_task_ids:
        warnings.append(f"Tasks with circular dependencies added at end: {list(remaining_task_ids)}")
    
    return {
        'ordered_tasks': ordered_tasks,
        'circular_dependencies': circular_info,
        'warnings': warnings
    }


def analyze_task_dependencies(tasks):
    """
    Comprehensive dependency analysis for a list of tasks.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        dict: Complete dependency analysis including circular detection,
              ordering, and recommendations
    """
    circular_info = detect_circular_dependencies(tasks)
    dependency_order = get_dependency_order(tasks)
    
    # Calculate dependency statistics
    total_tasks = len(tasks)
    tasks_with_deps = sum(1 for task in tasks if task.get('dependencies'))
    max_deps = max((len(task.get('dependencies', [])) for task in tasks), default=0)
    
    # Find tasks that are blocking others
    blocking_tasks = {}
    for task in tasks:
        task_id = task.get('id')
        if task_id:
            blocking_tasks[task_id] = []
    
    for task in tasks:
        for dep_id in task.get('dependencies', []):
            if dep_id in blocking_tasks:
                blocking_tasks[dep_id].append(task.get('id'))
    
    most_blocking = max(blocking_tasks.items(), key=lambda x: len(x[1]), default=(None, []))
    
    return {
        'circular_dependencies': circular_info,
        'dependency_order': dependency_order,
        'statistics': {
            'total_tasks': total_tasks,
            'tasks_with_dependencies': tasks_with_deps,
            'max_dependencies_per_task': max_deps,
            'most_blocking_task': most_blocking[0] if most_blocking[1] else None,
            'most_blocking_count': len(most_blocking[1]) if most_blocking else 0
        },
        'recommendations': _generate_dependency_recommendations(tasks, circular_info, blocking_tasks)
    }


def _generate_dependency_recommendations(tasks, circular_info, blocking_tasks):
    """Generate recommendations based on dependency analysis."""
    recommendations = []
    
    if circular_info['has_circular']:
        recommendations.append({
            'type': 'warning',
            'message': 'Circular dependencies detected. Consider breaking these cycles.',
            'action': 'Review task dependencies and remove circular references.'
        })
    
    # Find highly blocking tasks
    high_blocking = [(task_id, blocked) for task_id, blocked in blocking_tasks.items() if len(blocked) >= 3]
    if high_blocking:
        task_id, blocked_count = high_blocking[0]
        recommendations.append({
            'type': 'priority',
            'message': f'Task {task_id} is blocking {len(blocked_count)} other tasks.',
            'action': 'Prioritize this task to unblock others.'
        })
    
    # Find tasks with no dependencies (can start immediately)
    no_deps = [task for task in tasks if not task.get('dependencies')]
    if no_deps:
        recommendations.append({
            'type': 'opportunity',
            'message': f'{len(no_deps)} tasks have no dependencies and can start immediately.',
            'action': 'Consider these for quick wins or parallel execution.'
        })
    
    return recommendations
