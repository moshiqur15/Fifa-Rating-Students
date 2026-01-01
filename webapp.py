"""
Student Rating System - Streamlit Web Application
FIFA-style student performance analysis with interactive UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import sys
import pickle
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from student_rating import StudentRatingModel
from csv_processor import CSVReportProcessor
from improvement_model import StudentImprovementModel
from prediction_model import StudentPredictionModel

# Page configuration
st.set_page_config(
    page_title="Student Rating System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'rating_model' not in st.session_state:
    st.session_state.rating_model = StudentRatingModel()
if 'csv_processor' not in st.session_state:
    st.session_state.csv_processor = CSVReportProcessor()
if 'improvement_model' not in st.session_state:
    st.session_state.improvement_model = StudentImprovementModel()
if 'prediction_model' not in st.session_state:
    st.session_state.prediction_model = StudentPredictionModel()

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size: 30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🎓 Student Rating System")
st.markdown("### FIFA-Style Student Performance Analysis")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    mode = st.radio(
        "Select Mode:",
        ["Upload CSV", "Manual Entry", "Batch Analysis"],
        index=0
    )
    
    st.markdown("---")
    
    # Check for Groq API
    groq_available = os.environ.get("GROQ_API_KEY") is not None
    if groq_available:
        st.success("✅ AI Features Active")
    else:
        st.info("ℹ️ AI Features: Set GROQ_API_KEY for advanced suggestions")
    
    st.markdown("---")
    st.markdown("### 📊 Rating Tiers")
    st.markdown("""
    - 85-100: **ELITE** ⭐⭐⭐
    - 75-84: **EXCELLENT** ⭐⭐
    - 65-74: **GOOD** ⭐
    - 50-64: **DEVELOPING**
    - 0-49: **NEEDS IMPROVEMENT** ⚠️
    """)

# Main content area
if mode == "Upload CSV":
    st.header("📤 Upload CSV Report Card")
    
    # Scan data folder
    data_folder = "data"
    if os.path.exists(data_folder):
        csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
        
        if csv_files:
            st.success(f"📂 Found {len(csv_files)} CSV file(s) in data/ folder")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_file = st.selectbox("Select a CSV file:", csv_files)
            
            with col2:
                if st.button("🔄 Refresh Files"):
                    st.rerun()
            
            if selected_file:
                file_path = os.path.join(data_folder, selected_file)
                
                # Preview CSV
                with st.expander("👁️ Preview CSV Data"):
                    try:
                        preview_df = pd.read_csv(file_path)
                        st.dataframe(preview_df.head(10))
                        st.info(f"Total records: {len(preview_df)}")
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
                
                # Analyze button
                if st.button("🔍 Analyze Selected File", type="primary"):
                    try:
                        with st.spinner("Processing student data..."):
                            # Extract student name from filename
                            student_name = selected_file.replace('.csv', '')
                            
                            # Process CSV
                            student_data = st.session_state.csv_processor.process_student_csv(
                                file_path, student_name
                            )
                            
                            # Calculate ratings
                            ratings = st.session_state.rating_model.compute_student_ratings(student_data)
                            
                            # Get recommendations
                            weak_category, recommendation, all_scores = st.session_state.rating_model.recommend_improvement(ratings)
                            
                            # Display results
                            st.success("✅ Analysis Complete!")
                            st.markdown("---")
                            
                            # Overall rating
                            overall = ratings["overall_rating"]
                            if overall >= 85:
                                tier = "ELITE ⭐⭐⭐"
                                color = "#28a745"
                            elif overall >= 75:
                                tier = "EXCELLENT ⭐⭐"
                                color = "#17a2b8"
                            elif overall >= 65:
                                tier = "GOOD ⭐"
                                color = "#ffc107"
                            elif overall >= 50:
                                tier = "DEVELOPING"
                                color = "#fd7e14"
                            else:
                                tier = "NEEDS IMPROVEMENT ⚠️"
                                color = "#dc3545"
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Student ID", student_name)
                            with col2:
                                st.metric("Overall Rating", f"{overall:.1f}/100")
                            with col3:
                                st.markdown(f"<h3 style='color: {color};'>{tier}</h3>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # Performance breakdown
                            st.subheader("📊 Performance Breakdown")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Create radar chart
                                categories = ['Attendance', 'Homework', 'Classwork', 'Class Focus', 'Exam']
                                values = [
                                    ratings["subcategories"]["Attendance"],
                                    ratings["subcategories"]["Homework"],
                                    ratings["subcategories"]["Classwork"],
                                    ratings["subcategories"]["Class Focus"],
                                    ratings["subcategories"]["Exam"]
                                ]
                                
                                fig = go.Figure()
                                fig.add_trace(go.Scatterpolar(
                                    r=values,
                                    theta=categories,
                                    fill='toself',
                                    name=student_name
                                ))
                                fig.update_layout(
                                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                    showlegend=True,
                                    title="Performance Radar"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                # Bar chart
                                fig2 = go.Figure()
                                fig2.add_trace(go.Bar(
                                    x=categories,
                                    y=values,
                                    marker_color=['#28a745', '#17a2b8', '#ffc107', '#fd7e14', '#dc3545']
                                ))
                                fig2.update_layout(
                                    title="Category Scores",
                                    yaxis_title="Score (0-100)",
                                    yaxis_range=[0, 100]
                                )
                                st.plotly_chart(fig2, use_container_width=True)
                            
                            # Skills
                            st.subheader("🎯 Skills Assessment")
                            skills = ratings["subcategories"]["Skills"]
                            skill_cols = st.columns(3)
                            
                            for idx, (skill, score) in enumerate(skills.items()):
                                with skill_cols[idx]:
                                    st.metric(skill.replace('_', ' ').title(), f"{score:.1f}/100")
                            
                            # Recommendations
                            st.markdown("---")
                            st.subheader("💡 Improvement Recommendations")
                            st.warning(f"**Weakest Area:** {weak_category}")
                            st.info(f"**Recommendation:** {recommendation}")
                            
                            # Generate Improvement Plan
                            with st.expander("📋 View Detailed Improvement Plan", expanded=False):
                                teacher_input = st.text_area(
                                    "Teacher's Additional Suggestions (Optional):",
                                    placeholder="Add specific observations or goals for this student...",
                                    height=100
                                )
                                
                                if st.button("🎯 Generate Improvement Plan", key="gen_improve"):
                                    with st.spinner("Creating personalized improvement plan..."):
                                        try:
                                            teacher_suggestion = teacher_input if teacher_input else "Focus on consistent practice and time management."
                                            
                                            improvement_plan = st.session_state.improvement_model.create_improvement_plan(
                                                student_data=student_data,
                                                rating_recommendation=recommendation,
                                                teacher_suggestion=teacher_suggestion,
                                                weak_category=weak_category,
                                                num_tasks=5
                                            )
                                            
                                            st.success("✅ Improvement Plan Generated!")
                                            
                                            # Display merged strategy
                                            merged = improvement_plan['merged_strategy']
                                            st.markdown("### 🎯 Unified Strategy")
                                            st.info(merged['merged_strategy'])
                                            
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.markdown("**Priority Level:**")
                                                priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                                                st.markdown(f"{priority_color.get(merged['priority_level'], '🟡')} {merged['priority_level']}")
                                            
                                            with col2:
                                                st.markdown("**Strategy Source:**")
                                                st.markdown(f"{'🤖 AI-Powered' if merged['source'] == 'groq_ai' else '📝 Rule-Based'}")
                                            
                                            st.markdown("**Key Focus Areas:**")
                                            for area in merged['key_focus_areas']:
                                                st.markdown(f"- {area}")
                                            
                                            st.markdown("**Reasoning:**")
                                            st.markdown(merged['reasoning'])
                                            
                                            # Display tasks
                                            st.markdown("---")
                                            st.markdown("### 📝 Action Items")
                                            
                                            for task in improvement_plan['tasks']:
                                                with st.container():
                                                    st.markdown(f"#### {task['task_id']}. {task['title']}")
                                                    st.markdown(f"**Category:** {task['category']} | **Difficulty:** {task['difficulty']} | **Time:** {task['time_estimate']}")
                                                    st.markdown(f"{task['description']}")
                                                    st.markdown(f"**Expected Impact:** {task['expected_impact']}")
                                                    st.markdown("")
                                            
                                            # Save plan
                                            os.makedirs("logs", exist_ok=True)
                                            plan_filename = f"logs/improvement_plan_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                            with open(plan_filename, 'w') as f:
                                                json.dump(improvement_plan, f, indent=2)
                                            
                                            st.success(f"💾 Plan saved to: {plan_filename}")
                                            
                                        except Exception as e:
                                            st.error(f"Error generating improvement plan: {e}")
                                            st.exception(e)
                            
                            # Generate Prediction
                            with st.expander("📈 View Performance Predictions", expanded=False):
                                if st.button("🔮 Generate Predictions", key="gen_predict"):
                                    with st.spinner("Analyzing improvement trajectory..."):
                                        try:
                                            # Create sample tasks for prediction (or use generated tasks if available)
                                            sample_tasks = [
                                                {"xp": 30, "time_estimate_minutes": 45},
                                                {"xp": 40, "time_estimate_minutes": 60},
                                                {"xp": 25, "time_estimate_minutes": 30},
                                                {"xp": 50, "time_estimate_minutes": 90},
                                            ]
                                            
                                            predictions = st.session_state.prediction_model.predict_improvement(
                                                student_data=student_data,
                                                tasks=sample_tasks
                                            )
                                            
                                            st.success("✅ Predictions Generated!")
                                            
                                            # Display summary
                                            summary = predictions['summary']
                                            st.markdown("### 🎯 Prediction Summary")
                                            
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric(
                                                    "Improvement Probability",
                                                    f"{summary['overall_improvement_probability']}%"
                                                )
                                            with col2:
                                                st.metric(
                                                    "Avg. Mark Increase",
                                                    f"+{summary['average_predicted_increase']}"
                                                )
                                            with col3:
                                                st.metric(
                                                    "Best Timeline",
                                                    summary['best_timeline'].upper()
                                                )
                                            
                                            st.info(summary['recommendation'])
                                            
                                            # Visualization
                                            st.markdown("---")
                                            st.markdown("### 📊 Timeline Analysis")
                                            
                                            viz_data = predictions['visualization_data']
                                            
                                            # Create dual-axis chart
                                            fig = go.Figure()
                                            
                                            # Probability line
                                            fig.add_trace(go.Scatter(
                                                x=viz_data['timelines'],
                                                y=viz_data['probabilities'],
                                                name='Improvement Probability (%)',
                                                mode='lines+markers',
                                                line=dict(color='#17a2b8', width=3),
                                                yaxis='y'
                                            ))
                                            
                                            # Mark increase bars
                                            fig.add_trace(go.Bar(
                                                x=viz_data['timelines'],
                                                y=viz_data['mark_increases'],
                                                name='Predicted Mark Increase',
                                                marker_color='#28a745',
                                                yaxis='y2'
                                            ))
                                            
                                            fig.update_layout(
                                                title="Improvement Predictions Across Timelines",
                                                xaxis_title="Timeline",
                                                yaxis=dict(
                                                    title="Probability (%)",
                                                    side='left',
                                                    range=[0, 100]
                                                ),
                                                yaxis2=dict(
                                                    title="Mark Increase",
                                                    side='right',
                                                    overlaying='y',
                                                    range=[0, max(viz_data['mark_increases']) * 1.2]
                                                ),
                                                hovermode='x unified'
                                            )
                                            
                                            st.plotly_chart(fig, use_container_width=True)
                                            
                                            # Timeline details
                                            st.markdown("### 📅 Timeline Details")
                                            timeline_df = pd.DataFrame(predictions['timelines'])
                                            timeline_df['improve_probability'] = (timeline_df['improve_probability'] * 100).round(1)
                                            timeline_df['predicted_mark_increase'] = timeline_df['predicted_mark_increase'].round(1)
                                            timeline_df['will_improve'] = timeline_df['will_improve'].map({1: '✅ Yes', 0: '❌ No'})
                                            
                                            st.dataframe(
                                                timeline_df[['timeline', 'improve_probability', 'predicted_mark_increase', 'will_improve']],
                                                use_container_width=True
                                            )
                                            
                                            # Save predictions
                                            pred_filename = f"logs/predictions_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                            with open(pred_filename, 'w') as f:
                                                json.dump(predictions, f, indent=2)
                                            
                                            st.success(f"💾 Predictions saved to: {pred_filename}")
                                            
                                        except Exception as e:
                                            st.error(f"Error generating predictions: {e}")
                                            st.exception(e)
                            
                            # Export option
                            st.markdown("---")
                            if st.button("💾 Export Results as JSON"):
                                results = {
                                    "timestamp": datetime.now().isoformat(),
                                    "student_id": student_name,
                                    "ratings": ratings,
                                    "weak_category": weak_category,
                                    "recommendation": recommendation
                                }
                                
                                # Save to logs
                                os.makedirs("logs", exist_ok=True)
                                filename = f"logs/analysis_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                with open(filename, 'w') as f:
                                    json.dump(results, f, indent=2)
                                
                                st.success(f"✅ Results saved to: {filename}")
                    
                    except Exception as e:
                        st.error(f"❌ Error processing file: {e}")
                        st.exception(e)
        else:
            st.warning("⚠️ No CSV files found in data/ folder")
            st.info("💡 Add CSV files to the data/ folder and click 'Refresh Files'")
    else:
        st.error("❌ data/ folder not found")
        if st.button("📁 Create data/ folder"):
            os.makedirs(data_folder, exist_ok=True)
            st.success("✅ Created data/ folder")
            st.rerun()

elif mode == "Manual Entry":
    st.header("✍️ Manual Student Data Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        student_id = st.text_input("Student ID", "student_001")
        attendance = st.slider("Attendance (%)", 0, 100, 85)
        homework = st.slider("Homework (1-10)", 1, 10, 8)
        classwork = st.slider("Classwork (1-10)", 1, 10, 7)
    
    with col2:
        class_focus = st.slider("Class Focus (%)", 0, 100, 75)
        exam = st.slider("Exam Score (%)", 0, 100, 70)
        
        st.markdown("**Skills:**")
        problem_solving = st.slider("Problem Solving (1-10)", 1, 10, 7)
        communication = st.slider("Communication (1-10)", 1, 10, 8)
        discipline = st.slider("Discipline (1-10)", 1, 10, 9)
    
    if st.button("🔍 Analyze Student", type="primary"):
        student_data = {
            "student_id": student_id,
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
        
        # Calculate ratings
        ratings = st.session_state.rating_model.compute_student_ratings(student_data)
        weak_category, recommendation, all_scores = st.session_state.rating_model.recommend_improvement(ratings)
        
        # Display results (same as above)
        st.success("✅ Analysis Complete!")
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
            tier = "NEEDS IMPROVEMENT ⚠️"
        
        st.markdown(f"### Overall Rating: {overall:.1f}/100 - {tier}")
        st.warning(f"**Weakest Area:** {weak_category}")
        st.info(f"**Recommendation:** {recommendation}")

elif mode == "Batch Analysis":
    st.header("📊 Batch Analysis - Compare Multiple Students")
    
    data_folder = "data"
    if os.path.exists(data_folder):
        csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
        
        if csv_files:
            selected_files = st.multiselect(
                "Select students to compare:",
                csv_files,
                default=csv_files[:min(3, len(csv_files))]
            )
            
            if selected_files and st.button("🔍 Analyze Selected Students", type="primary"):
                results = []
                
                with st.spinner("Processing students..."):
                    for file in selected_files:
                        try:
                            file_path = os.path.join(data_folder, file)
                            student_name = file.replace('.csv', '')
                            
                            student_data = st.session_state.csv_processor.process_student_csv(
                                file_path, student_name
                            )
                            ratings = st.session_state.rating_model.compute_student_ratings(student_data)
                            
                            results.append({
                                'Student': student_name,
                                'Overall': ratings['overall_rating'],
                                'Attendance': ratings['subcategories']['Attendance'],
                                'Homework': ratings['subcategories']['Homework'],
                                'Classwork': ratings['subcategories']['Classwork'],
                                'Class Focus': ratings['subcategories']['Class Focus'],
                                'Exam': ratings['subcategories']['Exam']
                            })
                        except Exception as e:
                            st.warning(f"⚠️ Could not process {file}: {e}")
                
                if results:
                    st.success(f"✅ Analyzed {len(results)} students")
                    
                    # Create comparison DataFrame
                    df = pd.DataFrame(results)
                    
                    # Rankings
                    st.subheader("🏆 Rankings")
                    df_sorted = df.sort_values('Overall', ascending=False)
                    st.dataframe(df_sorted, use_container_width=True)
                    
                    # Comparison chart
                    st.subheader("📈 Performance Comparison")
                    
                    fig = go.Figure()
                    for idx, row in df.iterrows():
                        fig.add_trace(go.Bar(
                            name=row['Student'],
                            x=['Attendance', 'Homework', 'Classwork', 'Class Focus', 'Exam'],
                            y=[row['Attendance'], row['Homework'], row['Classwork'], row['Class Focus'], row['Exam']]
                        ))
                    
                    fig.update_layout(
                        barmode='group',
                        title="Category-wise Comparison",
                        yaxis_title="Score (0-100)",
                        yaxis_range=[0, 100]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Comparison Report (CSV)",
                        data=csv,
                        file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.warning("⚠️ No CSV files found in data/ folder")
    else:
        st.error("❌ data/ folder not found")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎓 Student Rating System v2.1 | Built with ❤️ for better education</p>
</div>
""", unsafe_allow_html=True)
