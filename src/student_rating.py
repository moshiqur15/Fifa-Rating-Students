"""
Student Rating System - Core Module
FIFA-style rating system for student performance
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple
import joblib
import os


class StudentRatingModel:
    """Core model for calculating student ratings"""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Default weights - can be adjusted through training
        self.weights = {
            "attendance": 0.2,
            "homework": 0.15,
            "classwork": 0.1,
            "class_focus": 0.15,
            "exam": 0.25,
            "skills": 0.15
        }
        
        # History for adaptive learning
        self.prediction_history = []
        self.performance_metrics = {
            "total_predictions": 0,
            "accuracy_scores": [],
            "feedback_count": 0
        }
    
    @staticmethod
    def normalize_1_100(val: float, vmin: float, vmax: float) -> float:
        """Map any value to 1-100 scale"""
        return np.clip(1.0 + 99.0 * (val - vmin) / (vmax - vmin + 1e-9), 1.0, 100.0)
    
    def compute_student_ratings(self, student: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate student ratings across multiple dimensions
        
        Args:
            student: Dictionary with student performance data
            
        Returns:
            Dictionary with overall rating and subcategory scores
        """
        # ---- Attendance ----
        att = student.get("attendance", 80)  # percentage
        r_att = self.normalize_1_100(att, 0, 100)
        
        # ---- Homework/Classwork ----
        hw = student.get("homework", 7)      # 1-10 scale
        cw = student.get("classwork", 7)     # 1-10 scale
        r_hw = self.normalize_1_100(hw, 1, 10)
        r_cw = self.normalize_1_100(cw, 1, 10)
        
        # ---- Class Focus ----
        focus = student.get("class_focus", 70)  # percentage
        r_focus = self.normalize_1_100(focus, 0, 100)
        
        # ---- Exam ----
        exam = student.get("exam", 65)  # percentage
        r_exam = self.normalize_1_100(exam, 0, 100)
        
        # ---- Skills ----
        skills = student.get("skills", {
            "problem_solving": 7,
            "communication": 7,
            "discipline": 7
        })
        r_skills = {k: self.normalize_1_100(v, 1, 10) for k, v in skills.items()}
        
        # ---- Overall rating ----
        overall = (
            r_att * self.weights["attendance"] +
            r_hw * self.weights["homework"] +
            r_cw * self.weights["classwork"] +
            r_focus * self.weights["class_focus"] +
            r_exam * self.weights["exam"] +
            np.mean(list(r_skills.values())) * self.weights["skills"]
        )
        
        result = {
            "overall_rating": round(overall, 2),
            "subcategories": {
                "Attendance": round(r_att, 2),
                "Homework": round(r_hw, 2),
                "Classwork": round(r_cw, 2),
                "Class Focus": round(r_focus, 2),
                "Exam": round(r_exam, 2),
                "Skills": {k: round(v, 2) for k, v in r_skills.items()}
            },
            "timestamp": datetime.now().isoformat(),
            "student_id": student.get("student_id", "unknown")
        }
        
        # Track prediction
        self.prediction_history.append(result)
        self.performance_metrics["total_predictions"] += 1
        
        return result
    
    def recommend_improvement(self, ratings_dict: Dict[str, Any]) -> Tuple[str, str, Dict[str, float]]:
        """
        Analyze ratings and recommend improvements
        
        Returns:
            Tuple of (weakest_category, recommendation, all_scores)
        """
        subcats = ratings_dict["subcategories"]
        
        # Find weakest main category
        main_scores = {
            "Attendance": subcats["Attendance"],
            "Homework/Classwork": (subcats["Homework"] + subcats["Classwork"]) / 2,
            "Class Focus": subcats["Class Focus"],
            "Exam": subcats["Exam"],
            "Skills": np.mean(list(subcats["Skills"].values()))
        }
        
        weakest = min(main_scores, key=main_scores.get)
        
        recommendations = {
            "Attendance": "Improve class presence; track absences and ensure punctuality.",
            "Homework/Classwork": "Submit homework & classwork on time; improve quality and consistency.",
            "Class Focus": "Increase concentration in class; use short quizzes and active participation.",
            "Exam": "Practice exam strategy, time management, and answer organization.",
            "Skills": "Enhance key skills through practice, presentations, and problem-solving drills."
        }
        
        return weakest, recommendations[weakest], main_scores
    
    def adapt_weights(self, feedback: Dict[str, Any]):
        """
        Adjust model weights based on feedback (adaptive learning)
        
        Args:
            feedback: Dictionary with actual performance vs predicted
        """
        # Simple adaptive learning - adjust weights based on error
        if "actual_rating" in feedback and "predicted_rating" in feedback:
            error = feedback["actual_rating"] - feedback["predicted_rating"]
            
            # Adjust weights slightly based on error direction
            adjustment = 0.01 * np.sign(error)
            
            if "weak_category" in feedback:
                category = feedback["weak_category"].lower()
                if category in self.weights:
                    # Increase weight for underperforming category
                    self.weights[category] = min(0.5, self.weights[category] + abs(adjustment))
                    # Normalize weights to sum to 1
                    total = sum(self.weights.values())
                    self.weights = {k: v / total for k, v in self.weights.items()}
            
            self.performance_metrics["feedback_count"] += 1
            self.performance_metrics["accuracy_scores"].append(abs(error))
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        avg_error = (
            np.mean(self.performance_metrics["accuracy_scores"])
            if self.performance_metrics["accuracy_scores"]
            else 0
        )
        
        return {
            "total_predictions": self.performance_metrics["total_predictions"],
            "feedback_count": self.performance_metrics["feedback_count"],
            "average_error": round(avg_error, 2),
            "current_weights": self.weights,
            "improvement_rate": self._calculate_improvement_rate()
        }
    
    def _calculate_improvement_rate(self) -> float:
        """Calculate if model is improving over time"""
        errors = self.performance_metrics["accuracy_scores"]
        if len(errors) < 2:
            return 0.0
        
        # Compare first half vs second half
        mid = len(errors) // 2
        first_half = np.mean(errors[:mid])
        second_half = np.mean(errors[mid:])
        
        if first_half == 0:
            return 0.0
        
        improvement = ((first_half - second_half) / first_half) * 100
        return round(improvement, 2)
    
    def save_model(self, filepath: str):
        """Save model weights and history"""
        model_data = {
            "weights": self.weights,
            "prediction_history": self.prediction_history,
            "performance_metrics": self.performance_metrics,
            "timestamp": datetime.now().isoformat()
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model weights and history"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.weights = model_data["weights"]
            self.prediction_history = model_data["prediction_history"]
            self.performance_metrics = model_data["performance_metrics"]
            print(f"Model loaded from {filepath}")
        else:
            print(f"No model found at {filepath}, using default weights")
