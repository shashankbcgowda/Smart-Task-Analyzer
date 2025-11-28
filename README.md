# 🧠 Smart Task Analyzer

A Django-based web application that intelligently prioritizes tasks using a custom scoring algorithm to help users decide what to work on first.

## 🎯 Project Overview

The Smart Task Analyzer takes a list of tasks with properties like due date, importance, and effort, then uses an intelligent algorithm to prioritize them. This helps users make better decisions about task management and productivity.

## ✨ Features

- **Intelligent Prioritization**: Custom algorithm considers urgency, importance, effort, and dependencies
- **Dual Input Methods**: JSON input for bulk tasks or form-based input for individual tasks
- **Real-time Analysis**: Instant task scoring and priority ranking
- **Visual Priority Indicators**: Color-coded task cards based on priority levels
- **Smart Suggestions**: Get top 3 task recommendations with explanations
- **Responsive Design**: Works on desktop and mobile devices
- **Edge Case Handling**: Robust handling of missing data, past due dates, and invalid inputs

## 🏗️ Project Structure

```
task-analyzer/
├── backend/                  # Main Django Project Folder
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks/                    # Django App
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py             # Task data model
│   ├── scoring.py            # Smart prioritization algorithm
│   ├── tests.py
│   ├── urls.py               # API endpoints
│   └── views.py              # API logic
├── frontend/                 # Frontend Files
│   ├── index.html            # Main interface
│   ├── styles.css            # Styling and responsive design
│   └── script.js             # Interactive functionality
├── venv/                     # Virtual environment
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧮 Algorithm Explanation

### Scoring Components

The Smart Task Analyzer uses a multi-factor scoring algorithm:

#### 1. **Urgency (Highest Weight)**
- **Overdue tasks**: +100 points + 10 points per day overdue
- **Due today**: +80 points
- **Due tomorrow**: +60 points
- **Due within 3 days**: +40 points
- **Due within a week**: +20 points
- **Future tasks**: Decreasing points based on weeks away

#### 2. **Importance (Second Highest Weight)**
- User-defined scale (1-10) multiplied by 8
- Ensures high-importance tasks get significant priority boost

#### 3. **Effort Consideration (Quick Wins Strategy)**
- **≤1 hour**: +15 points (very quick wins)
- **≤2 hours**: +10 points (quick tasks)
- **≤4 hours**: +5 points (medium tasks)
- **>4 hours**: Penalty of -2 points per extra hour

#### 4. **Dependencies**
- Tasks with no dependencies: +5 points (easier to start)

#### 5. **Special Combinations**
- High importance + overdue: +25 bonus points
- Quick task + high importance: +10 productivity boost

### Priority Levels

- **CRITICAL**: Score ≥ 100 (Usually overdue or due today with high importance)
- **HIGH**: Score ≥ 70
- **MEDIUM**: Score ≥ 40
- **LOW**: Score ≥ 20
- **MINIMAL**: Score < 20

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

### Installation



1. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the development server**
   ```bash
   python manage.py runserver
   ```

5. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or visit the API directly at `http://127.0.0.1:8000/api/tasks/`

## 🔧 Usage

### Method 1: JSON Input

Use the JSON input area to paste task data:

```json
[
  {
    "title": "Complete project report",
    "due_date": "2024-12-01",
    "importance": 8,
    "estimated_hours": 3,
    "dependencies": []
  },
  {
    "title": "Review team presentations",
    "due_date": "2024-11-30",
    "importance": 6,
    "estimated_hours": 1,
    "dependencies": []
  }
]
```

### Method 2: Form Input

Use the form interface to add tasks one by one:
1. Enter task title
2. Set due date
3. Adjust importance slider (1-10)
4. Set estimated hours
5. Click "Add Task"

### Analysis Options

- **Analyze Tasks**: Get complete priority ranking of all tasks
- **Get Top 3 Suggestions**: Receive focused recommendations for immediate action

## 🛠️ API Endpoints

### POST `/api/tasks/analyze/`

**Description**: Accept a list of tasks and return them sorted by priority score.

**Parameters**: 
- `strategy` (query param): Sorting strategy (`smart_balance`, `fastest_wins`, `high_impact`, `deadline_driven`)

**Request Body** (matches PDF specification):
```json
[
  {
    "title": "Fix login bug",
    "due_date": "2025-11-30",
    "estimated_hours": 3,
    "importance": 8,
    "dependencies": []
  }
]
```

**Response**:
```json
{
  "status": "success",
  "total_tasks": 1,
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "importance": 8,
      "estimated_hours": 3,
      "dependencies": [],
      "priority_score": 95,
      "priority_level": "HIGH",
      "explanation": "Priority: HIGH (Score: 95) - Due in 2 days, Very important (8/10)"
    }
  ]
}
```

### GET `/api/tasks/suggest/`

**Description**: Return the top 3 tasks the user should work on today, with explanations for why each was chosen.

**Response**:
```json
{
  "status": "success",
  "summary": "Today's Focus: Start with 'Fix login bug' (HIGH priority)",
  "top_tasks": [
    {
      "rank": 1,
      "task": { /* full task object with scoring */ },
      "reason": "Rank #1: Priority: HIGH (Score: 95) - Due in 2 days, Very important (8/10)"
    }
  ],
  "total_analyzed": 3
}
```

### GET `/api/tasks/strategies/`

**Description**: Get available sorting strategies.

**Response**:
```json
{
  "status": "success",
  "strategies": [
    {
      "key": "smart_balance",
      "name": "Smart Balance", 
      "description": "Balanced algorithm considering all factors"
    }
  ]
}
```

## 🧪 Testing Edge Cases

The system handles various edge cases:

1. **Missing Data**: Default values applied (importance: 5, hours: 1)
2. **Past Due Dates**: Tasks due in 1990 get maximum urgency score
3. **Invalid JSON**: Clear error messages with format guidance
4. **Empty Task Lists**: Appropriate user feedback
5. **Extreme Values**: Importance clamped to 1-10 range
6. **Date Parsing Errors**: Graceful fallback to medium urgency

## 🎨 Design Decisions

### Algorithm Design Decisions

**Why Urgency Over Effort?**
The algorithm prioritizes urgency over effort because:
- **Deadline pressure** is often external and non-negotiable (client deliverables, legal deadlines)
- **Overdue tasks** create cascading problems that compound over time
- **Quick wins** are rewarded but don't override critical deadlines
- **Balance** is maintained through the multi-factor approach

**Trade-offs Made:**
1. **Simplicity vs Sophistication**: Chose interpretable linear scoring over complex ML models
2. **Performance vs Accuracy**: Optimized for fast response times over perfect prioritization  
3. **Flexibility vs Consistency**: Multiple strategies vs single "perfect" algorithm
4. **User Control vs Automation**: Allow strategy selection vs fully automated decisions

**Edge Case Handling:**
- **Missing Data**: Sensible defaults (importance: 5, effort: 1 hour)
- **Invalid Dates**: Graceful fallback to medium urgency scoring
- **Circular Dependencies**: Detection with clear warnings, graceful ordering
- **Extreme Values**: Input validation and clamping (importance 1-10)

### Color Coding System

- **Red (Critical)**: Immediate attention required
- **Orange (High)**: High priority, schedule soon
- **Yellow (Medium)**: Important but not urgent
- **Green (Low)**: Can be scheduled flexibly
- **Gray (Minimal)**: Low priority or far future

## 📱 Responsive Design

The interface adapts to different screen sizes:
- **Desktop**: Side-by-side input and results layout
- **Mobile**: Stacked layout with touch-friendly controls
- **Tablet**: Optimized spacing and button sizes

## 🔮 Future Enhancements

Potential improvements for the system:
- **Task Dependencies**: Visual dependency graphs
- **Calendar Integration**: Import from Google Calendar, Outlook
- **Team Collaboration**: Multi-user task sharing
- **Analytics**: Task completion tracking and productivity insights
- **Machine Learning**: Personalized scoring based on user behavior
- **Notifications**: Due date reminders and priority alerts

## 🐛 Troubleshooting

### Common Issues

1. **Server not starting**
   ```bash
   # Make sure you're in the right directory
   cd task-analyzer
   
   # Activate virtual environment
   venv\Scripts\activate
   
   # Install dependencies
   pip install django
   
   # Run server
   python manage.py runserver
   ```

2. **Frontend can't connect to API**
   - Ensure Django server is running on `http://127.0.0.1:8000`
   - Check browser console for CORS errors
   - Verify API endpoints are accessible

3. **JSON parsing errors**
   - Validate JSON format using online validators
   - Ensure date format is YYYY-MM-DD
   - Check for trailing commas

## 📄 License

This project is created for educational purposes as part of the NxtWave assignment.

## 👨‍💻 Development

**Author**: Shashank BC  
**Assignment**: Singularium Smart Task Analyzer  
**Framework**: Django 5.2.8  
**Database**: SQLite  
**Frontend**: Vanilla HTML/CSS/JavaScript  

---

**🚀 Ready to boost your productivity? Start analyzing your tasks now!**
