# Student Report Card Analysis Guide

## Overview
This system now supports analyzing student performance from **daily report card CSV files**. The CSV processor extracts metrics from attendance records, homework/classwork completion, exam scores, and teacher comments, then feeds them into the FIFA-style rating system.

## Features

### 1. **CSV Report Card Processing**
- Automatically calculates attendance percentage from daily records
- Computes homework and classwork scores (1-10 scale)
- Averages exam marks and converts to percentage
- Calculates class focus as weighted metric (45% exam, 25% attendance, 15% HW, 15% CW)

### 2. **AI-Powered Comment Analysis**
- Uses Groq API to analyze teacher comments
- Extracts skill scores for:
  - **Problem Solving**: Math, science, logical reasoning
  - **Communication**: English/Bangla speaking, writing, expression
  - **Discipline**: Punctuality, attendance, homework behavior
- Falls back to keyword-based analysis if API is unavailable

### 3. **FIFA-Style Rating Integration**
- Processes extracted metrics through the rating model
- Generates overall rating (1-100)
- Identifies weakest areas
- Provides improvement recommendations
- Creates AI-powered improvement plans

## CSV Format

### Required Columns
Your CSV file should contain daily records with these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `date` | Date | Record date | 2025-12-01 |
| `attendance` | Text | Present/Absent | Present |
| `HW_issue` | Boolean | Homework incomplete? | False |
| `CW_issue` | Boolean | Classwork incomplete? | False |
| `daily_exam1_mark` | Number | First exam score (out of 10) | 8 |
| `daily_exam2_mark` | Number | Second exam score (out of 10) | 7 |
| `daily_exam1_subject` | Text | First exam subject | Math |
| `daily_exam2_subject` | Text | Second exam subject | English |
| `teacher_comment` | Text | Daily comment | "Good participation" |

### Optional Columns
- `student` - Student name (if not provided, extracted from filename)

### Sample CSV Structure
```csv
date,attendance,HW_issue,CW_issue,daily_exam1_subject,daily_exam1_mark,daily_exam2_subject,daily_exam2_mark,teacher_comment
2025-12-01,Present,False,False,Math,8,English,7,"Participates actively in class discussions."
2025-12-02,Present,False,False,Math,7,English,8,"Needs to review last week's assignment."
2025-12-03,Present,False,False,Math,9,English,6,"Shows improvement in logical reasoning."
```

See `data/amin.csv`, `data/rina.csv`, or `data/jamil.csv` for complete examples.

## Usage

### Method 1: Using the Main App (Interactive)

```bash
python app.py
```

Then select:
- **Option 2**: "Analyze Student from Report Card CSV (Daily Records)"
- Enter the path to your CSV file (e.g., `data/amin.csv`)
- Review extracted metrics
- Proceed with FIFA-style analysis

### Method 2: Using the Demo Script

```bash
# Analyze a single student
python demo_report_card.py data/amin.csv

# Use default (data/amin.csv)
python demo_report_card.py
```

### Method 3: Programmatic Usage

```python
from src.csv_processor import CSVReportProcessor
from src.student_rating import StudentRatingModel

# Process report card
processor = CSVReportProcessor()
student_data = processor.process_student_csv("data/amin.csv")

# Calculate ratings
rating_model = StudentRatingModel()
ratings = rating_model.compute_student_ratings(student_data)

print(f"Overall Rating: {ratings['overall_rating']}/100")
```

## Workflow

```
┌─────────────────────┐
│  Student Report     │
│  Card CSV           │
│  (Daily Records)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  CSV Processor      │
│  • Attendance %     │
│  • HW/CW Scores     │
│  • Exam Average     │
│  • Class Focus      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Groq API           │
│  Comment Analysis   │
│  • Problem Solving  │
│  • Communication    │
│  • Discipline       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Student Rating     │
│  Model              │
│  • Overall Rating   │
│  • Category Scores  │
│  • Recommendations  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Improvement     │
│  Plan Generator     │
│  • Detailed Steps   │
│  • Strengths        │
│  • Action Plan      │
└─────────────────────┘
```

## Configuration

### Groq API Setup (Optional but Recommended)

For AI-powered teacher comment analysis:

1. Get API key from [Groq Console](https://console.groq.com)
2. Set environment variable:

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY = "your_api_key_here"
```

**Windows CMD:**
```cmd
set GROQ_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY=your_api_key_here
```

3. Or create a `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

Without Groq API, the system automatically falls back to keyword-based comment analysis.

## Output

### Console Output
```
✓ Report card processed for: Amin

📊 Extracted Metrics:
  - Attendance: 100.0%
  - Homework Score: 10/10
  - Classwork Score: 10/10
  - Class Focus: 77.5%
  - Exam Average: 77.9%
  - Skills:
    • Problem Solving: 8/10
    • Communication: 6/10
    • Discipline: 8/10

🏆 OVERALL RATING: 78.3/100
Performance Tier: EXCELLENT ⭐⭐

📈 Category Breakdown:
Attendance           [██████████████████████████████████████████████████] 100.0/100
Homework/Classwork   [██████████████████████████████████████████████████] 100.0/100
Class Focus          [███████████████████████████████████░░░░░░░░░░░░░░] 78.5/100
Exam                 [███████████████████████████████████████░░░░░░░░░░] 78.9/100 ⚠
Skills               [███████████████████████████████████░░░░░░░░░░░░░░] 73.3/100

⚠ Weakest Area: Exam (78.9/100)

📝 Recommendation: Practice exam strategy, time management, and answer organization.
```

### Saved Files
- **JSON Results**: `logs/analysis_<student>_<timestamp>.json`
- **AI Suggestions**: `logs/ai_suggestions_<student>_<timestamp>.txt`

## Examples

The `data/` directory contains example report cards:
- `amin.csv` - Student with excellent attendance, good exam performance
- `rina.csv` - Student with strong communication skills
- `jamil.csv` - Student with good English/Bangla skills

Test the system with:
```bash
python demo_report_card.py data/amin.csv
```

## Troubleshooting

### Error: "Missing required columns"
Ensure your CSV has all required columns: `attendance`, `HW_issue`, `CW_issue`, `daily_exam1_mark`, `daily_exam2_mark`

### Error: "Groq API initialization failed"
The system will automatically fall back to keyword-based analysis. For AI features, set your `GROQ_API_KEY` environment variable.

### Error: "File not found"
Check the file path. Use forward slashes (/) or escaped backslashes (\\\\) in paths.

## Advanced Features

### Batch Processing
Process multiple students:
```python
from src.csv_processor import CSVReportProcessor

processor = CSVReportProcessor()
results = processor.process_multiple_students([
    "data/amin.csv",
    "data/rina.csv",
    "data/jamil.csv"
])
```

### Custom Skill Analysis
Modify `CSVReportProcessor.analyze_comments_with_groq()` to adjust skill categories or scoring logic.

### Weight Adjustment
The rating model adapts weights based on feedback. Use the feedback feature in the app to improve accuracy over time.

## Next Steps

1. **Prepare your CSV files** with daily student records
2. **Set up Groq API** (optional) for enhanced comment analysis
3. **Run analysis** using app.py or demo script
4. **Review results** and improvement suggestions
5. **Provide feedback** to help the model learn and adapt

## Support

For issues or questions, check the main README.md or contact the development team.
