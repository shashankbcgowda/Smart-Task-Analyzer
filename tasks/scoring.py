from datetime import date
import json

def calculate_task_score(task_data):
    """
    Calculates a priority score for a task.
    Higher score = Higher priority.
    
    Algorithm considers:
    1. Urgency (due date proximity)
    2. Importance (user-defined 1-10 scale)
    3. Effort (quick wins get bonus)
    4. Dependencies (tasks with no dependencies get slight boost)
    
    Args:
        task_data: Dictionary containing task information
        
    Returns:
        int: Priority score (higher = more important)
    """
    score = 0
    
    # Handle missing or invalid data with defaults
    importance = task_data.get('importance', 5)
    estimated_hours = task_data.get('estimated_hours', 1)
    dependencies = task_data.get('dependencies', [])
    
    # Ensure importance is within valid range
    importance = max(1, min(10, importance))
    
    # 1. URGENCY CALCULATION (Most Important Factor)
    try:
        if isinstance(task_data.get('due_date'), str):
            # Parse string date (expected format: YYYY-MM-DD)
            due_date = date.fromisoformat(task_data['due_date'])
        else:
            due_date = task_data.get('due_date', date.today())
            
        today = date.today()
        days_until_due = (due_date - today).days
        
        if days_until_due < 0:
            # OVERDUE! Massive priority boost
            score += 100 + abs(days_until_due) * 10  # More overdue = higher priority
        elif days_until_due == 0:
            score += 80  # Due today
        elif days_until_due <= 1:
            score += 60  # Due tomorrow
        elif days_until_due <= 3:
            score += 40  # Due within 3 days
        elif days_until_due <= 7:
            score += 20  # Due within a week
        else:
            # Future tasks get lower urgency scores
            score += max(0, 10 - (days_until_due // 7))
            
    except (ValueError, TypeError):
        # If date parsing fails, treat as medium urgency
        score += 15
    
    # 2. IMPORTANCE WEIGHTING (Second Most Important)
    # Scale importance (1-10) to have significant impact
    score += importance * 8
    
    # 3. EFFORT CONSIDERATION (Quick Wins Strategy)
    if estimated_hours <= 1:
        score += 15  # Very quick tasks get good bonus
    elif estimated_hours <= 2:
        score += 10  # Quick tasks get bonus
    elif estimated_hours <= 4:
        score += 5   # Medium tasks get small bonus
    else:
        # Long tasks get penalty (unless very important)
        score -= max(0, (estimated_hours - 4) * 2)
    
    # 4. DEPENDENCY BONUS
    if not dependencies or len(dependencies) == 0:
        score += 5  # Tasks with no dependencies are easier to start
    
    # 5. SPECIAL COMBINATIONS
    # High importance + overdue = extra boost
    try:
        if days_until_due < 0 and importance >= 8:
            score += 25
        
        # Quick + important = productivity boost
        if estimated_hours <= 2 and importance >= 7:
            score += 10
    except:
        pass
    
    return max(0, score)  # Ensure non-negative score


def get_task_priority_level(score):
    """
    Convert numerical score to human-readable priority level.
    
    Args:
        score: Numerical priority score
        
    Returns:
        str: Priority level description
    """
    if score >= 100:
        return "CRITICAL"
    elif score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "MINIMAL"


def explain_score(task_data, score):
    """
    Generate human-readable explanation for why a task got its score.
    
    Args:
        task_data: Dictionary containing task information
        score: Calculated priority score
        
    Returns:
        str: Explanation of the scoring
    """
    explanations = []
    
    # Analyze urgency
    try:
        if isinstance(task_data.get('due_date'), str):
            due_date = date.fromisoformat(task_data['due_date'])
        else:
            due_date = task_data.get('due_date', date.today())
            
        today = date.today()
        days_until_due = (due_date - today).days
        
        if days_until_due < 0:
            explanations.append(f"⚠️ OVERDUE by {abs(days_until_due)} days")
        elif days_until_due == 0:
            explanations.append("🔥 Due TODAY")
        elif days_until_due <= 3:
            explanations.append(f"⏰ Due in {days_until_due} days")
        
    except:
        explanations.append("📅 Date unclear")
    
    # Analyze importance
    importance = task_data.get('importance', 5)
    if importance >= 8:
        explanations.append(f"🎯 Very important ({importance}/10)")
    elif importance >= 6:
        explanations.append(f"📌 Important ({importance}/10)")
    
    # Analyze effort
    hours = task_data.get('estimated_hours', 1)
    if hours <= 1:
        explanations.append("⚡ Quick win (≤1h)")
    elif hours <= 2:
        explanations.append("🏃 Fast task (≤2h)")
    
    priority_level = get_task_priority_level(score)
    
    explanation = f"Priority: {priority_level} (Score: {score})"
    if explanations:
        explanation += " - " + ", ".join(explanations)
    
    return explanation