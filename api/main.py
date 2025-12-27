"""
FastAPI Backend for Student Rating System
Modern REST API with beautiful web interface
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from student_rating import StudentRatingModel
from data_input import StudentDataInput
from groq_client import GroqSuggestionGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Student Rating System",
    description="FIFA-style student performance analysis with AI-powered insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), '..', 'static')
os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Initialize model
model = StudentRatingModel()
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'student_rating_model.pkl')
if os.path.exists(model_path):
    model.load_model(model_path)

# Try to initialize Groq
try:
    groq_client = GroqSuggestionGenerator()
    groq_available = True
except:
    groq_client = None
    groq_available = False


# Pydantic models for request/response
class StudentInput(BaseModel):
    student_id: str
    attendance: float
    homework: float
    classwork: float
    class_focus: float
    exam: float
    problem_solving: float
    communication: float
    discipline: float


class FeedbackInput(BaseModel):
    student_id: str
    predicted_rating: float
    actual_rating: float
    weak_category: Optional[str] = None


class AnalysisResponse(BaseModel):
    success: bool
    student_id: str
    overall_rating: float
    tier: str
    subcategories: Dict[str, Any]
    weak_category: str
    recommendation: str
    all_scores: Dict[str, float]
    ai_suggestions: Optional[str] = None
    timestamp: str


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Student Rating System</h1><p>Frontend not found. Please check static/index.html</p>"


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "groq_available": groq_available,
        "model_loaded": True,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_student(student: StudentInput):
    """Analyze a single student"""
    try:
        # Prepare student data
        student_data = {
            "student_id": student.student_id,
            "attendance": student.attendance,
            "homework": student.homework,
            "classwork": student.classwork,
            "class_focus": student.class_focus,
            "exam": student.exam,
            "skills": {
                "problem_solving": student.problem_solving,
                "communication": student.communication,
                "discipline": student.discipline
            }
        }
        
        # Calculate ratings
        ratings = model.compute_student_ratings(student_data)
        
        # Get recommendations
        weak_category, recommendation, all_scores = model.recommend_improvement(ratings)
        
        # Determine tier
        overall = ratings["overall_rating"]
        if overall >= 85:
            tier = "ELITE ⭐⭐⭐"
        elif overall >= 75:
            tier = "EXCELLENT ⭐⭐"
        elif overall >= 65:
            tier = "GOOD ⭐"
        elif overall >= 50:
            tier = "DEVELOPING"
        else:
            tier = "NEEDS IMPROVEMENT"
        
        # Generate AI suggestions if available
        ai_suggestions = None
        if groq_available and groq_client:
            try:
                ai_suggestions = groq_client.generate_improvement_plan(
                    student.student_id, ratings, weak_category, recommendation, all_scores
                )
            except Exception as e:
                print(f"Groq API error: {e}")
        
        # Save model
        model.save_model(model_path)
        
        return AnalysisResponse(
            success=True,
            student_id=student.student_id,
            overall_rating=ratings["overall_rating"],
            tier=tier,
            subcategories=ratings["subcategories"],
            weak_category=weak_category,
            recommendation=recommendation,
            all_scores=all_scores,
            ai_suggestions=ai_suggestions,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackInput):
    """Submit feedback for model improvement"""
    try:
        feedback_data = {
            "actual_rating": feedback.actual_rating,
            "predicted_rating": feedback.predicted_rating,
            "weak_category": feedback.weak_category
        }
        
        model.adapt_weights(feedback_data)
        model.save_model(model_path)
        
        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance")
async def get_performance():
    """Get model performance metrics"""
    try:
        metrics = model.get_model_performance()
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and analyze CSV file"""
    try:
        # Save uploaded file temporarily
        temp_path = f"data/temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Read students from CSV
        students = StudentDataInput.read_from_csv(temp_path)
        
        if not students:
            raise HTTPException(status_code=400, detail="No valid students found in CSV")
        
        # Analyze all students
        results = []
        for student in students:
            ratings = model.compute_student_ratings(student)
            weak_category, recommendation, all_scores = model.recommend_improvement(ratings)
            
            results.append({
                "student_id": student["student_id"],
                "overall_rating": ratings["overall_rating"],
                "weak_category": weak_category,
                "all_scores": all_scores
            })
        
        # Save model
        model.save_model(model_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "success": True,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
