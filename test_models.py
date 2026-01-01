"""
Quick test script to verify all models work correctly
"""

import sys
import os
sys.path.insert(0, 'src')

from student_rating import StudentRatingModel
from improvement_model import StudentImprovementModel
from prediction_model import StudentPredictionModel

print("=" * 60)
print("Testing Student Rating System Models")
print("=" * 60)
print()

# Sample student data
student_data = {
    "student_id": "test_student",
    "attendance": 85.5,
    "homework": 7,
    "classwork": 8,
    "class_focus": 75.3,
    "exam": 72.5,
    "skills": {
        "problem_solving": 7,
        "communication": 8,
        "discipline": 9
    }
}

# Test Rating Model
print("1. Testing Rating Model...")
try:
    rating_model = StudentRatingModel()
    ratings = rating_model.compute_student_ratings(student_data)
    weak_category, recommendation, all_scores = rating_model.recommend_improvement(ratings)
    print(f"   ✓ Overall Rating: {ratings['overall_rating']:.1f}/100")
    print(f"   ✓ Weak Category: {weak_category}")
    print()
except Exception as e:
    print(f"   ✗ Error: {e}")
    print()

# Test Improvement Model
print("2. Testing Improvement Model...")
try:
    improvement_model = StudentImprovementModel()
    
    improvement_plan = improvement_model.create_improvement_plan(
        student_data=student_data,
        rating_recommendation=recommendation,
        teacher_suggestion="Focus on exam preparation and time management.",
        weak_category=weak_category,
        num_tasks=3
    )
    
    print(f"   ✓ Generated {len(improvement_plan['tasks'])} tasks")
    print(f"   ✓ Strategy: {improvement_plan['merged_strategy']['merged_strategy'][:60]}...")
    print(f"   ✓ Source: {improvement_plan['merged_strategy']['source']}")
    print()
except Exception as e:
    print(f"   ✗ Error: {e}")
    print()

# Test Prediction Model
print("3. Testing Prediction Model...")
try:
    prediction_model = StudentPredictionModel()
    
    sample_tasks = [
        {"xp": 30, "time_estimate_minutes": 45},
        {"xp": 40, "time_estimate_minutes": 60},
        {"xp": 25, "time_estimate_minutes": 30},
    ]
    
    predictions = prediction_model.predict_improvement(
        student_data=student_data,
        tasks=sample_tasks
    )
    
    summary = predictions['summary']
    print(f"   ✓ Improvement Probability: {summary['overall_improvement_probability']}%")
    print(f"   ✓ Average Mark Increase: +{summary['average_predicted_increase']}")
    print(f"   ✓ Best Timeline: {summary['best_timeline']}")
    print()
except Exception as e:
    print(f"   ✗ Error: {e}")
    print()

print("=" * 60)
print("All tests completed!")
print()
print("Tips:")
print("- Set GROQ_API_KEY environment variable for AI-powered features")
print("- Run 'python app.py' to start the web application")
print("=" * 60)
