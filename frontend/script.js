// Smart Task Analyzer - Frontend JavaScript

class TaskAnalyzer {
    constructor() {
        this.tasks = [];
        this.currentInputMethod = 'json';
        this.apiBaseUrl = 'http://127.0.0.1:8000/api/tasks';
        
        this.initializeEventListeners();
        this.updateImportanceDisplay();
    }

    initializeEventListeners() {
        // Input method toggle
        document.getElementById('jsonToggle').addEventListener('click', () => this.switchInputMethod('json'));
        document.getElementById('formToggle').addEventListener('click', () => this.switchInputMethod('form'));

        // Form input handlers
        document.getElementById('taskImportance').addEventListener('input', (e) => {
            document.getElementById('importanceValue').textContent = e.target.value;
        });

        document.getElementById('addTask').addEventListener('click', () => this.addTaskFromForm());

        // Action buttons
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeTasks());
        document.getElementById('suggestBtn').addEventListener('click', () => this.getSuggestions());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());

        // Enter key support for form inputs
        ['taskTitle', 'taskDueDate', 'taskHours'].forEach(id => {
            document.getElementById(id).addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.addTaskFromForm();
            });
        });
    }

    switchInputMethod(method) {
        this.currentInputMethod = method;
        
        // Update toggle buttons
        document.getElementById('jsonToggle').classList.toggle('active', method === 'json');
        document.getElementById('formToggle').classList.toggle('active', method === 'form');
        
        // Show/hide input methods
        document.getElementById('jsonInput').classList.toggle('hidden', method !== 'json');
        document.getElementById('formInput').classList.toggle('hidden', method !== 'form');
    }

    addTaskFromForm() {
        const title = document.getElementById('taskTitle').value.trim();
        const dueDate = document.getElementById('taskDueDate').value;
        const importance = parseInt(document.getElementById('taskImportance').value);
        const hours = parseFloat(document.getElementById('taskHours').value);

        if (!title || !dueDate) {
            this.showError('Please fill in all required fields (title and due date).');
            return;
        }

        const task = {
            id: this.tasks.length + 1,
            title: title,
            due_date: dueDate,
            importance: importance,
            estimated_hours: hours,
            dependencies: []
        };

        this.tasks.push(task);
        this.displayAddedTask(task);
        this.clearForm();
    }

    displayAddedTask(task) {
        const addedTasksContainer = document.getElementById('addedTasks');
        const taskElement = document.createElement('div');
        taskElement.className = 'added-task';
        taskElement.innerHTML = `
            <div class="task-info">
                <strong>${task.title}</strong><br>
                <small>Due: ${task.due_date} | Importance: ${task.importance}/10 | Hours: ${task.estimated_hours}</small>
            </div>
            <button class="remove-task" onclick="taskAnalyzer.removeTask(${task.id})">Remove</button>
        `;
        addedTasksContainer.appendChild(taskElement);
    }

    removeTask(taskId) {
        this.tasks = this.tasks.filter(task => task.id !== taskId);
        this.refreshAddedTasksDisplay();
    }

    refreshAddedTasksDisplay() {
        const container = document.getElementById('addedTasks');
        container.innerHTML = '';
        this.tasks.forEach(task => this.displayAddedTask(task));
    }

    clearForm() {
        document.getElementById('taskTitle').value = '';
        document.getElementById('taskDueDate').value = '';
        document.getElementById('taskImportance').value = 5;
        document.getElementById('taskHours').value = 1;
        this.updateImportanceDisplay();
    }

    updateImportanceDisplay() {
        const importance = document.getElementById('taskImportance').value;
        document.getElementById('importanceValue').textContent = importance;
    }

    async analyzeTasks() {
        let tasks;
        
        if (this.currentInputMethod === 'json') {
            tasks = this.getTasksFromJSON();
        } else {
            tasks = this.tasks;
        }

        if (!tasks || tasks.length === 0) {
            this.showError('Please add some tasks to analyze.');
            return;
        }

        // Get selected sorting strategy
        const strategy = document.getElementById('strategy').value;

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/analyze/?strategy=${strategy}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(tasks)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                this.displayResults(data.tasks, 'analysis', strategy);
            } else {
                this.showError(data.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showError(`Failed to analyze tasks: ${error.message}. Make sure the Django server is running on http://127.0.0.1:8000`);
        } finally {
            this.showLoading(false);
        }
    }

    async getSuggestions() {
        let tasks;
        
        if (this.currentInputMethod === 'json') {
            tasks = this.getTasksFromJSON();
        } else {
            tasks = this.tasks;
        }

        if (!tasks || tasks.length === 0) {
            this.showError('Please add some tasks to get suggestions.');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/suggest/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(tasks)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                this.displaySuggestions(data);
            } else {
                this.showError(data.error || 'Failed to get suggestions');
            }

        } catch (error) {
            console.error('Error:', error);
            this.showError(`Failed to get suggestions: ${error.message}. Make sure the Django server is running on http://127.0.0.1:8000`);
        } finally {
            this.showLoading(false);
        }
    }

    getTasksFromJSON() {
        try {
            const taskInput = document.getElementById('taskInput').value.trim();
            if (!taskInput) {
                return null;
            }
            return JSON.parse(taskInput);
        } catch (error) {
            this.showError('Invalid JSON format. Please check your input.');
            return null;
        }
    }

    displayResults(tasks, type = 'analysis', strategy = 'smart_balance') {
        const resultsContainer = document.getElementById('results');
        
        const strategyNames = {
            'smart_balance': 'Smart Balance',
            'fastest_wins': 'Fastest Wins',
            'high_impact': 'High Impact',
            'deadline_driven': 'Deadline Driven'
        };
        
        const strategyDescriptions = {
            'smart_balance': 'Balanced algorithm considering all factors',
            'fastest_wins': 'Prioritizing low-effort tasks for quick completion',
            'high_impact': 'Prioritizing importance over everything',
            'deadline_driven': 'Prioritizing based on due date urgency'
        };
        
        let html = `
            <div class="summary-section">
                <h3>📊 Analysis Complete!</h3>
                <p>Analyzed ${tasks.length} tasks using <strong>${strategyNames[strategy]}</strong> strategy</p>
            </div>
            <div class="strategy-info">
                <h4>🎯 ${strategyNames[strategy]} Strategy</h4>
                <p>${strategyDescriptions[strategy]}</p>
            </div>
        `;

        tasks.forEach((task, index) => {
            const priorityClass = task.priority_level.toLowerCase();
            const rank = index + 1;
            
            html += `
                <div class="task-card ${priorityClass}">
                    <div class="task-header">
                        <div>
                            <div class="task-title">#${rank} ${task.title}</div>
                            <span class="priority-badge ${priorityClass}">${task.priority_level}</span>
                        </div>
                    </div>
                    
                    <div class="task-details">
                        <div class="detail-item">
                            <span class="icon">📅</span>
                            <span>Due: ${task.due_date}</span>
                        </div>
                        <div class="detail-item">
                            <span class="icon">⭐</span>
                            <span>Importance: ${task.importance}/10</span>
                        </div>
                        <div class="detail-item">
                            <span class="icon">⏱️</span>
                            <span>Hours: ${task.estimated_hours}</span>
                        </div>
                        <div class="detail-item">
                            <span class="icon">🎯</span>
                            <span>Score: ${task.priority_score}</span>
                        </div>
                    </div>
                    
                    <div class="task-explanation">
                        ${task.explanation}
                    </div>
                </div>
            `;
        });

        resultsContainer.innerHTML = html;
    }

    displaySuggestions(data) {
        const resultsContainer = document.getElementById('results');
        
        let html = `
            <div class="summary-section">
                <h3>💡 Today's Recommendations</h3>
                <p>${data.summary}</p>
            </div>
        `;

        data.top_tasks.forEach(recommendation => {
            const task = recommendation.task;
            const priorityClass = task.priority_level.toLowerCase();
            
            html += `
                <div class="task-card ${priorityClass}">
                    <div class="task-header">
                        <div>
                            <div class="task-title">🏆 ${task.title}</div>
                            <span class="priority-badge ${priorityClass}">Rank #${recommendation.rank}</span>
                        </div>
                    </div>
                    
                    <div class="task-details">
                        <div class="detail-item">
                            <span class="icon">📅</span>
                            <span>Due: ${task.due_date}</span>
                        </div>
                        <div class="detail-item">
                            <span class="icon">⭐</span>
                            <span>Importance: ${task.importance}/10</span>
                        </div>
                        <div class="detail-item">
                            <span class="icon">⏱️</span>
                            <span>Hours: ${task.estimated_hours}</span>
                        </div>
                        <div class="detail-item">
                            <span class="icon">🎯</span>
                            <span>Score: ${task.priority_score}</span>
                        </div>
                    </div>
                    
                    <div class="task-explanation">
                        <strong>Why this task?</strong> ${recommendation.reason}
                    </div>
                </div>
            `;
        });

        // Add actionable next steps
        html += `
            <div class="summary-section" style="background: #48bb78;">
                <h3>🚀 Action Plan</h3>
                <p>Start with "${data.top_tasks[0].task.title}" - it's your highest priority task right now!</p>
            </div>
        `;

        resultsContainer.innerHTML = html;
    }

    showLoading(show) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        const results = document.getElementById('results');
        
        if (show) {
            loadingSpinner.classList.remove('hidden');
            results.style.opacity = '0.5';
        } else {
            loadingSpinner.classList.add('hidden');
            results.style.opacity = '1';
        }
    }

    showError(message) {
        const resultsContainer = document.getElementById('results');
        resultsContainer.innerHTML = `
            <div style="background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; padding: 20px; border-radius: 10px; text-align: center;">
                <h3>❌ Error</h3>
                <p>${message}</p>
                <small style="opacity: 0.7; display: block; margin-top: 10px;">
                    Make sure your Django server is running: <code>python manage.py runserver</code>
                </small>
            </div>
        `;
    }

    clearAll() {
        // Clear JSON input
        document.getElementById('taskInput').value = '';
        
        // Clear form inputs
        this.clearForm();
        
        // Clear added tasks
        this.tasks = [];
        document.getElementById('addedTasks').innerHTML = '';
        
        // Reset results
        document.getElementById('results').innerHTML = `
            <div class="welcome-message">
                <h3>👋 Welcome to Smart Task Analyzer!</h3>
                <p>Add your tasks on the left and click "Analyze Tasks" to see intelligent prioritization.</p>
                <div class="features">
                    <div class="feature">
                        <span class="icon">⚡</span>
                        <span>Urgency-based scoring</span>
                    </div>
                    <div class="feature">
                        <span class="icon">🎯</span>
                        <span>Importance weighting</span>
                    </div>
                    <div class="feature">
                        <span class="icon">🏃</span>
                        <span>Quick wins detection</span>
                    </div>
                </div>
            </div>
        `;
    }
}

// Initialize the application when the page loads
let taskAnalyzer;
document.addEventListener('DOMContentLoaded', function() {
    taskAnalyzer = new TaskAnalyzer();
    
    // Set today's date as default for the date input
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('taskDueDate').value = today;
});

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}
