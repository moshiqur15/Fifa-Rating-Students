"""
CSV Report Card Processor
Processes student CSV report cards and extracts performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import os
import pickle
import sys
from groq import Groq


class CSVReportProcessor:
    """Process student CSV report cards and analyze with Groq API"""
    
    def __init__(self):
        """Initialize processor with scoring model and optional Groq API client"""
        self.groq_client = None
        self.scoring_model = None
        
        # Load the scoring model from pickle
        try:
            # Import the class definition before loading pickle
            # Add src to path if needed
            src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            from scoring_model import StudentScoringModel
            
            model_path = "models/student_scoring_model.pkl"
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.scoring_model = pickle.load(f)
                print(f"[OK] Scoring model loaded (v{self.scoring_model.model_version})")
        except Exception as e:
            print(f"[WARN] Could not load scoring model: {e}")
            print("  Will use built-in methods")
        
        # Try to initialize Groq client
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                print("[OK] Groq API connected for comment analysis")
            except Exception as e:
                print(f"[WARN] Groq API initialization failed: {e}")
                print("  Will use keyword-based analysis instead")
    
    def compute_attendance(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Compute attendance % for each student.
        Expects multiple rows per student with 'attendance' column.
        """
        def att_percent(group):
            total_days = len(group)
            present_days = (group['attendance'].str.lower() == 'present').sum()
            return (present_days / total_days) * 100 if total_days > 0 else 0

        return df.groupby('student', group_keys=False).apply(att_percent, include_groups=False).to_dict()

    def compute_hw_cw_score(self, df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
        """
        Compute homework and classwork scores (1-10) per student.
        Expects boolean columns 'HW_issue' and 'CW_issue'.
        True = Issue (so lower score), False = Done (high score)
        """
        scores = {}
        for student, group in df.groupby('student'):
            hw_done_ratio = (~group['HW_issue']).mean()  # ratio of homework done
            cw_done_ratio = (~group['CW_issue']).mean()
            hw_score = int(round(1 + hw_done_ratio*9))
            cw_score = int(round(1 + cw_done_ratio*9))
            scores[student] = {'homework': hw_score, 'classwork': cw_score}
        return scores

    def compute_exam_score(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Compute exam score (percentage) per student based on daily exams.
        Columns: daily_exam1_mark, daily_exam2_mark (out of 10)
        """
        scores = {}
        for student, group in df.groupby('student'):
            # Average of all exam marks, convert to percentage
            avg_score = group[['daily_exam1_mark','daily_exam2_mark']].mean().mean()
            # Assuming marks are out of 10, convert to percentage
            scores[student] = (avg_score / 10) * 100
        return scores

    def compute_class_focus(self, attendance_dict: Dict[str, float], 
                          hwcw_scores: Dict[str, Dict[str, int]], 
                          exam_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Compute class focus % as weighted average:
        45% exam, 25% attendance, 15% HW, 15% CW
        """
        cf = {}
        for student in attendance_dict.keys():
            att = attendance_dict[student]
            hw = hwcw_scores[student]['homework'] / 10 * 100
            cw = hwcw_scores[student]['classwork'] / 10 * 100
            exam = exam_scores[student]
            cf[student] = 0.45*exam + 0.25*att + 0.15*hw + 0.15*cw
        return cf

    def infer_skills_from_comments_keyword(self, comments: Dict[str, str]) -> Dict[str, Dict[str, int]]:
        """
        Keyword-based skill extraction from teacher comments.
        Returns scores 1-10 for each skill.
        """
        skills_dict = {}
        for student, comment in comments.items():
            text = str(comment).lower()
            
            # Problem solving
            problem_keys = ["math", "science", "logical", "problem", "solve", "reason"]
            problem = sum(k in text for k in problem_keys)
            
            # Communication
            comm_keys = ["communication", "speak", "english", "bangla", "write", "express"]
            communication = sum(k in text for k in comm_keys)
            
            # Discipline
            disc_keys = ["regular", "punctual", "attendance", "disciplined", "homework"]
            discipline = sum(k in text for k in disc_keys)

            # Scale counts to 1-10
            def scale_count(n):
                return min(max(1, n*2), 10)  # simple scale

            skills_dict[student] = {
                'problem_solving': scale_count(problem),
                'communication': scale_count(communication),
                'discipline': scale_count(discipline)
            }
        return skills_dict
    
    def analyze_comments_with_groq(self, student_name: str, comments: str) -> Dict[str, int]:
        """
        Use Groq API to analyze teacher comments and extract skill scores.
        Returns scores 1-10 for problem_solving, communication, and discipline.
        """
        if not self.groq_client:
            # Fallback to keyword-based analysis
            return self.infer_skills_from_comments_keyword({student_name: comments})[student_name]
        
        try:
            # Combine all comments into single text
            full_comments = comments if isinstance(comments, str) else " ".join(comments)
            
            prompt = f"""Analyze the following teacher comments for student {student_name} and rate their skills on a scale of 1-10.

Teacher Comments: {full_comments}

Based on these comments, provide scores (1-10, where 10 is excellent) for:
1. Problem Solving: Ability to solve math, science, logical reasoning problems
2. Communication: English/Bangla speaking, writing, expression skills
3. Discipline: Punctuality, attendance, homework completion, behavior

Respond ONLY with three numbers separated by commas: problem_solving,communication,discipline
Example: 7,8,6
"""
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an educational assessment expert. Analyze teacher comments and provide skill scores."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            scores = [int(x.strip()) for x in result.split(',')]
            
            return {
                'problem_solving': min(max(1, scores[0]), 10),
                'communication': min(max(1, scores[1]), 10),
                'discipline': min(max(1, scores[2]), 10)
            }
            
        except Exception as e:
            print(f"[WARN] Groq API analysis failed: {e}")
            print("  Falling back to keyword-based analysis")
            return self.infer_skills_from_comments_keyword({student_name: comments})[student_name]

    def process_student_csv(self, filepath: str, student_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a single student CSV report card.
        
        Args:
            filepath: Path to the CSV file
            student_name: Optional student name (if not in CSV, will be extracted from filename)
            
        Returns:
            Dictionary with processed student data ready for rating model
        """
        # Read CSV
        df = pd.read_csv(filepath)
        
        # Extract student name
        if student_name is None:
            # Try to get from filename
            student_name = os.path.splitext(os.path.basename(filepath))[0].capitalize()
        
        # Add student column if not present
        if 'student' not in df.columns:
            df['student'] = student_name
        
        # Validate required columns
        required_cols = ['attendance', 'HW_issue', 'CW_issue', 
                        'daily_exam1_mark', 'daily_exam2_mark']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Convert boolean columns
        df['HW_issue'] = df['HW_issue'].astype(bool)
        df['CW_issue'] = df['CW_issue'].astype(bool)
        
        # Compute metrics
        attendance = self.compute_attendance(df)
        hwcw = self.compute_hw_cw_score(df)
        exams = self.compute_exam_score(df)
        class_focus = self.compute_class_focus(attendance, hwcw, exams)
        
        # Process teacher comments
        if 'teacher_comment' in df.columns:
            # Combine all comments
            all_comments = " ".join(df['teacher_comment'].dropna().astype(str))
            skills = self.analyze_comments_with_groq(student_name, all_comments)
        else:
            # Default skills
            skills = {'problem_solving': 5, 'communication': 5, 'discipline': 5}
        
        # Compile final result for the student
        result = {
            "student_id": student_name,
            "attendance": round(attendance[student_name], 2),
            "homework": hwcw[student_name]['homework'],
            "classwork": hwcw[student_name]['classwork'],
            "class_focus": round(class_focus[student_name], 2),
            "exam": round(exams[student_name], 2),
            "skills": skills
        }
        
        return result
    
    def process_multiple_students(self, csv_files: list) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple student CSV files.
        
        Args:
            csv_files: List of CSV file paths
            
        Returns:
            Dictionary mapping student names to their processed data
        """
        results = {}
        for filepath in csv_files:
            try:
                student_data = self.process_student_csv(filepath)
                student_name = student_data['student_id']
                results[student_name] = student_data
                print(f"[OK] Processed: {student_name}")
            except Exception as e:
                print(f"[ERROR] Error processing {filepath}: {e}")
        
        return results
