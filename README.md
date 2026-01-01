# 🎓 Student Rating System

## FIFA-Style Student Performance Analysis with AI-Powered Insights

**Version 2.1** - Streamlined Web Application

---

## 🚀 Quick Start (3 Steps!)

```powershell
# 1. Install dependencies
pip install -r requirements_webapp.txt

# 2. Run the application
python app.py

# 3. Visit http://localhost:8501
```

**That's it!** The app auto-opens in your browser. 🎉

---

## ✨ What's New in v2.1

### 📦 **Unified Web-Only Design**
- ✅ Single entry point: `python app.py`
- ✅ No more CLI confusion
- ✅ All features in beautiful web UI
- ✅ Auto-installs dependencies
- ✅ Uses pickle model from notebook

### 🔄 **New Features**
1. **Model Performance Dashboard** - View metrics, weights, export reports
2. **Sample CSV Creator** - Generate test data with custom parameters
3. **Enhanced File Scanner** - Auto-detects CSV files in data/ folder
4. **Pickle Model Integration** - Uses `student_scoring_model.pkl`

---

## 📋 Features Overview

| Feature | Description |
|---------|-------------|
| 📤 **Upload CSV** | Auto-scan data/ folder, dropdown selector, live preview |
| ✍️ **Manual Entry** | Interactive sliders for quick assessments |
| 📊 **Batch Analysis** | Compare multiple students, export rankings |
| 📈 **Visualizations** | Radar, bar, scatter charts with Plotly |
| 🤖 **AI Features** | Comment analysis, improvement plans (optional Groq API) |
| 📊 **Model Dashboard** | View performance, weights, export reports |
| 📝 **CSV Creator** | Generate sample data for testing |

---

## 📂 Files & Directories

```
📁 Project Root
├── app.py                        ⭐ Main launcher (run this!)
├── create_scoring_model_pkl.py   # Update scoring model
├── create_prediction_model_pkl.py # Update prediction model
├── create_improvement_model_pkl.py # Update improvement model
├── requirements_webapp.txt       # Dependencies
├── SYSTEM_ARCHITECTURE.md        ⭐ Full system documentation
│
├── 📁 models/
│   ├── student_scoring_model.pkl ⭐ From notebook
│   ├── student_rating_model.pkl  # FIFA rating model
│   ├── student_prediction_model.pkl # Prediction model
│   └── student_improvement_model.pkl # Improvement model
│
├── 📁 data/                      # Auto-scanned!
│   ├── amin.csv                  # 23 records
│   ├── rina.csv                  # 20 records  
│   └── jamil.csv                 # 25 records
│
├── 📁 src/
│   ├── csv_processor.py          # Uses pickle model
│   ├── student_rating.py         # Rating engine
│   ├── scoring_model.py          # Scoring logic
│   ├── prediction_model.py       # Prediction ML
│   ├── improvement_model.py      # Improvement AI
│   ├── groq_client.py            # AI client
│   └── data_input.py             # Utilities
│
└── 📁 logs/ (auto-created)
    ├── analysis_*.json
    └── ai_suggestions_*.txt
```

---

## 🎯 How to Use

### **Upload Mode** (Recommended)

1. Run `python app.py`
2. Sidebar shows: "📂 4 CSV file(s) available"
3. Select file from dropdown (e.g., amin.csv)
4. Preview appears automatically
5. Click "🔍 Analyze Selected File"
6. View results with charts!

### **Manual Entry** (Quick Assessment)

1. Select "Manual Entry" mode
2. Use sliders to set values
3. Click "Analyze"
4. Instant results!

### **Batch Analysis** (Compare Students)

1. Select "Batch Analysis"
2. Check students to compare
3. Click "Analyze Selected Students"
4. View rankings and charts
5. Download CSV report

### **Model Performance**

1. Sidebar → "ℹ️ Model Information"
2. Click "📊 View Full Performance"
3. See weights, metrics, trends
4. Export model report

### **Create Sample CSV**

1. Sidebar → "🛠️ Utilities"
2. Click "📝 Create Sample CSV"
3. Adjust parameters
4. Generate and download

---

## 📝 CSV Format (Required Columns)

```csv
date,attendance,HW_issue,CW_issue,daily_exam1_mark,daily_exam2_mark,teacher_comment
2025-01-01,Present,False,False,8,7,"Good work today"
2025-01-02,Present,False,False,7,8,"Shows improvement"
```

| Column | Type | Example |
|--------|------|---------|
| attendance | Text | Present/Absent |
| HW_issue | Boolean | False |
| CW_issue | Boolean | False |
| daily_exam1_mark | Number (0-10) | 8 |
| daily_exam2_mark | Number (0-10) | 7 |
| teacher_comment | Text | "Good work" |

---

## ⚙️ Optional: AI Features

For AI-powered comment analysis and improvement plans:

```powershell
# Get API key from https://console.groq.com
$env:GROQ_API_KEY = "your_api_key_here"
python app.py
```

Without API: Keyword-based analysis (still great!)

---

## 🔄 Updating Models After Notebook Edits

When you edit the Jupyter notebooks to improve model logic:

```powershell
# 1. Edit your notebook (e.g., student_scoring_model.ipynb)
# 2. Export changes to corresponding src/*.py file

# 3. Update the pickle files:
python create_scoring_model_pkl.py
python create_prediction_model_pkl.py
python create_improvement_model_pkl.py

# 4. Restart the webapp
python app.py
```

**Features:**
- ✅ Automatically detects existing models
- ✅ Creates timestamped backups before updating
- ✅ Verifies new models load correctly
- ✅ Shows version info and file sizes

---

## 📊 Rating Tiers

| Score | Tier | Stars |
|-------|------|-------|
| 85-100 | ELITE | ⭐⭐⭐ |
| 75-84 | EXCELLENT | ⭐⭐ |
| 65-74 | GOOD | ⭐ |
| 50-64 | DEVELOPING | - |
| 0-49 | NEEDS IMPROVEMENT | ⚠️ |

---

## 🔧 Troubleshooting

**Module not found?**
```powershell
pip install -r requirements_webapp.txt
```

**Port in use?**
```powershell
streamlit run webapp.py --server.port 8502
```

**Files not showing?**
- Check they're in `data/` folder
- Ensure `.csv` extension
- Click "🔄 Refresh Files"

---

## 💡 Pro Tips

- 📂 **Auto-scan works!** Just drop CSV in data/ folder
- 🎯 **Start with samples** Try data/amin.csv first
- 🔄 **Batch mode rocks** Compare multiple students easily
- 💬 **Give feedback** Helps model learn
- 📥 **Export everything** Keep records as JSON/CSV

---

## 📚 More Documentation

- **FEATURES_SUMMARY.md** 🎉 - Complete features list & user guide (NEW!)
- **SYSTEM_ARCHITECTURE.md** ⭐ - Complete system architecture & technical documentation
- **WEBAPP_GUIDE.md** - Detailed features guide
- **REPORT_CARD_GUIDE.md** - CSV format details  
- **QUICK_REFERENCE.txt** - One-page cheat sheet
- **README_COMPLETE.md** - Full technical docs

---

## 🎉 Ready to Go!

```powershell
# That's all you need:
python app.py

# Opens at http://localhost:8501
# Try data/amin.csv
# Enjoy the beautiful UI! ✨
```

---

**Built with ❤️ for better education**  
**v2.1 - Web-First Design** | Production Ready ✅
