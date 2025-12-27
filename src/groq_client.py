"""
Groq API Integration
Generate detailed improvement suggestions using Groq LLM
"""

from groq import Groq
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqSuggestionGenerator:
    """Generate detailed improvement suggestions using Groq API"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (if not provided, reads from environment)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Please set GROQ_API_KEY environment variable "
                "or pass it to the constructor."
            )
        
        self.client = Groq(api_key=self.api_key)
    
    def generate_improvement_plan(
        self,
        student_id: str,
        ratings: Dict[str, Any],
        weak_category: str,
        recommendation: str,
        all_scores: Dict[str, float]
    ) -> str:
        """
        Generate detailed improvement plan using Groq
        
        Args:
            student_id: Student identifier
            ratings: Full rating dictionary
            weak_category: Weakest performance category
            recommendation: Basic recommendation text
            all_scores: All category scores
            
        Returns:
            Detailed improvement plan as text
        """
        
        # Build context for the LLM
        overall_rating = ratings["overall_rating"]
        subcats = ratings["subcategories"]
        
        prompt = f"""You are an educational consultant AI. Analyze this student's performance and create a detailed, actionable improvement plan.

STUDENT ID: {student_id}
OVERALL RATING: {overall_rating}/100

PERFORMANCE BREAKDOWN:
- Attendance: {subcats['Attendance']}/100
- Homework: {subcats['Homework']}/100
- Classwork: {subcats['Classwork']}/100
- Class Focus: {subcats['Class Focus']}/100
- Exam: {subcats['Exam']}/100
- Skills:
  * Problem Solving: {subcats['Skills'].get('problem_solving', 'N/A')}/100
  * Communication: {subcats['Skills'].get('communication', 'N/A')}/100
  * Discipline: {subcats['Skills'].get('discipline', 'N/A')}/100

WEAKEST AREA: {weak_category} ({all_scores.get(weak_category, 0):.2f}/100)
BASIC RECOMMENDATION: {recommendation}

Please create a comprehensive improvement plan with:
1. **Immediate Actions** (Week 1-2): Specific steps to take right away
2. **Short-term Goals** (Month 1): Measurable objectives for the first month
3. **Medium-term Strategy** (Months 2-3): Sustained improvement approach
4. **Long-term Development** (3+ months): Building lasting habits
5. **Success Metrics**: How to measure progress
6. **Additional Resources**: Tools, techniques, or resources that can help

Focus especially on the weakest area ({weak_category}) but provide a holistic approach.
Be specific, actionable, and encouraging. Format with clear sections and bullet points.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768"
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational consultant who creates detailed, actionable improvement plans for students."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            improvement_plan = response.choices[0].message.content
            return improvement_plan
            
        except Exception as e:
            return f"Error generating improvement plan: {str(e)}\n\nBasic Recommendation: {recommendation}"
    
    def generate_strengths_analysis(
        self,
        student_id: str,
        ratings: Dict[str, Any]
    ) -> str:
        """
        Generate analysis of student's strengths
        
        Args:
            student_id: Student identifier
            ratings: Full rating dictionary
            
        Returns:
            Strengths analysis as text
        """
        subcats = ratings["subcategories"]
        overall = ratings["overall_rating"]
        
        prompt = f"""Analyze this student's strengths and provide encouragement.

STUDENT ID: {student_id}
OVERALL RATING: {overall}/100

SCORES:
- Attendance: {subcats['Attendance']}/100
- Homework: {subcats['Homework']}/100
- Classwork: {subcats['Classwork']}/100
- Class Focus: {subcats['Class Focus']}/100
- Exam: {subcats['Exam']}/100
- Skills: {subcats['Skills']}

Identify the top 3 strengths and explain how they can leverage these strengths to improve weaker areas.
Be specific and encouraging. Keep it under 200 words.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a supportive educational coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating strengths analysis: {str(e)}"
    
    def generate_teacher_recommendations(
        self,
        student_id: str,
        ratings: Dict[str, Any],
        weak_category: str
    ) -> str:
        """
        Generate recommendations for teachers/educators
        
        Args:
            student_id: Student identifier
            ratings: Full rating dictionary
            weak_category: Weakest performance category
            
        Returns:
            Teacher recommendations as text
        """
        overall = ratings["overall_rating"]
        subcats = ratings["subcategories"]
        
        prompt = f"""As an educational expert, provide recommendations for teachers/educators working with this student.

STUDENT: {student_id}
OVERALL RATING: {overall}/100
WEAKEST AREA: {weak_category}

PERFORMANCE DATA:
{subcats}

Provide:
1. Teaching strategies tailored to this student
2. Classroom interventions
3. Ways to provide targeted support
4. Communication tips for parent/teacher conferences

Keep it practical and actionable for educators. About 150-200 words.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an educational consultant advising teachers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating teacher recommendations: {str(e)}"
