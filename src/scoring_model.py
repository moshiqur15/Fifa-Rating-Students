"""
Student Scoring Model
Extracted from student_scoring_model.ipynb notebook
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class StudentScoringModel:
    """Student scoring model extracted from notebook"""
    
    def __init__(self):
        self.model_version = "1.0"
        self.created_date = "2025-12-02"
    
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

    def infer_skills_from_comments(self, comments: Dict[str, str]) -> Dict[str, Dict[str, int]]:
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

    def process_student_csv(self, df: pd.DataFrame, student_name: str, 
                          comment_dict: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process student data from DataFrame.
        
        Args:
            df: DataFrame with student records
            student_name: Name of the student
            comment_dict: Optional dict with teacher comments
            
        Returns:
            Dictionary with processed student data
        """
        # Add student column if not present
        if 'student' not in df.columns:
            df['student'] = student_name
        
        attendance = self.compute_attendance(df)
        hwcw = self.compute_hw_cw_score(df)
        exams = self.compute_exam_score(df)
        class_focus = self.compute_class_focus(attendance, hwcw, exams)
        
        # Process comments if available
        if comment_dict:
            skills = self.infer_skills_from_comments(comment_dict)
        else:
            skills = {student_name: {'problem_solving': 5, 'communication': 5, 'discipline': 5}}
        
        # Compile final result
        result = {
            "student_id": student_name,
            "attendance": round(attendance[student_name], 2),
            "homework": hwcw[student_name]['homework'],
            "classwork": hwcw[student_name]['classwork'],
            "class_focus": round(class_focus[student_name], 2),
            "exam": round(exams[student_name], 2),
            "skills": skills.get(student_name, {'problem_solving': 5, 'communication': 5, 'discipline': 5})
        }
        
        return result
