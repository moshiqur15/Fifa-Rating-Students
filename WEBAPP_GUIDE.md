# Student Rating System - Web Application Guide

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
   ```powershell
   pip install -r requirements_webapp.txt
   ```

2. **Run the web app:**
   
   **Option A - Using PowerShell script (Recommended):**
   ```powershell
   .\run_webapp.ps1
   ```
   
   **Option B - Using batch file:**
   ```cmd
   run_webapp.bat
   ```
   
   **Option C - Direct command:**
   ```powershell
   streamlit run webapp.py
   ```

3. **Access the app:**
   - Opens automatically in your browser
   - Or navigate to: http://localhost:8501

## 📋 Features

### 1. Upload Report Card CSV
Upload CSV files with daily student records for instant analysis with AI-powered insights.

### 2. Manual Entry
Input student data directly using interactive sliders and forms.

### 3. Batch Analysis
Analyze multiple students at once and compare performance with visualizations.

## 🎯 Example Usage

```powershell
# Quick start
.\run_webapp.ps1

# Visit http://localhost:8501

# Try uploading data/amin.csv
# Or enter data manually
# See results with beautiful visualizations!
```

## ⚙️ Groq API Setup (Optional)

For AI-powered features:

```powershell
$env:GROQ_API_KEY = "your_api_key_here"
.\run_webapp.ps1
```

## 📊 What You Get

- **FIFA-Style Ratings** (1-100 scale with tiers)
- **Interactive Visualizations** (Radar charts, bar charts, scatter plots)
- **AI Improvement Plans** (Personalized recommendations)
- **Batch Comparisons** (Rank multiple students)
- **Export Results** (JSON and CSV downloads)
- **Model Feedback** (Help improve accuracy over time)

## 🎨 Interface

- **Sidebar:** Select analysis mode and view status
- **Main Area:** Upload, enter, or select data
- **Results:** Beautiful charts and detailed breakdowns
- **AI Section:** Generate improvement plans and strengths analysis

## 📂 Sample CSV Format

```csv
date,attendance,HW_issue,CW_issue,daily_exam1_mark,daily_exam2_mark,teacher_comment
2025-12-01,Present,False,False,8,7,"Good participation"
2025-12-02,Present,False,False,7,8,"Improving steadily"
```

See `data/amin.csv` for complete example.

## 🔧 Troubleshooting

**Module not found?**
```powershell
pip install -r requirements_webapp.txt
```

**Port in use?**
```powershell
streamlit run webapp.py --server.port 8502
```

**AI not working?**
Set GROQ_API_KEY environment variable (see Configuration section)

## 📚 Documentation

- **WEBAPP_GUIDE.md** - This file (complete guide)
- **REPORT_CARD_GUIDE.md** - CSV format details
- **QUICKSTART_REPORT_CARDS.md** - Quick reference

## 🎉 Enjoy!

Start analyzing student performance with modern web interface and AI-powered insights! 🚀
