# Student Improvement Prediction Model Guide

## Overview

The **Student Improvement Prediction Model** uses machine learning to predict:
- **Whether** a student will improve
- **When** improvement will occur (across 6 timelines)
- **How much** marks will increase

Predictions are based on:
- Historical performance trends
- Assigned improvement tasks
- Student attributes (hardwork, determination, focus, etc.)

## Features

### 1. **Multi-Timeline Predictions**
Predicts improvement across 6 timelines:
- **1 Week**: Short-term quick wins
- **3 Weeks**: Initial habit formation
- **1 Month**: First measurable results
- **2 Months**: Significant progress
- **6 Months**: Long-term development
- **1 Year**: Complete transformation

### 2. **Dual Prediction System**
- **Classification**: Will the student improve? (Yes/No + Probability)
- **Regression**: By how many marks? (Numeric prediction)

### 3. **Interactive Visualizations**
- **Line Chart**: Mark increase trajectory over time
- **Bar Chart**: Improvement probability by timeline
- **Combined View**: Dual-axis comparison
- **Details Table**: Complete timeline breakdown

### 4. **Smart Feature Engineering**
Automatically extracts features from:
- Student performance data (attendance, homework, exams)
- Task complexity (XP, time estimates)
- Student attributes (normalized to 0-1 scale)
- Historical improvement patterns

## How It Works

### Pipeline Overview

```
1. Student Data Input
   ↓
2. Create/Load Historical Data
   ↓
3. Aggregate Performance Features
   ↓
4. Convert Tasks to ML Features (XP, time, difficulty)
   ↓
5. Train Random Forest Models (if not trained)
   ↓
6. Generate Predictions for Each Timeline
   ↓
7. Create Visualization Data
   ↓
8. Display Graphs & Recommendations
```

### Model Architecture

```
StudentPredictionModel
├── RandomForestClassifier (150 trees)
│   └── Predicts: Will improve (0/1)
│
├── RandomForestRegressor (150 trees)
│   └── Predicts: Mark increase (0-30)
│
├── StandardScaler
│   └── Normalizes features
│
└── Timeline Multipliers
    ├── 1w: 0.15 (15% effect)
    ├── 3w: 0.35 (35% effect)
    ├── 1m: 0.50 (50% effect)
    ├── 2m: 0.70 (70% effect)
    ├── 6m: 0.95 (95% effect)
    └── 1y: 1.00 (full effect)
```

### Feature Engineering

**Input Features (14 total)**:
1. `mean_score`: Average historical score
2. `last_score`: Most recent score
3. `sessions`: Number of historical sessions
4. `avg_time_spent`: Average time per session
5. `completion_rate`: Task completion rate
6. `improvement_per_session`: Historical improvement rate
7. `total_xp`: Sum of task XP points
8. `n_tasks`: Number of assigned tasks
9. `est_minutes`: Total estimated time
10. `hardwork`: Student hardwork attribute (0-1)
11. `determination`: Determination level (0-1)
12. `focus`: Focus ability (0-1)
13. `discipline`: Discipline score (0-1)
14. `creativity`: Problem-solving creativity (0-1)

## Usage in Webapp

### Step-by-Step

1. **Generate Improvement Plan**
   - Follow improvement plan generation process
   - Tasks are created with difficulty levels and time estimates

2. **Click "Generate Improvement Predictions"**
   - System converts tasks to ML features
   - Trains model if needed
   - Generates predictions for all timelines

3. **View Summary Metrics**
   - Overall improvement probability
   - Average mark increase
   - Best timeline for results

4. **Explore Graphs**
   - **Tab 1**: Mark increase trajectory
   - **Tab 2**: Probability distribution
   - **Tab 3**: Combined view

5. **Review Timeline Details**
   - Table with full breakdown
   - Save predictions as JSON

## Graph Interpretation

### Mark Increase Over Time (Line Chart)

```
Example:
1 Week:    +2.3 marks
3 Weeks:   +5.1 marks
1 Month:   +7.2 marks  ← Steepest growth
2 Months:  +10.1 marks
6 Months:  +13.7 marks
1 Year:    +14.5 marks ← Plateau
```

**What to look for:**
- **Steep upward slope**: Rapid initial improvement
- **Plateau**: Long-term stabilization
- **Peak timeline**: When maximum improvement occurs

### Improvement Probability (Bar Chart)

```
Example:
1 Week:    45%  (Yellow - Moderate)
3 Weeks:   62%  (Yellow - Moderate)
1 Month:   75%  (Green - High)  ← Best probability
2 Months:  78%  (Green - High)
6 Months:  72%  (Green - High)
1 Year:    70%  (Green - High)
```

**Color coding:**
- 🟢 **Green (≥70%)**: High confidence
- 🟡 **Yellow (50-69%)**: Moderate confidence
- 🔴 **Red (<50%)**: Low confidence

### Combined View

Shows both metrics together for easy comparison:
- Top graph: Mark trajectory
- Bottom graph: Probability bars
- Helps identify optimal intervention window

## API Integration

### Loading the Model

```python
import pickle
from src.prediction_model import StudentPredictionModel

# Load from pickle
with open('models/student_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Or create new
model = StudentPredictionModel()
```

### Making Predictions

```python
# Prepare student data
student_data = {
    'student_id': 'Amin',
    'attendance': 75.5,
    'homework': 6,
    'classwork': 7,
    'class_focus': 68.2,
    'exam': 62.5,
    'skills': {
        'problem_solving': 6,
        'communication': 7,
        'discipline': 5
    }
}

# Prepare tasks
tasks = [
    {
        'task': 'Daily homework tracker',
        'xp': 20,
        'time_estimate_minutes': 15,
        'category': 'Homework'
    },
    {
        'task': 'Weekly practice tests',
        'xp': 40,
        'time_estimate_minutes': 45,
        'category': 'Exam'
    },
    # ... more tasks
]

# Generate predictions
predictions = model.predict_improvement(
    student_data=student_data,
    tasks=tasks,
    timelines=['1w', '3w', '1m', '2m', '6m', '1y']
)

# Access results
print(predictions['summary'])
print(predictions['visualization_data'])
```

### Output Structure

```json
{
  "student_id": "Amin",
  "generated_date": "2025-12-09T17:46:41",
  "timelines": [
    {
      "student_id": "Amin",
      "subject": "General",
      "timeline": "1w",
      "improve_probability": 0.45,
      "predicted_mark_increase": 2.3,
      "will_improve": 0
    },
    // ... more timelines
  ],
  "summary": {
    "overall_improvement_probability": 68.5,
    "average_predicted_increase": 8.8,
    "best_timeline": "2m",
    "best_timeline_increase": 10.1,
    "best_timeline_probability": 78.2,
    "recommendation": "The student has good improvement prospects..."
  },
  "visualization_data": {
    "timelines": ["1 Week", "3 Weeks", ...],
    "probabilities": [45.0, 62.0, 75.0, ...],
    "mark_increases": [2.3, 5.1, 7.2, ...],
    "will_improve_flags": [0, 1, 1, ...]
  }
}
```

## Technical Details

### Model Training

The model auto-trains on the first prediction using:
1. **Synthetic History**: Generates 10 historical sessions based on current performance
2. **Target Creation**: Derives improvement targets from historical trends
3. **Feature Scaling**: StandardScaler normalization
4. **Model Fitting**: Random Forest ensemble (150 trees)

### Prediction Logic

For each timeline:
1. Scale task effects by timeline multiplier
2. Prepare feature vector with scaled values
3. Run through classifier for probability
4. Run through regressor for mark increase
5. Apply threshold (≥50% = will improve)

### Attributes Mapping

Student attributes derived from performance:
- **Hardwork**: homework score / 10
- **Determination**: class_focus / 100
- **Focus**: classwork score / 10
- **Discipline**: attendance / 100
- **Creativity**: problem_solving skill / 10

## Files

### Core Files
- `src/prediction_model.py` - Main model class (385 lines)
- `models/student_prediction_model.pkl` - Pickled model
- `create_prediction_model_pkl.py` - Pickle generator

### Integration
- `webapp.py` - Prediction UI (lines 973-1166)

## Validation & Accuracy

### Expected Performance
- **Classification Accuracy**: 70-85% (typical for educational ML)
- **Regression MAE**: 2-5 marks (acceptable error range)
- **R² Score**: 0.4-0.7 (moderate explanatory power)

### Limitations
1. **Synthetic History**: Uses simulated data if no real history available
2. **Small Sample**: Trains on single student initially
3. **Linear Assumptions**: Assumes consistent effort/improvement rate
4. **No External Factors**: Doesn't account for life events, health, etc.

### Improvements for Production
- Collect real historical data from multiple students
- Implement cross-validation
- Add confidence intervals
- Track prediction accuracy over time
- Adjust multipliers based on actual outcomes

## Troubleshooting

### Model Not Loading
```bash
python create_prediction_model_pkl.py
```

### Predictions Seem Off
- Check if student has realistic performance data
- Verify task complexity is appropriate
- Ensure sufficient tasks (3-10 recommended)
- Review historical trend (is student actually improving?)

### Import Errors
```bash
# Verify file exists
dir src\prediction_model.py
dir models\student_prediction_model.pkl
```

## Example Scenarios

### Scenario 1: Struggling Student

**Input:**
- Current score: 45%
- Improvement rate: +0.5 per session
- 5 medium-difficulty tasks

**Predicted Output:**
- 1 Week: +1.5 marks (35% probability)
- 1 Month: +4.2 marks (55% probability)
- 6 Months: +8.5 marks (68% probability)

**Recommendation**: Focus on long-term consistent effort

### Scenario 2: High Performer

**Input:**
- Current score: 85%
- Improvement rate: +1.2 per session
- 7 challenging tasks

**Predicted Output:**
- 1 Week: +3.2 marks (75% probability)
- 1 Month: +9.1 marks (85% probability)
- 6 Months: +12.3 marks (88% probability)

**Recommendation**: Excellent prospects, maintain momentum

### Scenario 3: Inconsistent Student

**Input:**
- Current score: 62%
- Improvement rate: +0.2 per session (low)
- 4 easy tasks

**Predicted Output:**
- 1 Week: +0.8 marks (25% probability)
- 1 Month: +2.1 marks (45% probability)
- 6 Months: +5.2 marks (58% probability)

**Recommendation**: Consider revised task plan or additional support

## Version History

- **v1.0** (2025-12-09): Initial release
  - Multi-timeline prediction
  - Interactive visualizations
  - Random Forest models
  - Auto-training capability

## Future Enhancements

Potential additions:
- **Real-time tracking**: Update predictions as student progresses
- **Confidence intervals**: Show prediction uncertainty
- **Subject-specific models**: Different models per subject
- **Ensemble methods**: Combine multiple algorithms
- **External factors**: Weather, holidays, stress levels
- **Peer comparison**: Compare to similar students

## License & Credits

Part of the Student Rating System project.
Uses scikit-learn for machine learning and Plotly for visualizations.
