# 📊 Model Monitoring & Improvement Guide

Complete guide on how to monitor, evaluate, and improve your Student Rating Model over time.

## 🎯 Overview

The Student Rating System uses adaptive learning to improve its accuracy over time. This guide teaches you how to monitor performance and make improvements.

## 📈 Key Performance Metrics

### 1. Total Predictions
**What it is**: Number of students analyzed  
**How to check**: Menu Option 3  
**Good target**: 20+ (more data = better learning)  

### 2. Feedback Count
**What it is**: Number of times you've corrected the model  
**How to check**: Menu Option 3  
**Good target**: At least 30% of predictions  
**Why it matters**: Model needs feedback to learn

### 3. Average Error
**What it is**: How far off predictions are from your feedback  
**How to check**: Menu Option 3  
**Excellent**: < 3 points  
**Good**: 3-5 points  
**Needs work**: > 5 points  

### 4. Improvement Rate
**What it is**: Whether model is getting better over time  
**How to check**: Menu Option 3  
**Positive number**: Model is improving ✅  
**Negative number**: Model might be overfitting ⚠️  
**Zero**: Need more feedback data

## 🔍 How to Monitor Your Model

### Daily Monitoring (For Active Use)

```bash
# 1. Run your analyses as normal
python app.py

# 2. Always provide feedback when prompted
# Be honest! The model learns from corrections

# 3. Check performance weekly
Menu Option 3 → View Model Performance
```

### Weekly Review Checklist

- [ ] Average error is decreasing
- [ ] Improvement rate is positive
- [ ] Feedback count is growing
- [ ] Predictions feel accurate

### Monthly Deep Dive

1. **Export performance history**
   ```python
   from src.student_rating import StudentRatingModel
   model = StudentRatingModel()
   model.load_model("models/student_rating_model.pkl")
   metrics = model.get_model_performance()
   print(metrics)
   ```

2. **Analyze logs**
   - Review `logs/` directory
   - Compare predictions vs reality
   - Identify patterns in errors

3. **Weight analysis**
   - Check current weights (Menu Option 3)
   - Do they make sense for your context?
   - Consider manual adjustments if needed

## 🛠️ Improvement Strategies

### Strategy 1: Consistent Feedback

**Problem**: Model not improving (improvement rate ~0%)  
**Solution**: Provide more feedback

```
After EVERY analysis:
1. Think: "Does this rating feel right?"
2. If not, provide feedback with correct rating
3. Be specific about which category is off
```

**Target**: Feedback on at least 30% of predictions

### Strategy 2: Manual Weight Adjustment

**Problem**: Model consistently over/under-values a category  
**Solution**: Manually adjust weights

```python
# Edit src/student_rating.py, line 22-29
self.weights = {
    "attendance": 0.25,      # Increased from 0.2
    "homework": 0.15,
    "classwork": 0.10,
    "class_focus": 0.15,
    "exam": 0.20,            # Decreased from 0.25
    "skills": 0.15
}
# Weights must sum to 1.0
```

**When to do this**:
- After 50+ predictions with consistent patterns
- When average error stays high (>5)
- When you understand your specific context better

### Strategy 3: Data Quality

**Problem**: Erratic predictions  
**Solution**: Improve input data consistency

**Best practices**:
- Use same scale for all students
- Be consistent with what scores mean
- Document your rating criteria
- Don't compare across very different contexts

### Strategy 4: Periodic Model Reset

**Problem**: Model seems stuck or confused  
**Solution**: Start fresh while keeping insights

```python
# Backup current model
import shutil
shutil.copy(
    "models/student_rating_model.pkl",
    "models/backup_student_rating_model.pkl"
)

# Start fresh
# Delete models/student_rating_model.pkl
# Model will use default weights on next run
```

**When to do this**:
- After major changes in rating criteria
- If improvement rate goes negative for weeks
- Once per semester/term

## 📊 Understanding Your Weights

### Current Weights Interpretation

View your current weights: Menu Option 3

```
attendance    0.200  (20.0%)  - How much attendance matters
homework      0.150  (15.0%)  - Homework impact
classwork     0.100  (10.0%)  - Classwork impact
class_focus   0.150  (15.0%)  - Focus/engagement impact
exam          0.250  (25.0%)  - Exam performance impact
skills        0.150  (15.0%)  - Overall skills impact
```

### Weight Adjustment Examples

**Example 1: Attendance matters more**
```python
# For schools with strict attendance policies
self.weights = {
    "attendance": 0.30,    # +0.10
    "homework": 0.15,
    "classwork": 0.10,
    "class_focus": 0.10,   # -0.05
    "exam": 0.20,          # -0.05
    "skills": 0.15
}
```

**Example 2: Skills-focused**
```python
# For project-based or vocational programs
self.weights = {
    "attendance": 0.15,    # -0.05
    "homework": 0.10,      # -0.05
    "classwork": 0.10,
    "class_focus": 0.15,
    "exam": 0.20,          # -0.05
    "skills": 0.30         # +0.15
}
```

**Example 3: Exam-heavy**
```python
# For test-focused curricula
self.weights = {
    "attendance": 0.15,    # -0.05
    "homework": 0.10,      # -0.05
    "classwork": 0.10,
    "class_focus": 0.10,   # -0.05
    "exam": 0.40,          # +0.15
    "skills": 0.15
}
```

## 🎓 Advanced Monitoring

### Custom Performance Tracking

Create a monitoring script:

```python
# monitor.py
import sys
sys.path.insert(0, 'src')
from student_rating import StudentRatingModel
import json
from datetime import datetime

model = StudentRatingModel()
model.load_model("models/student_rating_model.pkl")

metrics = model.get_model_performance()
metrics['timestamp'] = datetime.now().isoformat()

# Save to log
with open(f"logs/performance_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
    json.dump(metrics, f, indent=2)

print("Performance Snapshot:")
print(json.dumps(metrics, indent=2))
```

Run weekly: `python monitor.py`

### Trend Analysis

```python
# Compare performance over time
import json
import glob

files = sorted(glob.glob("logs/performance_*.json"))
for file in files[-5:]:  # Last 5 snapshots
    with open(file) as f:
        data = json.load(f)
    print(f"{file}: Error={data['average_error']}, Improvement={data['improvement_rate']}%")
```

## 🚨 Warning Signs

### Red Flags to Watch For

1. **Average error increasing**
   - Action: Review recent feedback
   - Check for inconsistent ratings
   - Consider weight adjustment

2. **Negative improvement rate**
   - Action: More feedback needed
   - Or possibly overfitting
   - Consider model reset

3. **Very low feedback count**
   - Action: Make feedback a habit
   - Set a target (e.g., feedback on 50% of predictions)

4. **Wildly different weights from default**
   - Action: Document why
   - Ensure it makes sense for your context
   - Consider if you need a separate model

## 📚 Learning Resources

### Understanding Your Model

1. **Prediction History**
   ```python
   model = StudentRatingModel()
   model.load_model("models/student_rating_model.pkl")
   
   # View last 10 predictions
   for pred in model.prediction_history[-10:]:
       print(f"{pred['student_id']}: {pred['overall_rating']}")
   ```

2. **Error Patterns**
   ```python
   errors = model.performance_metrics['accuracy_scores']
   import matplotlib.pyplot as plt
   
   plt.plot(errors)
   plt.title("Prediction Error Over Time")
   plt.xlabel("Prediction Number")
   plt.ylabel("Absolute Error")
   plt.show()
   ```

### Jupyter Notebook Analysis

Create `notebooks/model_analysis.ipynb`:

```python
import sys
sys.path.insert(0, '../src')
from student_rating import StudentRatingModel
import pandas as pd
import matplotlib.pyplot as plt

model = StudentRatingModel()
model.load_model("../models/student_rating_model.pkl")

# Create performance dashboard
metrics = model.get_model_performance()
errors = model.performance_metrics['accuracy_scores']

# Plot error trend
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(errors)
plt.title("Error Trend")
plt.xlabel("Prediction")
plt.ylabel("Error")

plt.subplot(1, 2, 2)
weights = list(metrics['current_weights'].values())
labels = list(metrics['current_weights'].keys())
plt.bar(labels, weights)
plt.title("Current Weights")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

## ✅ Monthly Improvement Checklist

- [ ] Check average error (target: decreasing)
- [ ] Review improvement rate (target: positive)
- [ ] Verify feedback ratio (target: >30%)
- [ ] Analyze weight changes (make sense?)
- [ ] Review sample predictions (feel accurate?)
- [ ] Check logs for patterns
- [ ] Update documentation if weights changed
- [ ] Backup model file
- [ ] Plan adjustments for next month

## 🎯 Success Criteria

Your model is performing well when:

✅ Average error < 5 points  
✅ Improvement rate positive  
✅ Predictions feel intuitively correct  
✅ Weights make sense for your context  
✅ Regular feedback being provided  
✅ Consistent rating criteria being used

## 📞 Getting Help

If your model isn't improving:
1. Review this guide
2. Check your feedback consistency
3. Verify input data quality
4. Consider context-specific weight adjustments
5. Try a model reset if needed

Remember: **The model learns from you!** More feedback = better predictions.

---

**Pro Tip**: Set a calendar reminder to check model performance every week for the first month, then monthly after that.
