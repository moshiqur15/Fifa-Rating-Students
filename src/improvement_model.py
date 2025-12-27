"""
Student Improvement Model
Merges AI suggestions from rating model with teacher feedback using Groq API
Generates specific, actionable task lists for student improvement
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from groq import Groq


class StudentImprovementModel:
    """
    Improvement model that:
    1. Takes suggestions from student_rating_model
    2. Takes teacher suggestions
    3. Uses Groq AI to merge and create best recommendations
    4. Generates specific, actionable task lists
    """
    
    def __init__(self):
        self.model_version = "1.0"
        self.created_date = "2025-12-09"
        
        # Initialize Groq client
        self.groq_client = None
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                print("[OK] Groq API connected for improvement suggestions")
            except Exception as e:
                print(f"[WARN] Groq API initialization failed: {e}")
        
        # Track improvement history
        self.improvement_history = []
    
    def merge_suggestions_with_groq(
        self,
        rating_recommendation: str,
        teacher_suggestion: str,
        student_data: Dict[str, Any],
        weak_category: str
    ) -> Dict[str, Any]:
        """
        Use Groq AI to intelligently merge rating model recommendations
        with teacher suggestions into a comprehensive improvement plan.
        
        Args:
            rating_recommendation: Suggestion from student_rating_model
            teacher_suggestion: Teacher's input/feedback
            student_data: Full student performance data
            weak_category: Weakest performance category
            
        Returns:
            Dictionary with merged suggestion and analysis
        """
        if not self.groq_client:
            # Fallback: Simple merge without AI
            return self._fallback_merge(
                rating_recommendation,
                teacher_suggestion,
                weak_category
            )
        
        try:
            # Prepare context for Groq
            student_context = self._prepare_student_context(student_data)
            
            prompt = f"""You are an expert educational advisor. Analyze and merge two improvement suggestions for a student.

STUDENT PERFORMANCE DATA:
{student_context}

WEAKEST AREA: {weak_category}

AI MODEL RECOMMENDATION:
{rating_recommendation}

TEACHER SUGGESTION:
{teacher_suggestion}

TASK:
1. Analyze both suggestions and identify the most critical improvements
2. Create a unified, specific improvement strategy that combines the best of both
3. Prioritize based on the student's weakest area ({weak_category})
4. Make the strategy actionable and measurable

Respond in JSON format with these fields:
{{
  "merged_strategy": "The unified improvement strategy (2-3 sentences)",
  "key_focus_areas": ["area1", "area2", "area3"],
  "reasoning": "Why this approach will work for this student",
  "priority_level": "High/Medium/Low"
}}
"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational advisor who creates personalized improvement strategies. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse Groq response
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            return {
                "merged_strategy": result.get("merged_strategy", ""),
                "key_focus_areas": result.get("key_focus_areas", []),
                "reasoning": result.get("reasoning", ""),
                "priority_level": result.get("priority_level", "Medium"),
                "source": "groq_ai"
            }
            
        except Exception as e:
            print(f"[WARN] Groq merge failed: {e}")
            return self._fallback_merge(
                rating_recommendation,
                teacher_suggestion,
                weak_category
            )
    
    def _fallback_merge(
        self,
        rating_recommendation: str,
        teacher_suggestion: str,
        weak_category: str
    ) -> Dict[str, Any]:
        """Fallback merge without AI"""
        merged = f"{rating_recommendation} Additionally, {teacher_suggestion}"
        
        return {
            "merged_strategy": merged,
            "key_focus_areas": [weak_category, "Consistency", "Practice"],
            "reasoning": "Combined model and teacher suggestions",
            "priority_level": "High",
            "source": "fallback"
        }
    
    def _prepare_student_context(self, student_data: Dict[str, Any]) -> str:
        """Format student data for Groq context"""
        context = f"""
Student ID: {student_data.get('student_id', 'N/A')}
Attendance: {student_data.get('attendance', 'N/A')}%
Homework Score: {student_data.get('homework', 'N/A')}/10
Classwork Score: {student_data.get('classwork', 'N/A')}/10
Class Focus: {student_data.get('class_focus', 'N/A')}%
Exam Score: {student_data.get('exam', 'N/A')}%
Skills: {json.dumps(student_data.get('skills', {}), indent=2)}
"""
        return context.strip()
    
    def generate_task_list_with_groq(
        self,
        merged_strategy: Dict[str, Any],
        student_data: Dict[str, Any],
        num_tasks: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Use Groq AI to generate specific, actionable tasks based on the merged strategy.
        Tasks are reusable for students with similar issues.
        
        Args:
            merged_strategy: The merged improvement strategy
            student_data: Student performance data
            num_tasks: Number of tasks to generate
            
        Returns:
            List of task dictionaries with details
        """
        if not self.groq_client:
            return self._fallback_task_list(merged_strategy, num_tasks)
        
        try:
            weak_area = self._identify_weakest_area(student_data)
            
            prompt = f"""You are creating a personalized improvement plan for a student.

IMPROVEMENT STRATEGY:
{merged_strategy['merged_strategy']}

KEY FOCUS AREAS:
{', '.join(merged_strategy['key_focus_areas'])}

WEAKEST AREA: {weak_area}

TASK:
Generate {num_tasks} specific, actionable tasks for the student. Each task should:
1. Be clear and measurable
2. Target the key focus areas
3. Be achievable within 1-2 weeks
4. Be reusable for other students with similar issues
5. Include an estimated time commitment
6. Have a difficulty level (Easy/Medium/Hard)

Respond in JSON format:
{{
  "tasks": [
    {{
      "task_id": 1,
      "title": "Task title",
      "description": "Detailed description",
      "category": "Which focus area it addresses",
      "time_estimate": "e.g., 30 minutes daily",
      "difficulty": "Easy/Medium/Hard",
      "expected_impact": "What improvement to expect",
      "reusable_for": "Description of similar student profiles"
    }}
  ]
}}
"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational task planner. Create specific, actionable tasks. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            tasks = result.get("tasks", [])
            
            # Add metadata
            for task in tasks:
                task["created_date"] = datetime.now().isoformat()
                task["status"] = "pending"
            
            return tasks
            
        except Exception as e:
            print(f"[WARN] Groq task generation failed: {e}")
            return self._fallback_task_list(merged_strategy, num_tasks)
    
    def _fallback_task_list(
        self,
        merged_strategy: Dict[str, Any],
        num_tasks: int
    ) -> List[Dict[str, Any]]:
        """Generate basic task list without AI"""
        focus_areas = merged_strategy.get('key_focus_areas', ['General'])
        
        tasks = []
        for i in range(num_tasks):
            area = focus_areas[i % len(focus_areas)]
            tasks.append({
                "task_id": i + 1,
                "title": f"Improve {area}",
                "description": merged_strategy['merged_strategy'],
                "category": area,
                "time_estimate": "30 minutes daily",
                "difficulty": "Medium",
                "expected_impact": "Gradual improvement in this area",
                "reusable_for": f"Students struggling with {area}",
                "created_date": datetime.now().isoformat(),
                "status": "pending"
            })
        
        return tasks
    
    def _identify_weakest_area(self, student_data: Dict[str, Any]) -> str:
        """Identify the weakest performance area"""
        scores = {
            "Attendance": student_data.get("attendance", 80),
            "Homework": student_data.get("homework", 7) * 10,
            "Classwork": student_data.get("classwork", 7) * 10,
            "Class Focus": student_data.get("class_focus", 70),
            "Exam": student_data.get("exam", 65)
        }
        
        return min(scores, key=scores.get)
    
    def create_improvement_plan(
        self,
        student_data: Dict[str, Any],
        rating_recommendation: str,
        teacher_suggestion: str,
        weak_category: str,
        num_tasks: int = 5
    ) -> Dict[str, Any]:
        """
        Complete improvement plan pipeline:
        1. Merge suggestions using Groq AI
        2. Generate specific task list
        3. Package everything for delivery
        
        Args:
            student_data: Student performance data
            rating_recommendation: AI model suggestion
            teacher_suggestion: Teacher input
            weak_category: Weakest area
            num_tasks: Number of tasks to generate
            
        Returns:
            Complete improvement plan
        """
        # Step 1: Merge suggestions
        merged_strategy = self.merge_suggestions_with_groq(
            rating_recommendation,
            teacher_suggestion,
            student_data,
            weak_category
        )
        
        # Step 2: Generate task list
        tasks = self.generate_task_list_with_groq(
            merged_strategy,
            student_data,
            num_tasks
        )
        
        # Step 3: Create complete plan
        improvement_plan = {
            "student_id": student_data.get("student_id", "unknown"),
            "generated_date": datetime.now().isoformat(),
            "weak_category": weak_category,
            "merged_strategy": merged_strategy,
            "tasks": tasks,
            "original_suggestions": {
                "rating_model": rating_recommendation,
                "teacher": teacher_suggestion
            },
            "model_version": self.model_version
        }
        
        # Track history
        self.improvement_history.append({
            "student_id": student_data.get("student_id"),
            "date": datetime.now().isoformat(),
            "weak_category": weak_category,
            "num_tasks": len(tasks)
        })
        
        return improvement_plan
    
    def get_reusable_tasks_for_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get previously generated tasks that are reusable for a specific category.
        Useful for students with similar issues.
        
        Args:
            category: The performance category (e.g., "Attendance", "Exam")
            
        Returns:
            List of reusable tasks for that category
        """
        reusable = []
        for plan in self.improvement_history:
            if plan.get("weak_category") == category:
                # In a real system, this would query a database
                # For now, return placeholder
                reusable.append({
                    "note": f"Tasks for {category} from previous students",
                    "available": True
                })
        
        return reusable
