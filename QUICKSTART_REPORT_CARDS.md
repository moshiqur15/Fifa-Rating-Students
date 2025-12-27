# Quick Start: Report Card Analysis

## 🚀 Get Started in 3 Minutes

### Step 1: Test with Sample Data
```bash
python demo_report_card.py data/amin.csv
```

### Step 2: Use the Interactive App
```bash
python app.py
```
Then select **Option 2**: "Analyze Student from Report Card CSV"

### Step 3: Try Your Own CSV
Create a CSV file with daily student records:

```csv
date,attendance,HW_issue,CW_issue,daily_exam1_subject,daily_exam1_mark,daily_exam2_subject,daily_exam2_mark,teacher_comment
2025-12-01,Present,False,False,Math,8,English,7,"Good participation today"
2025-12-02,Present,False,True,Math,7,English,8,"Missed some classwork"
2025-12-03,Absent,True,True,Math,0,English,0,"Was absent"
```

## 📋 What You Get

### 1. Extracted Metrics
- ✓ Attendance percentage (from daily records)
- ✓ Homework/Classwork scores (1-10)
- ✓ Exam averages (percentage)
- ✓ Class focus score (weighted metric)
- ✓ Skills from teacher comments (AI-powered)

### 2. FIFA-Style Ratings
```
🏆 OVERALL RATING: 88.6/100
Performance Tier: ELITE ⭐⭐⭐

📈 Category Breakdown:
Attendance           [██████████████████████████] 100.0/100
Homework/Classwork   [██████████████████████████] 100.0/100
Class Focus          [████████████████████░░░░░░] 89.2/100
Exam                 [███████████████████░░░░░░░] 76.1/100 ⚠
Skills               [██████████████████░░░░░░░░] 74.3/100
```

### 3. AI Improvement Plan
Personalized suggestions using Groq AI to help students improve.

## 🔧 Setup (Optional - for AI Features)

Set your Groq API key for AI-powered comment analysis:

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY = "your_api_key_here"
python app.py
```

**Without API**: The system still works with keyword-based analysis!

## 📂 Example Files

Try these sample report cards in the `data/` folder:
- **amin.csv** - Perfect attendance, strong in math
- **rina.csv** - Excellent communication skills
- **jamil.csv** - Good English/Bangla performance

## 🎯 Common Use Cases

### Use Case 1: Analyze One Student
```bash
python demo_report_card.py data/your_student.csv
```

### Use Case 2: Compare Multiple Students
```python
from src.csv_processor import CSVReportProcessor
from src.student_rating import StudentRatingModel

processor = CSVReportProcessor()
model = StudentRatingModel()

students = ["data/amin.csv", "data/rina.csv", "data/jamil.csv"]
for csv_file in students:
    data = processor.process_student_csv(csv_file)
    rating = model.compute_student_ratings(data)
    print(f"{data['student_id']}: {rating['overall_rating']:.1f}/100")
```

### Use Case 3: Generate Report for Parents
The analysis is automatically saved to:
- `logs/analysis_<student>_<timestamp>.json` (metrics)
- `logs/ai_suggestions_<student>_<timestamp>.txt` (recommendations)

## ❓ FAQ

**Q: What if my CSV format is different?**  
A: Ensure you have these required columns: `attendance`, `HW_issue`, `CW_issue`, `daily_exam1_mark`, `daily_exam2_mark`

**Q: Can I use without Groq API?**  
A: Yes! The system falls back to keyword-based comment analysis automatically.

**Q: How do I add more students?**  
A: Just create more CSV files (one per student) and run the analysis for each.

**Q: What if exam marks are out of 100, not 10?**  
A: You'll need to adjust the `compute_exam_score` method in `csv_processor.py` to not multiply by 10.

## 📚 Full Documentation

For detailed information, see:
- **REPORT_CARD_GUIDE.md** - Complete guide with all features
- **README.md** - Main project documentation

## 🎉 That's It!

You're ready to analyze student report cards with AI-powered insights!

```bash
python app.py
# Select Option 2, enter your CSV path, and enjoy! 🚀
```
