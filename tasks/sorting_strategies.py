"""
Multiple sorting strategies as required by the assignment.
Each strategy implements a different approach to task prioritization.
"""

from datetime import date
from .scoring import calculate_task_score


def sort_fastest_wins(tasks):
    """
    Fastest Wins: Prioritize low-effort tasks for quick completion.
    """
    def fastest_score(task):
        base_score = calculate_task_score(task)
        effort_hours = task.get('estimated_hours', 1)
        
        # Heavy bonus for quick tasks
        if effort_hours <= 1:
            bonus = 50
        elif effort_hours <= 2:
            bonus = 30
        elif effort_hours <= 4:
            bonus = 15
        else:
            bonus = 0
            
        return base_score + bonus
    
    return sorted(tasks, key=fastest_score, reverse=True)


def sort_high_impact(tasks):
    """
    High Impact: Prioritize importance over everything else.
    """
    def impact_score(task):
        importance = task.get('importance', 5)
        # Heavily weight importance
        return importance * 20 + calculate_task_score(task) * 0.3
    
    return sorted(tasks, key=impact_score, reverse=True)


def sort_deadline_driven(tasks):
    """
    Deadline Driven: Prioritize based on due date urgency.
    """
    def deadline_score(task):
        try:
            if isinstance(task.get('due_date'), str):
                due_date = date.fromisoformat(task['due_date'])
            else:
                due_date = task.get('due_date', date.today())
                
            today = date.today()
            days_until_due = (due_date - today).days
            
            # Heavy urgency weighting
            if days_until_due < 0:
                urgency_score = 1000 + abs(days_until_due) * 50
            elif days_until_due == 0:
                urgency_score = 500
            elif days_until_due <= 1:
                urgency_score = 400
            elif days_until_due <= 3:
                urgency_score = 300
            elif days_until_due <= 7:
                urgency_score = 200
            else:
                urgency_score = max(0, 100 - days_until_due)
                
        except (ValueError, TypeError):
            urgency_score = 100
            
        return urgency_score + calculate_task_score(task) * 0.2
    
    return sorted(tasks, key=deadline_score, reverse=True)


def sort_smart_balance(tasks):
    """
    Smart Balance: Custom algorithm that balances all factors.
    This is the default algorithm from scoring.py
    """
    return sorted(tasks, key=calculate_task_score, reverse=True)


# Strategy mapping for easy access
SORTING_STRATEGIES = {
    'fastest_wins': sort_fastest_wins,
    'high_impact': sort_high_impact,
    'deadline_driven': sort_deadline_driven,
    'smart_balance': sort_smart_balance,
}


def get_available_strategies():
    """Return list of available sorting strategies."""
    return [
        {'key': 'smart_balance', 'name': 'Smart Balance', 'description': 'Balanced algorithm considering all factors'},
        {'key': 'fastest_wins', 'name': 'Fastest Wins', 'description': 'Prioritize low-effort tasks for quick completion'},
        {'key': 'high_impact', 'name': 'High Impact', 'description': 'Prioritize importance over everything'},
        {'key': 'deadline_driven', 'name': 'Deadline Driven', 'description': 'Prioritize based on due date urgency'},
    ]


def apply_sorting_strategy(tasks, strategy='smart_balance'):
    """
    Apply the specified sorting strategy to a list of tasks.
    
    Args:
        tasks: List of task dictionaries
        strategy: Strategy key (default: 'smart_balance')
        
    Returns:
        Sorted list of tasks
    """
    if strategy not in SORTING_STRATEGIES:
        strategy = 'smart_balance'
        
    return SORTING_STRATEGIES[strategy](tasks)
