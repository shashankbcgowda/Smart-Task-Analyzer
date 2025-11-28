from django.test import TestCase
from datetime import date, timedelta
from .scoring import calculate_task_score, get_task_priority_level, explain_score
from .sorting_strategies import apply_sorting_strategy, SORTING_STRATEGIES
from .dependency_analyzer import detect_circular_dependencies, get_dependency_order


class TaskScoringTests(TestCase):
    """Test cases for the task scoring algorithm."""
    
    def test_overdue_task_gets_highest_priority(self):
        """Overdue tasks should get maximum priority boost."""
        overdue_task = {
            'title': 'Overdue task',
            'due_date': (date.today() - timedelta(days=2)).isoformat(),
            'importance': 5,
            'estimated_hours': 2,
            'dependencies': []
        }
        
        future_task = {
            'title': 'Future task',
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
            'importance': 10,
            'estimated_hours': 1,
            'dependencies': []
        }
        
        overdue_score = calculate_task_score(overdue_task)
        future_score = calculate_task_score(future_task)
        
        self.assertGreater(overdue_score, future_score, 
                          "Overdue task should score higher than future task")
        self.assertGreaterEqual(overdue_score, 100, 
                               "Overdue task should get at least 100 points")
    
    def test_importance_scaling(self):
        """Higher importance should result in higher scores."""
        low_importance = {
            'title': 'Low importance',
            'due_date': (date.today() + timedelta(days=3)).isoformat(),
            'importance': 2,
            'estimated_hours': 2,
            'dependencies': []
        }
        
        high_importance = {
            'title': 'High importance',
            'due_date': (date.today() + timedelta(days=3)).isoformat(),
            'importance': 9,
            'estimated_hours': 2,
            'dependencies': []
        }
        
        low_score = calculate_task_score(low_importance)
        high_score = calculate_task_score(high_importance)
        
        self.assertGreater(high_score, low_score,
                          "Higher importance should result in higher score")
    
    def test_quick_wins_bonus(self):
        """Tasks with low effort should get bonus points."""
        quick_task = {
            'title': 'Quick task',
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'importance': 5,
            'estimated_hours': 1,
            'dependencies': []
        }
        
        long_task = {
            'title': 'Long task',
            'due_date': (date.today() + timedelta(days=5)).isoformat(),
            'importance': 5,
            'estimated_hours': 8,
            'dependencies': []
        }
        
        quick_score = calculate_task_score(quick_task)
        long_score = calculate_task_score(long_task)
        
        self.assertGreater(quick_score, long_score,
                          "Quick tasks should score higher than long tasks")
    
    def test_missing_data_handling(self):
        """Algorithm should handle missing or invalid data gracefully."""
        incomplete_task = {
            'title': 'Incomplete task',
            # Missing due_date, importance, estimated_hours
        }
        
        # Should not raise an exception
        score = calculate_task_score(incomplete_task)
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
    
    def test_priority_level_mapping(self):
        """Test that scores map correctly to priority levels."""
        self.assertEqual(get_task_priority_level(150), "CRITICAL")
        self.assertEqual(get_task_priority_level(80), "HIGH")
        self.assertEqual(get_task_priority_level(50), "MEDIUM")
        self.assertEqual(get_task_priority_level(30), "LOW")
        self.assertEqual(get_task_priority_level(10), "MINIMAL")
    
    def test_invalid_date_handling(self):
        """Test handling of invalid date formats."""
        invalid_date_task = {
            'title': 'Invalid date',
            'due_date': 'not-a-date',
            'importance': 5,
            'estimated_hours': 2,
            'dependencies': []
        }
        
        # Should not crash and should return a reasonable score
        score = calculate_task_score(invalid_date_task)
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)


class SortingStrategyTests(TestCase):
    """Test cases for different sorting strategies."""
    
    def setUp(self):
        """Set up test tasks."""
        self.test_tasks = [
            {
                'id': 1,
                'title': 'Quick important task',
                'due_date': (date.today() + timedelta(days=2)).isoformat(),
                'importance': 9,
                'estimated_hours': 1,
                'dependencies': []
            },
            {
                'id': 2,
                'title': 'Long overdue task',
                'due_date': (date.today() - timedelta(days=1)).isoformat(),
                'importance': 6,
                'estimated_hours': 8,
                'dependencies': []
            },
            {
                'id': 3,
                'title': 'Medium future task',
                'due_date': (date.today() + timedelta(days=10)).isoformat(),
                'importance': 5,
                'estimated_hours': 4,
                'dependencies': []
            }
        ]
    
    def test_fastest_wins_strategy(self):
        """Fastest wins should prioritize low-effort tasks."""
        sorted_tasks = apply_sorting_strategy(self.test_tasks, 'fastest_wins')
        
        # Quick task should be first
        self.assertEqual(sorted_tasks[0]['id'], 1,
                        "Fastest wins should prioritize quick tasks")
    
    def test_deadline_driven_strategy(self):
        """Deadline driven should prioritize overdue/urgent tasks."""
        sorted_tasks = apply_sorting_strategy(self.test_tasks, 'deadline_driven')
        
        # Overdue task should be first
        self.assertEqual(sorted_tasks[0]['id'], 2,
                        "Deadline driven should prioritize overdue tasks")
    
    def test_high_impact_strategy(self):
        """High impact should prioritize importance."""
        sorted_tasks = apply_sorting_strategy(self.test_tasks, 'high_impact')
        
        # Most important task should be first
        self.assertEqual(sorted_tasks[0]['id'], 1,
                        "High impact should prioritize important tasks")
    
    def test_invalid_strategy_fallback(self):
        """Invalid strategy should fall back to smart_balance."""
        sorted_tasks = apply_sorting_strategy(self.test_tasks, 'invalid_strategy')
        
        # Should not crash and should return sorted tasks
        self.assertEqual(len(sorted_tasks), len(self.test_tasks))
        self.assertIsInstance(sorted_tasks, list)


class DependencyAnalysisTests(TestCase):
    """Test cases for dependency analysis."""
    
    def test_circular_dependency_detection(self):
        """Should detect circular dependencies correctly."""
        circular_tasks = [
            {'id': 1, 'title': 'Task A', 'dependencies': [2]},
            {'id': 2, 'title': 'Task B', 'dependencies': [3]},
            {'id': 3, 'title': 'Task C', 'dependencies': [1]}  # Creates cycle
        ]
        
        result = detect_circular_dependencies(circular_tasks)
        
        self.assertTrue(result['has_circular'],
                       "Should detect circular dependency")
        self.assertGreater(len(result['warnings']), 0,
                          "Should generate warning messages")
    
    def test_no_circular_dependencies(self):
        """Should correctly identify when no circular dependencies exist."""
        linear_tasks = [
            {'id': 1, 'title': 'Task A', 'dependencies': []},
            {'id': 2, 'title': 'Task B', 'dependencies': [1]},
            {'id': 3, 'title': 'Task C', 'dependencies': [2]}
        ]
        
        result = detect_circular_dependencies(linear_tasks)
        
        self.assertFalse(result['has_circular'],
                        "Should not detect circular dependency")
        self.assertEqual(len(result['circular_chains']), 0,
                        "Should have no circular chains")
    
    def test_dependency_ordering(self):
        """Should provide correct dependency ordering."""
        tasks_with_deps = [
            {'id': 1, 'title': 'Task A', 'dependencies': []},
            {'id': 2, 'title': 'Task B', 'dependencies': [1]},
            {'id': 3, 'title': 'Task C', 'dependencies': [2]}  # C depends only on B
        ]
        
        result = get_dependency_order(tasks_with_deps)
        ordered_tasks = result['ordered_tasks']
        
        # Task A should come before B, and B should come before C
        task_a_pos = next(i for i, t in enumerate(ordered_tasks) if t['id'] == 1)
        task_b_pos = next(i for i, t in enumerate(ordered_tasks) if t['id'] == 2)
        task_c_pos = next(i for i, t in enumerate(ordered_tasks) if t['id'] == 3)
        
        self.assertLess(task_a_pos, task_b_pos,
                       "Task A should come before Task B")
        self.assertLess(task_b_pos, task_c_pos,
                       "Task B should come before Task C")
