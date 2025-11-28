from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import date
from .scoring import calculate_task_score, get_task_priority_level, explain_score
from .sorting_strategies import apply_sorting_strategy, get_available_strategies

@csrf_exempt
@require_http_methods(["POST"])
def analyze_tasks(request):
    """
    Endpoint: /analyze/
    Accepts a POST request containing a list of tasks.
    Returns the sorted list by priority score.
    """
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
        # Handle both single task and list of tasks
        if isinstance(data, dict):
            tasks = [data]
        elif isinstance(data, list):
            tasks = data
        else:
            return JsonResponse({'error': 'Invalid data format. Expected task object or array of tasks.'}, status=400)
        
        # Calculate scores and sort tasks
        scored_tasks = []
        for i, task in enumerate(tasks):
            # Add an ID if not present
            if 'id' not in task:
                task['id'] = i + 1
            
            # Calculate priority score
            score = calculate_task_score(task)
            priority_level = get_task_priority_level(score)
            explanation = explain_score(task, score)
            
            # Add scoring information to task
            task_with_score = {
                **task,
                'priority_score': score,
                'priority_level': priority_level,
                'explanation': explanation
            }
            scored_tasks.append(task_with_score)
        
        # Get sorting strategy from request (default: smart_balance)
        strategy = request.GET.get('strategy', 'smart_balance')
        
        # Apply the selected sorting strategy
        sorted_tasks = apply_sorting_strategy(scored_tasks, strategy)
        
        return JsonResponse({
            'status': 'success',
            'total_tasks': len(sorted_tasks),
            'tasks': sorted_tasks
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def suggest_tasks(request):
    """
    Endpoint: /suggest/
    Returns the top 3 tasks for "today" with text explanations.
    """
    try:
        if request.method == "POST":
            # Parse tasks from POST request body
            data = json.loads(request.body)
            if isinstance(data, dict):
                tasks = [data]
            elif isinstance(data, list):
                tasks = data
            else:
                return JsonResponse({'error': 'Invalid data format'}, status=400)
        else:
            # For GET request, return example tasks with suggestions
            example_tasks = [
                {
                    'id': 1,
                    'title': 'Fix login bug',
                    'due_date': '2024-11-30',
                    'importance': 8,
                    'estimated_hours': 3,
                    'dependencies': []
                },
                {
                    'id': 2,
                    'title': 'Update documentation',
                    'due_date': '2024-12-05',
                    'importance': 6,
                    'estimated_hours': 1,
                    'dependencies': []
                },
                {
                    'id': 3,
                    'title': 'Review pull requests',
                    'due_date': '2024-11-29',
                    'importance': 7,
                    'estimated_hours': 2,
                    'dependencies': []
                }
            ]
            tasks = example_tasks
        
        # Calculate scores for all tasks
        scored_tasks = []
        for i, task in enumerate(tasks):
            if 'id' not in task:
                task['id'] = i + 1
            
            score = calculate_task_score(task)
            priority_level = get_task_priority_level(score)
            explanation = explain_score(task, score)
            
            task_with_score = {
                **task,
                'priority_score': score,
                'priority_level': priority_level,
                'explanation': explanation
            }
            scored_tasks.append(task_with_score)
        
        # Sort and get top 3
        sorted_tasks = sorted(scored_tasks, key=lambda x: x['priority_score'], reverse=True)
        top_3_tasks = sorted_tasks[:3]
        
        # Generate recommendations
        recommendations = []
        for i, task in enumerate(top_3_tasks, 1):
            recommendation = {
                'rank': i,
                'task': task,
                'reason': f"Rank #{i}: {task['explanation']}"
            }
            recommendations.append(recommendation)
        
        # Generate summary message
        if top_3_tasks:
            summary = f"Today's Focus: Start with '{top_3_tasks[0]['title']}' ({top_3_tasks[0]['priority_level']} priority)"
            if len(top_3_tasks) > 1:
                summary += f", then '{top_3_tasks[1]['title']}'"
        else:
            summary = "No tasks to prioritize today."
        
        return JsonResponse({
            'status': 'success',
            'summary': summary,
            'top_tasks': recommendations,
            'total_analyzed': len(tasks)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def get_strategies(request):
    """
    Endpoint: /strategies/
    Returns available sorting strategies.
    """
    return JsonResponse({
        'status': 'success',
        'strategies': get_available_strategies()
    })
