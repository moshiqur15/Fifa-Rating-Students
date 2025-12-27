"""
Student Improvement Prediction Model
Predicts whether, when, and how much a student will improve based on:
- Historical performance data
- Assigned improvement tasks
- Student attributes (hardwork, determination, etc.)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import json


class StudentPredictionModel:
    """
    Predicts student improvement across multiple timelines
    """
    
    def __init__(self):
        self.model_version = "1.0"
        self.created_date = "2025-12-09"
        
        # ML models
        self.classifier = RandomForestClassifier(n_estimators=150, random_state=42)
        self.regressor = RandomForestRegressor(n_estimators=150, random_state=42)
        self.scaler = StandardScaler()
        self.feature_cols = None
        self.is_trained = False
        
        # Timeline multipliers for predictions
        self.timeline_multipliers = {
            '1w': 0.15,
            '3w': 0.35,
            '1m': 0.5,
            '2m': 0.7,
            '6m': 0.95,
            '1y': 1.0
        }
    
    @staticmethod
    def normalize_attributes(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        """Normalize attribute columns to 0-1 scale"""
        df2 = df.copy()
        for c in cols:
            if c in df2.columns:
                if df2[c].max() > 1:
                    df2[c] = (df2[c] - df2[c].min()) / (df2[c].max() - df2[c].min() + 1e-9)
                else:
                    df2[c] = df2[c].clip(0, 1)
        return df2
    
    def create_student_history_from_data(self, student_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Create a synthetic student history from current performance data.
        This simulates past sessions for training the model.
        """
        student_id = student_data.get('student_id', 'unknown')
        
        # Generate simulated history (10 sessions over past 2 months)
        history = []
        base_score = student_data.get('exam', 65)
        
        for i in range(10):
            date = datetime.now() - timedelta(days=60 - i*6)
            
            # Simulate score progression with noise
            score = base_score + np.random.normal(i * 0.5, 2)
            score = np.clip(score, 0, 100)
            
            history.append({
                'student_id': student_id,
                'date': date,
                'subject': 'General',
                'score': score,
                'task_type': np.random.choice(['homework', 'quiz', 'revision']),
                'time_spent_minutes': np.random.randint(20, 60),
                'completed': np.random.choice([0, 1], p=[0.2, 0.8])
            })
        
        return pd.DataFrame(history)
    
    def aggregate_student_history(self, history_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate student history into features per student and subject
        """
        h = history_df.copy()
        h['date'] = pd.to_datetime(h['date'])
        
        agg = h.groupby(['student_id', 'subject']).agg(
            mean_score=('score', 'mean'),
            last_score=('score', 'last'),
            first_score=('score', 'first'),
            sessions=('score', 'count'),
            avg_time_spent=('time_spent_minutes', 'mean'),
            completion_rate=('completed', 'mean')
        ).reset_index()
        
        # Calculate improvement per session
        agg['improvement_per_session'] = (agg['last_score'] - agg['first_score']) / (agg['sessions'] + 1e-9)
        agg['improvement_total'] = agg['last_score'] - agg['first_score']
        
        return agg
    
    def prepare_features_from_tasks(
        self,
        student_data: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        history_agg: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Prepare features from student data, tasks, and history
        """
        student_id = student_data.get('student_id', 'unknown')
        
        # Aggregate tasks
        total_xp = sum(t.get('xp', 0) for t in tasks)
        n_tasks = len(tasks)
        est_minutes = sum(t.get('time_estimate_minutes', 30) for t in tasks)
        
        # Student attributes from performance data
        attributes = {
            'hardwork': student_data.get('homework', 7) / 10,
            'determination': student_data.get('class_focus', 70) / 100,
            'focus': student_data.get('classwork', 7) / 10,
            'discipline': student_data.get('attendance', 80) / 100,
            'creativity': student_data.get('skills', {}).get('problem_solving', 7) / 10
        }
        
        # Merge with history
        if len(history_agg) > 0:
            hist_row = history_agg[history_agg['student_id'] == student_id].iloc[0]
            
            features = {
                'student_id': student_id,
                'subject': 'General',
                'mean_score': hist_row['mean_score'],
                'last_score': hist_row['last_score'],
                'first_score': hist_row['first_score'],
                'sessions': hist_row['sessions'],
                'avg_time_spent': hist_row['avg_time_spent'],
                'completion_rate': hist_row['completion_rate'],
                'improvement_per_session': hist_row['improvement_per_session'],
                'improvement_total': hist_row['improvement_total'],
                'total_xp': total_xp,
                'n_tasks': n_tasks,
                'est_minutes': est_minutes,
                **attributes
            }
        else:
            # No history, use defaults
            features = {
                'student_id': student_id,
                'subject': 'General',
                'mean_score': student_data.get('exam', 65),
                'last_score': student_data.get('exam', 65),
                'first_score': student_data.get('exam', 60),
                'sessions': 5,
                'avg_time_spent': 30,
                'completion_rate': 0.7,
                'improvement_per_session': 1.0,
                'improvement_total': 5.0,
                'total_xp': total_xp,
                'n_tasks': n_tasks,
                'est_minutes': est_minutes,
                **attributes
            }
        
        return pd.DataFrame([features])
    
    def train_model(self, features_df: pd.DataFrame):
        """Train the prediction models"""
        df = features_df.copy()
        
        # Create training targets
        # will_improve: based on improvement_per_session and task complexity
        # Add some variation to ensure both classes exist
        improvement_score = df['improvement_per_session'] + (df['total_xp'] / 200)
        df['will_improve'] = (improvement_score > 0.3).astype(int)
        
        # Ensure at least one sample of each class for training
        if df['will_improve'].nunique() == 1:
            # Add synthetic variation
            if df['will_improve'].iloc[0] == 1:
                # All positive, make some negative
                df.loc[df.index[0], 'will_improve'] = 0
            else:
                # All negative, make some positive
                df.loc[df.index[0], 'will_improve'] = 1
        
        # mark_increase: estimate based on improvement rate and number of tasks
        df['est_sessions_remain'] = df['n_tasks'].fillna(4)
        df['mark_increase'] = df['improvement_per_session'] * df['est_sessions_remain'] * 1.5
        df['mark_increase'] = df['mark_increase'].clip(0, 30)  # Cap at 30 marks increase
        
        # Prepare features
        feature_columns = [
            'mean_score', 'last_score', 'sessions', 'avg_time_spent',
            'completion_rate', 'improvement_per_session', 'total_xp',
            'n_tasks', 'est_minutes', 'hardwork', 'determination',
            'focus', 'discipline', 'creativity'
        ]
        
        # Ensure all columns exist
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        X = df[feature_columns].fillna(0)
        y_clf = df['will_improve']
        y_reg = df['mark_increase']
        
        self.feature_cols = feature_columns
        
        # Scale and train
        X_scaled = self.scaler.fit_transform(X)
        self.classifier.fit(X_scaled, y_clf)
        self.regressor.fit(X_scaled, y_reg)
        
        self.is_trained = True
        print(f"[OK] Model trained on {len(df)} samples")
    
    def predict_timeline(
        self,
        features_df: pd.DataFrame,
        timeline: str = '1m'
    ) -> pd.DataFrame:
        """
        Predict improvement for a specific timeline
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        df = features_df.copy()
        
        # Scale task effects by timeline multiplier
        multiplier = self.timeline_multipliers.get(timeline, 0.5)
        
        if 'total_xp' in df.columns:
            df['total_xp_scaled'] = df['total_xp'] * multiplier
        if 'est_minutes' in df.columns:
            df['est_minutes_scaled'] = df['est_minutes'] * multiplier
        
        # Prepare feature vector
        X = df[self.feature_cols].fillna(0)
        
        # Apply timeline scaling
        if 'total_xp' in self.feature_cols:
            X['total_xp'] = df.get('total_xp_scaled', df.get('total_xp', 0))
        if 'est_minutes' in self.feature_cols:
            X['est_minutes'] = df.get('est_minutes_scaled', df.get('est_minutes', 0))
        
        X_scaled = self.scaler.transform(X)
        
        # Predictions
        proba = self.classifier.predict_proba(X_scaled)
        # Handle case where only one class was seen during training
        if proba.shape[1] == 1:
            # Only one class present, use that probability
            improve_prob = proba[:, 0]
        else:
            # Normal case: use probability of class 1 (will improve)
            improve_prob = proba[:, 1]
        
        mark_increase = self.regressor.predict(X_scaled)
        
        result = df[['student_id', 'subject']].copy()
        result['timeline'] = timeline
        result['improve_probability'] = improve_prob
        result['predicted_mark_increase'] = mark_increase
        result['will_improve'] = (improve_prob >= 0.5).astype(int)
        
        return result
    
    def predict_all_timelines(
        self,
        features_df: pd.DataFrame,
        timelines: List[str] = None
    ) -> pd.DataFrame:
        """
        Predict improvement across multiple timelines
        """
        if timelines is None:
            timelines = ['1w', '3w', '1m', '2m', '6m', '1y']
        
        results = []
        for timeline in timelines:
            pred = self.predict_timeline(features_df, timeline)
            results.append(pred)
        
        return pd.concat(results, ignore_index=True)
    
    def predict_improvement(
        self,
        student_data: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        timelines: List[str] = None
    ) -> Dict[str, Any]:
        """
        Complete prediction pipeline for a single student
        
        Args:
            student_data: Student performance data
            tasks: List of improvement tasks
            timelines: List of timeline strings (default: all)
            
        Returns:
            Dictionary with predictions and visualization data
        """
        # Create history
        history = self.create_student_history_from_data(student_data)
        history_agg = self.aggregate_student_history(history)
        
        # Prepare features
        features = self.prepare_features_from_tasks(student_data, tasks, history_agg)
        
        # Train if not already trained
        if not self.is_trained:
            self.train_model(features)
        
        # Predict across timelines
        predictions = self.predict_all_timelines(features, timelines)
        
        # Format results
        result = {
            'student_id': student_data.get('student_id', 'unknown'),
            'generated_date': datetime.now().isoformat(),
            'timelines': predictions.to_dict('records'),
            'summary': self._create_summary(predictions),
            'visualization_data': self._prepare_viz_data(predictions),
            'model_version': self.model_version
        }
        
        return result
    
    def _create_summary(self, predictions: pd.DataFrame) -> Dict[str, Any]:
        """Create summary statistics from predictions"""
        # Find most promising timeline
        best_timeline = predictions.loc[predictions['predicted_mark_increase'].idxmax()]
        
        # Average predictions
        avg_prob = predictions['improve_probability'].mean()
        avg_increase = predictions['predicted_mark_increase'].mean()
        
        return {
            'overall_improvement_probability': round(avg_prob * 100, 1),
            'average_predicted_increase': round(avg_increase, 1),
            'best_timeline': best_timeline['timeline'],
            'best_timeline_increase': round(best_timeline['predicted_mark_increase'], 1),
            'best_timeline_probability': round(best_timeline['improve_probability'] * 100, 1),
            'recommendation': self._generate_recommendation(avg_prob, avg_increase, best_timeline)
        }
    
    def _generate_recommendation(
        self,
        avg_prob: float,
        avg_increase: float,
        best_timeline: pd.Series
    ) -> str:
        """Generate human-readable recommendation"""
        if avg_prob >= 0.7:
            outlook = "excellent"
        elif avg_prob >= 0.5:
            outlook = "good"
        else:
            outlook = "moderate"
        
        rec = f"The student has {outlook} improvement prospects with an average {avg_increase:.1f} mark increase expected. "
        rec += f"Best results anticipated in {best_timeline['timeline']} timeline "
        rec += f"with {best_timeline['predicted_mark_increase']:.1f} marks improvement. "
        
        if avg_prob < 0.5:
            rec += "Consider additional support or revised task plans."
        elif avg_increase > 10:
            rec += "Strong potential for significant improvement!"
        
        return rec
    
    def _prepare_viz_data(self, predictions: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for visualization"""
        timeline_order = ['1w', '3w', '1m', '2m', '6m', '1y']
        timeline_labels = {
            '1w': '1 Week',
            '3w': '3 Weeks',
            '1m': '1 Month',
            '2m': '2 Months',
            '6m': '6 Months',
            '1y': '1 Year'
        }
        
        # Sort by timeline
        pred_sorted = predictions.sort_values('timeline', key=lambda x: x.map({t: i for i, t in enumerate(timeline_order)}))
        
        return {
            'timelines': [timeline_labels.get(t, t) for t in pred_sorted['timeline']],
            'timeline_codes': pred_sorted['timeline'].tolist(),
            'probabilities': (pred_sorted['improve_probability'] * 100).round(1).tolist(),
            'mark_increases': pred_sorted['predicted_mark_increase'].round(1).tolist(),
            'will_improve_flags': pred_sorted['will_improve'].tolist()
        }
