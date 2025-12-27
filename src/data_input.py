"""
Data Input Module
Handles CSV reading and manual data entry for student information
"""

import pandas as pd
from typing import Dict, Any, List
import json


class StudentDataInput:
    """Handle various input methods for student data"""
    
    @staticmethod
    def read_from_csv(filepath: str) -> List[Dict[str, Any]]:
        """
        Read student data from CSV file
        
        Expected CSV format:
        student_id, attendance, homework, classwork, class_focus, exam, 
        problem_solving, communication, discipline
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of student dictionaries
        """
        try:
            df = pd.read_csv(filepath)
            students = []
            
            for _, row in df.iterrows():
                student = {
                    "student_id": row.get("student_id", "unknown"),
                    "attendance": float(row.get("attendance", 80)),
                    "homework": float(row.get("homework", 7)),
                    "classwork": float(row.get("classwork", 7)),
                    "class_focus": float(row.get("class_focus", 70)),
                    "exam": float(row.get("exam", 65)),
                    "skills": {
                        "problem_solving": float(row.get("problem_solving", 7)),
                        "communication": float(row.get("communication", 7)),
                        "discipline": float(row.get("discipline", 7))
                    }
                }
                students.append(student)
            
            print(f"✓ Successfully loaded {len(students)} student(s) from {filepath}")
            return students
            
        except FileNotFoundError:
            print(f"✗ Error: File not found - {filepath}")
            return []
        except Exception as e:
            print(f"✗ Error reading CSV: {str(e)}")
            return []
    
    @staticmethod
    def manual_input_interactive() -> Dict[str, Any]:
        """
        Interactive CLI for manual student data entry
        
        Returns:
            Student data dictionary
        """
        print("\n" + "="*50)
        print("📝 STUDENT DATA ENTRY")
        print("="*50 + "\n")
        
        student_id = input("Student ID/Name: ").strip()
        
        print("\n--- Performance Metrics (0-100%) ---")
        attendance = float(input("Attendance (0-100): ") or "80")
        class_focus = float(input("Class Focus (0-100): ") or "70")
        exam = float(input("Exam Score (0-100): ") or "65")
        
        print("\n--- Assignments (1-10 scale) ---")
        homework = float(input("Homework Quality (1-10): ") or "7")
        classwork = float(input("Classwork Quality (1-10): ") or "7")
        
        print("\n--- Skills (1-10 scale) ---")
        problem_solving = float(input("Problem Solving (1-10): ") or "7")
        communication = float(input("Communication (1-10): ") or "7")
        discipline = float(input("Discipline (1-10): ") or "7")
        
        student = {
            "student_id": student_id or "unknown",
            "attendance": attendance,
            "homework": homework,
            "classwork": classwork,
            "class_focus": class_focus,
            "exam": exam,
            "skills": {
                "problem_solving": problem_solving,
                "communication": communication,
                "discipline": discipline
            }
        }
        
        print("\n✓ Student data collected successfully!")
        return student
    
    @staticmethod
    def manual_input_dict(student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accept student data as dictionary (for programmatic input)
        
        Args:
            student_data: Dictionary with student information
            
        Returns:
            Validated student data dictionary
        """
        # Provide defaults for missing fields
        defaults = {
            "student_id": "unknown",
            "attendance": 80,
            "homework": 7,
            "classwork": 7,
            "class_focus": 70,
            "exam": 65,
            "skills": {
                "problem_solving": 7,
                "communication": 7,
                "discipline": 7
            }
        }
        
        # Merge with defaults
        student = {**defaults, **student_data}
        
        # Ensure skills exist
        if "skills" in student_data:
            student["skills"] = {**defaults["skills"], **student_data["skills"]}
        
        return student
    
    @staticmethod
    def save_to_csv(students: List[Dict[str, Any]], filepath: str):
        """
        Save student data to CSV file
        
        Args:
            students: List of student dictionaries
            filepath: Path to save CSV
        """
        try:
            # Flatten the data structure for CSV
            flattened = []
            for student in students:
                flat = {
                    "student_id": student.get("student_id"),
                    "attendance": student.get("attendance"),
                    "homework": student.get("homework"),
                    "classwork": student.get("classwork"),
                    "class_focus": student.get("class_focus"),
                    "exam": student.get("exam"),
                    "problem_solving": student.get("skills", {}).get("problem_solving"),
                    "communication": student.get("skills", {}).get("communication"),
                    "discipline": student.get("skills", {}).get("discipline")
                }
                flattened.append(flat)
            
            df = pd.DataFrame(flattened)
            df.to_csv(filepath, index=False)
            print(f"✓ Student data saved to {filepath}")
            
        except Exception as e:
            print(f"✗ Error saving CSV: {str(e)}")
    
    @staticmethod
    def create_sample_csv(filepath: str = "data/sample_students.csv"):
        """
        Create a sample CSV file with example student data
        
        Args:
            filepath: Path where sample CSV will be saved
        """
        sample_data = [
            {
                "student_id": "STU001",
                "attendance": 85,
                "homework": 8,
                "classwork": 7,
                "class_focus": 75,
                "exam": 72,
                "problem_solving": 8,
                "communication": 7,
                "discipline": 8
            },
            {
                "student_id": "STU002",
                "attendance": 70,
                "homework": 6,
                "classwork": 6,
                "class_focus": 60,
                "exam": 55,
                "problem_solving": 6,
                "communication": 6,
                "discipline": 5
            },
            {
                "student_id": "STU003",
                "attendance": 95,
                "homework": 9,
                "classwork": 9,
                "class_focus": 90,
                "exam": 88,
                "problem_solving": 9,
                "communication": 8,
                "discipline": 9
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_csv(filepath, index=False)
        print(f"✓ Sample CSV created at {filepath}")
        return filepath
