"""
Student Rating System - Interactive Web Application
FIFA-style student performance analysis with web interface
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from student_rating import StudentRatingModel
from csv_processor import CSVReportProcessor
from groq_client import GroqSuggestionGenerator
from improvement_model import StudentImprovementModel
from prediction_model import StudentPredictionModel

# Page configuration
st.set_page_config(
    page_title="Student Rating System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .rating-excellent {
        color: #28a745;
        font-weight: bold;
    }
    .rating-good {
        color: #17a2b8;
        font-weight: bold;
    }
    .rating-needs-improvement {
        color: #ffc107;
        font-weight: bold;
    }
    .rating-poor {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'rating_model' not in st.session_state:
    st.session_state.rating_model = StudentRatingModel()
    # Load existing model if available
    model_path = "models/student_rating_model.pkl"
    if os.path.exists(model_path):
        st.session_state.rating_model.load_model(model_path)

if 'csv_processor' not in st.session_state:
    st.session_state.csv_processor = CSVReportProcessor()

if 'groq_client' not in st.session_state:
    try:
        st.session_state.groq_client = GroqSuggestionGenerator()
        st.session_state.groq_available = True
    except:
        st.session_state.groq_client = None
        st.session_state.groq_available = False

if 'improvement_model' not in st.session_state:
    import pickle
    try:
        # Try to load from pickle
        model_path = "models/student_improvement_model.pkl"
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                st.session_state.improvement_model = pickle.load(f)
        else:
            st.session_state.improvement_model = StudentImprovementModel()
    except:
        st.session_state.improvement_model = StudentImprovementModel()

if 'prediction_model' not in st.session_state:
    import pickle
    try:
        model_path = "models/student_prediction_model.pkl"
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                st.session_state.prediction_model = pickle.load(f)
        else:
            st.session_state.prediction_model = StudentPredictionModel()
    except:
        st.session_state.prediction_model = StudentPredictionModel()

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None


def get_rating_tier(rating):
    """Get rating tier and color"""
    if rating >= 85:
        return "ELITE ⭐⭐⭐", "rating-excellent"
    elif rating >= 75:
        return "EXCELLENT ⭐⭐", "rating-excellent"
    elif rating >= 65:
        return "GOOD ⭐", "rating-good"
    elif rating >= 50:
        return "DEVELOPING", "rating-needs-improvement"
    else:
        return "NEEDS IMPROVEMENT", "rating-poor"


def create_radar_chart(subcategories):
    """Create radar chart for category visualization"""
    categories = ['Attendance', 'Homework', 'Classwork', 'Class Focus', 'Exam']
    values = [
        subcategories['Attendance'],
        subcategories['Homework'],
        subcategories['Classwork'],
        subcategories['Class Focus'],
        subcategories['Exam']
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color='rgb(31, 119, 180)'),
        line=dict(color='rgb(31, 119, 180)')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400
    )
    
    return fig


def create_skills_chart(skills):
    """Create bar chart for skills"""
    skill_names = [k.replace('_', ' ').title() for k in skills.keys()]
    skill_values = list(skills.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=skill_names,
            y=skill_values,
            marker=dict(
                color=skill_values,
                colorscale='Blues',
                showscale=False
            ),
            text=skill_values,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        yaxis=dict(range=[0, 100]),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig


def create_category_bars(all_scores, weak_category):
    """Create horizontal bar chart for all categories"""
    categories = list(all_scores.keys())
    scores = list(all_scores.values())
    
    colors = ['red' if cat == weak_category else 'lightblue' for cat in categories]
    
    fig = go.Figure(data=[
        go.Bar(
            y=categories,
            x=scores,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{score:.1f}" for score in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Score"),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    return fig


def main():
    # Header
    st.markdown('<h1 class="main-header">🎓 Student Rating System</h1>', unsafe_allow_html=True)
    st.markdown("**FIFA-Style Student Performance Analysis with AI-Powered Insights**")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Analysis Options")
        
        analysis_mode = st.radio(
            "Select Input Method:",
            ["Upload Report Card CSV", "Manual Entry", "Batch Analysis"]
        )
        
        st.markdown("---")
        
        # CSV Files counter
        data_dir = "data"
        if os.path.exists(data_dir):
            csv_count = len([f for f in os.listdir(data_dir) if f.endswith('.csv')])
            if csv_count > 0:
                st.info(f"📂 {csv_count} CSV file(s) available in data/")
            else:
                st.warning("📂 No CSV files in data/ directory")
        
        st.markdown("---")
        
        # API Status
        if st.session_state.groq_available:
            st.success("✓ Groq AI Connected")
        else:
            st.warning("⚠ AI Features Limited")
            st.info("Set GROQ_API_KEY environment variable for full AI features")
        
        st.markdown("---")
        
        # Model info
        with st.expander("ℹ️ Model Information"):
            metrics = st.session_state.rating_model.get_model_performance()
            st.metric("Total Predictions", metrics['total_predictions'])
            st.metric("Feedback Count", metrics['feedback_count'])
            st.metric("Average Error", f"{metrics['average_error']:.2f}")
            
            if st.button("📊 View Full Performance"):
                st.session_state.show_model_performance = True
        
        st.markdown("---")
        
        # Utilities
        with st.expander("🛠️ Utilities"):
            if st.button("📝 Create Sample CSV"):
                st.session_state.show_sample_creator = True
    
    # Check for special views
    if 'show_model_performance' in st.session_state and st.session_state.show_model_performance:
        show_model_performance_view()
        if st.button("← Back to Main"):
            st.session_state.show_model_performance = False
            st.rerun()
        return
    
    if 'show_sample_creator' in st.session_state and st.session_state.show_sample_creator:
        show_sample_csv_creator()
        if st.button("← Back to Main"):
            st.session_state.show_sample_creator = False
            st.rerun()
        return
    
    # Main content based on mode
    if analysis_mode == "Upload Report Card CSV":
        show_csv_upload_mode()
        # Show results below if available
        if st.session_state.analysis_results:
            # Clear visual separator
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown('<div id="results-section"></div>', unsafe_allow_html=True)
            display_analysis_results()
    elif analysis_mode == "Manual Entry":
        show_manual_entry_mode()
        # Show results below if available
        if st.session_state.analysis_results:
            # Clear visual separator
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown('<div id="results-section"></div>', unsafe_allow_html=True)
            display_analysis_results()
    else:
        show_batch_analysis_mode()


def show_csv_upload_mode():
    """CSV upload and analysis mode"""
    st.header("📤 Upload Student Report Card")
    
    st.info("""
    Upload a CSV file containing daily student records with columns:
    - `attendance` (Present/Absent)
    - `HW_issue` (True/False)
    - `CW_issue` (True/False)
    - `daily_exam1_mark`, `daily_exam2_mark` (out of 10)
    - `teacher_comment` (optional, for AI analysis)
    """)
    
    # Scan for available CSV files in data directory
    data_dir = "data"
    available_csvs = []
    if os.path.exists(data_dir):
        available_csvs = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    # Show available CSV files
    if available_csvs:
        st.subheader("📂 Available CSV Files in Data Directory")
        
        # Create selection interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_csv = st.selectbox(
                "Select a CSV file to analyze:",
                ["-- Choose from available files --"] + available_csvs,
                key="csv_selector"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if selected_csv != "-- Choose from available files --":
                if st.button("🔍 Analyze Selected File", type="primary", key="analyze_selected"):
                    analyze_csv_file(os.path.join(data_dir, selected_csv))
                    return  # Exit function after analysis
        
        # Show file details in expander
        if selected_csv != "-- Choose from available files --":
            filepath = os.path.join(data_dir, selected_csv)
            with st.expander("👁️ Preview Selected File", expanded=True):
                try:
                    df = pd.read_csv(filepath)
                    st.dataframe(df.head(10), use_container_width=True)
                    st.caption(f"Total Records: {len(df)} | Columns: {', '.join(df.columns.tolist())}")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        
        st.markdown("---")
        st.markdown("**Or upload your own CSV file:**")
    else:
        st.warning(f"No CSV files found in '{data_dir}' directory. Upload your own file below.")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file to upload", type=['csv'])
    
    if uploaded_file is not None:
        # Preview uploaded data
        df = pd.read_csv(uploaded_file)
        
        with st.expander("📊 Preview Uploaded Data", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Total Records: {len(df)}")
        
        # Student name input
        student_name = st.text_input(
            "Student Name (optional - will use filename if empty)",
            value=""
        )
        
        if st.button("🔍 Analyze Report Card", type="primary"):
            with st.spinner("Processing report card..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Process CSV
                    student_data = st.session_state.csv_processor.process_student_csv(
                        temp_path,
                        student_name if student_name else None
                    )
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                    # Show extracted metrics
                    st.success(f"✓ Report card processed for: **{student_data['student_id']}**")
                    
                    show_extracted_metrics(student_data)
                    
                    # Analyze
                    with st.spinner("Calculating FIFA-style ratings..."):
                        ratings = st.session_state.rating_model.compute_student_ratings(student_data)
                        weak_category, recommendation, all_scores = st.session_state.rating_model.recommend_improvement(ratings)
                        
                        # Store results
                        st.session_state.analysis_results = {
                            'student_data': student_data,
                            'ratings': ratings,
                            'weak_category': weak_category,
                            'recommendation': recommendation,
                            'all_scores': all_scores
                        }
                        
                        st.success("✓ Analysis complete! **Scroll down** to view the full report.")
                        st.info("👇 Results are displayed below this section")
                        
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())


def analyze_csv_file(filepath):
    """Helper function to analyze a CSV file from the data directory"""
    with st.spinner("Processing report card..."):
        try:
            # Process CSV
            student_data = st.session_state.csv_processor.process_student_csv(filepath)
            
            # Analyze
            with st.spinner("Calculating FIFA-style ratings..."):
                ratings = st.session_state.rating_model.compute_student_ratings(student_data)
                weak_category, recommendation, all_scores = st.session_state.rating_model.recommend_improvement(ratings)
                
                # Store results
                st.session_state.analysis_results = {
                    'student_data': student_data,
                    'ratings': ratings,
                    'weak_category': weak_category,
                    'recommendation': recommendation,
                    'all_scores': all_scores
                }
                
                st.success(f"✓ Analysis complete for: **{student_data['student_id']}**")
                st.info("👇 Scroll down to view the full report")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())


def show_extracted_metrics(student_data):
    """Display extracted metrics from CSV"""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📊 Extracted Metrics")
    st.markdown("*These metrics were calculated from the daily records in the CSV file.*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display in a more visual way
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📅 Daily Metrics")
        st.metric("Attendance Rate", f"{student_data['attendance']:.1f}%", 
                 delta="Perfect" if student_data['attendance'] == 100 else None)
        st.metric("Homework Score", f"{student_data['homework']}/10")
        st.metric("Classwork Score", f"{student_data['classwork']}/10")
    
    with col2:
        st.markdown("### 📊 Performance")
        st.metric("Class Focus", f"{student_data['class_focus']:.1f}%")
        st.metric("Exam Average", f"{student_data['exam']:.1f}%")
    
    with col3:
        st.markdown("### 💪 Skills (from comments)")
        for skill, score in student_data['skills'].items():
            st.metric(skill.replace('_', ' ').title(), f"{score}/10")


def show_manual_entry_mode():
    """Manual data entry mode"""
    st.header("✍️ Manual Student Data Entry")
    
    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("Student Name *", placeholder="e.g., John Doe")
            attendance = st.slider("Attendance (%)", 0, 100, 80)
            homework = st.slider("Homework (1-10)", 1, 10, 7)
            classwork = st.slider("Classwork (1-10)", 1, 10, 7)
        
        with col2:
            class_focus = st.slider("Class Focus (%)", 0, 100, 70)
            exam = st.slider("Exam Score (%)", 0, 100, 65)
        
        st.subheader("Skills Assessment")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            problem_solving = st.slider("Problem Solving (1-10)", 1, 10, 7)
        with col4:
            communication = st.slider("Communication (1-10)", 1, 10, 7)
        with col5:
            discipline = st.slider("Discipline (1-10)", 1, 10, 7)
        
        submitted = st.form_submit_button("🔍 Analyze Student", type="primary")
        
        if submitted:
            if not student_id:
                st.error("Please enter a student name")
            else:
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
                
                with st.spinner("Calculating ratings..."):
                    ratings = st.session_state.rating_model.compute_student_ratings(student_data)
                    weak_category, recommendation, all_scores = st.session_state.rating_model.recommend_improvement(ratings)
                    
                    st.session_state.analysis_results = {
                        'student_data': student_data,
                        'ratings': ratings,
                        'weak_category': weak_category,
                        'recommendation': recommendation,
                        'all_scores': all_scores
                    }
                    
                    st.success("✓ Analysis complete! **Scroll down** to view the full report.")
                    st.info("👇 Results are displayed below this form")


def show_batch_analysis_mode():
    """Batch analysis mode for multiple students"""
    st.header("📊 Batch Student Analysis")
    
    st.info("Analyze multiple student CSV files at once from the data/ directory")
    
    # Find CSV files
    data_dir = "data"
    col1, col2 = st.columns([4, 1])
    
    with col2:
        if st.button("🔄 Refresh Files"):
            st.rerun()
    
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if csv_files:
            # Display found files
            st.success(f"✓ Found {len(csv_files)} CSV file(s) in data/ directory")
            
            # Show files in a nice format
            with st.expander("📁 Available Files", expanded=True):
                for i, filename in enumerate(csv_files, 1):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        df = pd.read_csv(filepath)
                        st.text(f"{i}. {filename} ({len(df)} records)")
                    except:
                        st.text(f"{i}. {filename}")
            
            st.markdown("---")
            
            selected_files = st.multiselect(
                "Select CSV files to analyze:",
                csv_files,
                default=csv_files[:3] if len(csv_files) >= 3 else csv_files
            )
            
            if st.button("🔍 Analyze Selected Students", type="primary"):
                if not selected_files:
                    st.warning("Please select at least one file")
                else:
                    results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, filename in enumerate(selected_files):
                        status_text.text(f"Processing {filename}...")
                        filepath = os.path.join(data_dir, filename)
                        
                        try:
                            student_data = st.session_state.csv_processor.process_student_csv(filepath)
                            ratings = st.session_state.rating_model.compute_student_ratings(student_data)
                            
                            results.append({
                                'Student': student_data['student_id'],
                                'Overall Rating': ratings['overall_rating'],
                                'Attendance': student_data['attendance'],
                                'Homework': student_data['homework'],
                                'Classwork': student_data['classwork'],
                                'Exam': student_data['exam'],
                                'Class Focus': student_data['class_focus']
                            })
                        except Exception as e:
                            st.warning(f"Error processing {filename}: {e}")
                        
                        progress_bar.progress((i + 1) / len(selected_files))
                    
                    status_text.text("✓ Analysis complete!")
                    
                    # Display results
                    if results:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown('<h2 style="text-align: center; color: #1f77b4;">📈 Batch Analysis Results</h2>', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        df_results = pd.DataFrame(results)
                        df_results = df_results.sort_values('Overall Rating', ascending=False)
                        
                        # Summary stats
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Students", len(df_results))
                        with col2:
                            st.metric("Average Rating", f"{df_results['Overall Rating'].mean():.1f}")
                        with col3:
                            st.metric("Highest", f"{df_results['Overall Rating'].max():.1f}")
                        with col4:
                            st.metric("Lowest", f"{df_results['Overall Rating'].min():.1f}")
                        
                        st.markdown("---")
                        st.markdown("### 🏆 Rankings")
                        
                        # Rankings with better styling
                        st.dataframe(
                            df_results.style.background_gradient(subset=['Overall Rating'], cmap='RdYlGn'),
                            use_container_width=True,
                            height=400
                        )
                        
                        # Visualization
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig = px.bar(
                                df_results,
                                x='Student',
                                y='Overall Rating',
                                title='Student Rankings',
                                color='Overall Rating',
                                color_continuous_scale='blues'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            fig = px.scatter(
                                df_results,
                                x='Exam',
                                y='Overall Rating',
                                size='Attendance',
                                color='Student',
                                title='Exam vs Overall Performance',
                                hover_data=['Homework', 'Classwork']
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Download results
                        csv = df_results.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
        else:
            st.warning(f"No CSV files found in {data_dir}/ directory")
    else:
        st.error(f"Data directory '{data_dir}' not found")


def display_analysis_results():
    """Display complete analysis results"""
    if st.session_state.analysis_results is None:
        return
    
    results = st.session_state.analysis_results
    ratings = results['ratings']
    weak_category = results['weak_category']
    recommendation = results['recommendation']
    all_scores = results['all_scores']
    
    # Large visual separator with arrow
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0; background: linear-gradient(to bottom, transparent, #f0f2f6, transparent); margin: 2rem 0;">
            <h3 style="color: #1f77b4; margin: 0;">⬇️ ANALYSIS RESULTS BELOW ⬇️</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Show extracted metrics first as summary
    if 'student_data' in results:
        show_extracted_metrics(results['student_data'])
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
    
    # Large prominent header
    st.markdown('<h1 style="text-align: center; color: #1f77b4; margin-top: 2rem;">🎯 FIFA-Style Rating Analysis</h1>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Overall rating - BIG and centered
    overall_rating = ratings['overall_rating']
    tier, tier_class = get_rating_tier(overall_rating)
    
    # Large rating display
    st.markdown(f'<h1 style="text-align: center; font-size: 4rem; color: #1f77b4;">🏆 {overall_rating:.1f}/100</h1>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="text-align: center;" class="{tier_class}">{tier}</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Compact info row
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"**Student:** {results['student_data']['student_id']}")
    
    with col2:
        st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    
    with col3:
        st.markdown(f"**Weak Area:** {weak_category}")
    
    st.markdown("---")
    
    # Visualizations - Full width tabs
    st.markdown("## 📊 Performance Breakdown")
    
    tab1, tab2, tab3 = st.tabs(["📊 Category Scores", "🎯 Radar View", "💪 Skills Analysis"])
    
    with tab1:
        # Create larger, better category chart
        fig = create_category_bars(all_scores, weak_category)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Prominent warning
        st.warning(f"⚠️ **Focus Area:** {weak_category} - Score: {all_scores[weak_category]:.1f}/100")
        st.info(f"💡 **Quick Tip:** {recommendation}")
    
    with tab2:
        fig = create_radar_chart(ratings['subcategories'])
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add interpretation
        st.markdown("""
        **📖 How to Read This Chart:**
        - Larger area = Better overall balance
        - Check for gaps between inner and outer rings
        - Aim for a balanced pentagon shape
        """)
    
    with tab3:
        if 'Skills' in ratings['subcategories']:
            skills = ratings['subcategories']['Skills']
            fig = create_skills_chart(skills)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Skills summary
            avg_skill = sum(skills.values()) / len(skills)
            st.metric("Average Skill Score", f"{avg_skill:.1f}/100")
    
    st.markdown("---")
    
    # Detailed scores - More prominent
    st.markdown("## 📈 Detailed Scores")
    
    subcats = ratings['subcategories']
    
    # Main categories in larger metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Attendance", f"{subcats['Attendance']:.1f}", delta=None)
    with col2:
        st.metric("Homework", f"{subcats['Homework']:.1f}", delta=None)
    with col3:
        st.metric("Classwork", f"{subcats['Classwork']:.1f}", delta=None)
    with col4:
        st.metric("Class Focus", f"{subcats['Class Focus']:.1f}", delta=None)
    with col5:
        st.metric("Exam", f"{subcats['Exam']:.1f}", delta=None)
    
    st.markdown("---")
    
    # Recommendations - More prominent
    st.markdown("## 💡 Recommendations & Next Steps")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(f"**Primary Focus:** {recommendation}")
    with col2:
        st.metric("Priority Area", weak_category, delta=f"{all_scores[weak_category]:.1f}")
    
    # AI-powered suggestions
    if st.session_state.groq_available:
        with st.expander("🤖 AI-Powered Improvement Plan", expanded=True):
            if st.button("Generate AI Improvement Plan"):
                with st.spinner("Generating personalized improvement plan..."):
                    try:
                        improvement_plan = st.session_state.groq_client.generate_improvement_plan(
                            results['student_data']['student_id'],
                            ratings,
                            weak_category,
                            recommendation,
                            all_scores
                        )
                        st.markdown(improvement_plan)
                        
                        # Save to file
                        output_file = f"logs/ai_suggestions_{results['student_data']['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        os.makedirs("logs", exist_ok=True)
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(improvement_plan)
                        
                        st.success(f"✓ Saved to {output_file}")
                    except Exception as e:
                        st.error(f"Error generating AI plan: {e}")
        
        with st.expander("💪 Strengths Analysis"):
            if st.button("Generate Strengths Analysis"):
                with st.spinner("Analyzing strengths..."):
                    try:
                        strengths = st.session_state.groq_client.generate_strengths_analysis(
                            results['student_data']['student_id'],
                            ratings
                        )
                        st.markdown(strengths)
                    except Exception as e:
                        st.error(f"Error generating strengths analysis: {e}")
    
    st.markdown("---")
    
    # NEW: Comprehensive Improvement Plan Section
    st.markdown("## 🎯 Comprehensive Improvement Plan")
    st.markdown("*Merges AI suggestions with teacher feedback using advanced AI analysis*")
    
    with st.expander("📋 Generate Complete Improvement Plan", expanded=True):
        st.markdown("""
        This feature combines:
        1. **AI Model Recommendations** from the rating system
        2. **Teacher's Personal Observations** and suggestions
        3. **Groq AI Analysis** to create the best unified strategy
        4. **Specific Task List** with actionable items
        """)
        
        # Teacher input
        st.markdown("### 👨‍🏫 Teacher Input")
        teacher_suggestion = st.text_area(
            "Teacher's observations and suggestions:",
            placeholder="e.g., Student struggles with time management. Needs to practice breaking down complex problems into smaller steps. Shows promise in group discussions.",
            height=100,
            key="teacher_suggestion"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            num_tasks = st.number_input("Number of Tasks", min_value=3, max_value=10, value=5)
        
        with col2:
            st.markdown("")
        
        if st.button("🚀 Generate Improvement Plan", type="primary", use_container_width=True):
            if not teacher_suggestion.strip():
                st.warning("⚠️ Please provide teacher suggestions for best results.")
            else:
                with st.spinner("🤖 AI is analyzing and creating your improvement plan..."):
                    try:
                        # Create complete improvement plan
                        improvement_plan = st.session_state.improvement_model.create_improvement_plan(
                            student_data=results['student_data'],
                            rating_recommendation=recommendation,
                            teacher_suggestion=teacher_suggestion,
                            weak_category=weak_category,
                            num_tasks=num_tasks
                        )
                        
                        # Display merged strategy
                        st.markdown("---")
                        st.markdown("### ✨ Unified Improvement Strategy")
                        
                        strategy = improvement_plan['merged_strategy']
                        
                        # Main strategy
                        st.success(f"**Strategy:** {strategy['merged_strategy']}")
                        
                        # Key focus areas
                        st.markdown("**🎯 Key Focus Areas:**")
                        for area in strategy['key_focus_areas']:
                            st.markdown(f"- {area}")
                        
                        # Reasoning
                        st.info(f"**💡 Why this works:** {strategy['reasoning']}")
                        
                        # Priority
                        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                        st.markdown(f"{priority_emoji.get(strategy['priority_level'], '🟡')} **Priority:** {strategy['priority_level']}")
                        
                        # Display tasks
                        st.markdown("---")
                        st.markdown("### 📝 Specific Action Tasks")
                        st.markdown("*These tasks are tailored for this student and reusable for similar cases*")
                        
                        tasks = improvement_plan['tasks']
                        
                        for i, task in enumerate(tasks, 1):
                            with st.expander(f"Task {i}: {task['title']}", expanded=(i == 1)):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.markdown(f"**Category:** {task['category']}")
                                with col2:
                                    st.markdown(f"**Time:** {task['time_estimate']}")
                                with col3:
                                    difficulty_color = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
                                    st.markdown(f"**Difficulty:** {difficulty_color.get(task['difficulty'], '🟡')} {task['difficulty']}")
                                
                                st.markdown("---")
                                st.markdown(f"**📖 Description:**\n{task['description']}")
                                st.markdown(f"**✨ Expected Impact:**\n{task['expected_impact']}")
                                st.markdown(f"**♻️ Reusable For:**\n{task['reusable_for']}")
                        
                        # Show original suggestions for reference
                        with st.expander("📚 View Original Suggestions"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**🤖 AI Model Recommendation:**")
                                st.info(improvement_plan['original_suggestions']['rating_model'])
                            
                            with col2:
                                st.markdown("**👨‍🏫 Teacher Suggestion:**")
                                st.info(improvement_plan['original_suggestions']['teacher'])
                        
                        # Save option
                        st.markdown("---")
                        if st.button("💾 Save Improvement Plan", use_container_width=True):
                            output_file = f"logs/improvement_plan_{results['student_data']['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            os.makedirs("logs", exist_ok=True)
                            
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(improvement_plan, f, indent=2, ensure_ascii=False)
                            
                            st.success(f"✓ Improvement plan saved to {output_file}")
                        
                        # Download button
                        json_str = json.dumps(improvement_plan, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📥 Download Improvement Plan",
                            data=json_str,
                            file_name=f"improvement_plan_{results['student_data']['student_id']}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        
                        # Store improvement plan in session state for predictions
                        st.session_state.current_improvement_plan = improvement_plan
                        st.session_state.current_tasks = tasks
                        st.session_state.improvement_plan_generated = True
                        
                    except Exception as e:
                        st.error(f"Error generating improvement plan: {e}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
    
    # NEW: Independent Prediction Section (outside the improvement plan expander)
    if st.session_state.get('improvement_plan_generated', False):
        st.markdown("---")
        with st.expander("🔮 Improvement Predictions & Timeline", expanded=False):
            st.markdown("*AI predicts when and how much the student will improve with these tasks*")
            
            if st.button("📊 Generate Improvement Predictions", use_container_width=True, key="predict_btn"):
                st.session_state.show_predictions = True
            
            if st.session_state.get('show_predictions', False):
                with st.spinner("🤖 Predicting improvement timelines..."):
                                try:
                                    # Get tasks from session state
                                    tasks = st.session_state.current_tasks
                                    
                                    # Convert tasks to required format with XP
                                    tasks_for_prediction = []
                                    for task in tasks:
                                        # Estimate XP based on difficulty
                                        difficulty_xp = {
                                            'Easy': 20,
                                            'Medium': 40,
                                            'Hard': 60
                                        }
                                        xp = difficulty_xp.get(task.get('difficulty', 'Medium'), 40)
                                        
                                        # Extract time estimate in minutes
                                        time_str = task.get('time_estimate', '30 minutes')
                                        time_minutes = 30  # default
                                        try:
                                            if 'minute' in time_str.lower():
                                                time_minutes = int(''.join(filter(str.isdigit, time_str.split('minute')[0])))
                                            elif 'hour' in time_str.lower():
                                                time_minutes = int(''.join(filter(str.isdigit, time_str.split('hour')[0]))) * 60
                                        except:
                                            time_minutes = 30
                                        
                                        tasks_for_prediction.append({
                                            'task': task.get('title', ''),
                                            'xp': xp,
                                            'time_estimate_minutes': time_minutes,
                                            'category': task.get('category', 'General')
                                        })
                                    
                                    # Generate predictions
                                    predictions = st.session_state.prediction_model.predict_improvement(
                                        student_data=results['student_data'],
                                        tasks=tasks_for_prediction
                                    )
                                    
                                    # Display summary
                                    summary = predictions['summary']
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric(
                                            "Overall Improvement Probability",
                                            f"{summary['overall_improvement_probability']}%"
                                        )
                                    with col2:
                                        st.metric(
                                            "Average Mark Increase",
                                            f"+{summary['average_predicted_increase']}"
                                        )
                                    with col3:
                                        st.metric(
                                            "Best Timeline",
                                            summary['best_timeline'].upper(),
                                            f"+{summary['best_timeline_increase']} marks"
                                        )
                                    
                                    st.info(f"💡 **Prediction:** {summary['recommendation']}")
                                    
                                    # Visualizations
                                    st.markdown("---")
                                    st.markdown("### 📊 Prediction Graphs")
                                    
                                    viz_data = predictions['visualization_data']
                                    
                                    tab1, tab2, tab3 = st.tabs(["📈 Mark Increase Over Time", "🎯 Improvement Probability", "📊 Combined View"])
                                    
                                    with tab1:
                                        # Line chart for mark increase
                                        import plotly.graph_objects as go
                                        
                                        fig = go.Figure()
                                        fig.add_trace(go.Scatter(
                                            x=viz_data['timelines'],
                                            y=viz_data['mark_increases'],
                                            mode='lines+markers',
                                            name='Predicted Mark Increase',
                                            line=dict(color='#1f77b4', width=3),
                                            marker=dict(size=10)
                                        ))
                                        
                                        fig.update_layout(
                                            title="Expected Mark Increase Across Timelines",
                                            xaxis_title="Timeline",
                                            yaxis_title="Mark Increase",
                                            height=400,
                                            hovermode='x unified'
                                        )
                                        
                                        st.plotly_chart(fig, use_container_width=True)
                                        st.markdown("📝 **Interpretation:** Shows how marks are expected to increase over different time periods.")
                                    
                                    with tab2:
                                        # Bar chart for probabilities
                                        fig = go.Figure()
                                        
                                        colors = ['#28a745' if p >= 70 else '#ffc107' if p >= 50 else '#dc3545' 
                                                 for p in viz_data['probabilities']]
                                        
                                        fig.add_trace(go.Bar(
                                            x=viz_data['timelines'],
                                            y=viz_data['probabilities'],
                                            marker=dict(color=colors),
                                            text=[f"{p}%" for p in viz_data['probabilities']],
                                            textposition='auto'
                                        ))
                                        
                                        fig.update_layout(
                                            title="Probability of Improvement by Timeline",
                                            xaxis_title="Timeline",
                                            yaxis_title="Probability (%)",
                                            yaxis=dict(range=[0, 100]),
                                            height=400
                                        )
                                        
                                        st.plotly_chart(fig, use_container_width=True)
                                        st.markdown("📝 **Interpretation:** Higher percentage = more likely to see improvement in that timeframe.")
                                    
                                    with tab3:
                                        # Combined view with dual y-axis
                                        from plotly.subplots import make_subplots
                                        
                                        fig = make_subplots(
                                            rows=2, cols=1,
                                            subplot_titles=("Mark Increase Prediction", "Improvement Probability"),
                                            vertical_spacing=0.15
                                        )
                                        
                                        # Mark increase
                                        fig.add_trace(
                                            go.Scatter(
                                                x=viz_data['timelines'],
                                                y=viz_data['mark_increases'],
                                                mode='lines+markers',
                                                name='Mark Increase',
                                                line=dict(color='#1f77b4', width=2),
                                                marker=dict(size=8)
                                            ),
                                            row=1, col=1
                                        )
                                        
                                        # Probability
                                        fig.add_trace(
                                            go.Bar(
                                                x=viz_data['timelines'],
                                                y=viz_data['probabilities'],
                                                name='Probability %',
                                                marker=dict(color='#28a745')
                                            ),
                                            row=2, col=1
                                        )
                                        
                                        fig.update_xaxes(title_text="Timeline", row=2, col=1)
                                        fig.update_yaxes(title_text="Marks", row=1, col=1)
                                        fig.update_yaxes(title_text="Probability (%)", range=[0, 100], row=2, col=1)
                                        
                                        fig.update_layout(height=700, showlegend=False)
                                        
                                        st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Timeline details table
                                    st.markdown("---")
                                    st.markdown("### 📑 Timeline Details")
                                    
                                    timeline_df = pd.DataFrame(predictions['timelines'])
                                    display_df = timeline_df[['timeline', 'improve_probability', 'predicted_mark_increase', 'will_improve']].copy()
                                    display_df.columns = ['Timeline', 'Improvement Probability', 'Expected Mark Increase', 'Will Improve']
                                    display_df['Improvement Probability'] = (display_df['Improvement Probability'] * 100).round(1).astype(str) + '%'
                                    display_df['Expected Mark Increase'] = '+' + display_df['Expected Mark Increase'].round(1).astype(str)
                                    display_df['Will Improve'] = display_df['Will Improve'].map({1: '✅ Yes', 0: '❌ No'})
                                    
                                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                                    
                                    # Save predictions
                                    if st.button("💾 Save Predictions", use_container_width=True):
                                        pred_file = f"logs/predictions_{results['student_data']['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                        os.makedirs("logs", exist_ok=True)
                                        with open(pred_file, 'w', encoding='utf-8') as f:
                                            json.dump(predictions, f, indent=2, ensure_ascii=False)
                                        st.success(f"✓ Predictions saved to {pred_file}")
                                    
                                except Exception as e:
                                    st.error(f"Error generating predictions: {e}")
                                    import traceback
                                    with st.expander("Error Details"):
                                        st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Action buttons section
    st.markdown("## 📥 Save & Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to Logs", use_container_width=True):
            output_file = f"logs/analysis_{results['student_data']['student_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("logs", exist_ok=True)
            
            save_data = {
                'student_id': results['student_data']['student_id'],
                'timestamp': datetime.now().isoformat(),
                'ratings': ratings,
                'weak_category': weak_category,
                'recommendation': recommendation,
                'all_scores': all_scores
            }
            
            with open(output_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            st.success(f"✓ Saved to {output_file}")
    
    with col2:
        # Download JSON
        json_str = json.dumps({
            'student_id': results['student_data']['student_id'],
            'ratings': ratings,
            'weak_category': weak_category,
            'recommendation': recommendation,
            'all_scores': all_scores
        }, indent=2)
        
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"analysis_{results['student_data']['student_id']}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Analyze Another", type="primary", use_container_width=True):
            st.session_state.analysis_results = None
            st.rerun()
    
    # Feedback section
    with st.expander("📝 Provide Feedback (Help Improve the Model)"):
        st.markdown("Your feedback helps the model learn and improve over time.")
        
        actual_rating = st.slider(
            "What should the actual rating be?",
            0, 100,
            int(overall_rating)
        )
        
        feedback_category = st.selectbox(
            "Which category needs most improvement?",
            list(all_scores.keys()),
            index=list(all_scores.keys()).index(weak_category)
        )
        
        if st.button("Submit Feedback"):
            feedback = {
                'actual_rating': actual_rating,
                'predicted_rating': overall_rating,
                'weak_category': feedback_category
            }
            
            st.session_state.rating_model.adapt_weights(feedback)
            st.session_state.rating_model.save_model("models/student_rating_model.pkl")
            
            st.success("✓ Feedback recorded! Model has been updated.")


def show_model_performance_view():
    """Display detailed model performance metrics"""
    st.header("📊 Model Performance Dashboard")
    
    metrics = st.session_state.rating_model.get_model_performance()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Predictions", metrics['total_predictions'])
    with col2:
        st.metric("Feedback Count", metrics['feedback_count'])
    with col3:
        st.metric("Average Error", f"{metrics['average_error']:.2f}")
    with col4:
        improvement = metrics['improvement_rate']
        st.metric("Improvement Rate", f"{improvement:.2f}%", 
                 delta=f"{improvement:.1f}%" if improvement > 0 else None)
    
    st.markdown("---")
    
    # Weights visualization
    st.subheader("⚖️ Current Model Weights")
    st.markdown("These weights determine how much each category contributes to the overall rating.")
    
    weights_data = pd.DataFrame({
        'Category': list(metrics['current_weights'].keys()),
        'Weight': list(metrics['current_weights'].values()),
        'Percentage': [v * 100 for v in metrics['current_weights'].values()]
    })
    
    fig = px.bar(
        weights_data,
        x='Category',
        y='Percentage',
        title='Category Weights Distribution',
        labels={'Percentage': 'Weight (%)'},
        color='Percentage',
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Weights table
    st.dataframe(
        weights_data.style.format({'Weight': '{:.3f}', 'Percentage': '{:.1f}%'}),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Model info
    st.subheader("ℹ️ Model Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Adaptive Learning:**
        - Model adjusts weights based on feedback
        - Improves accuracy over time
        - Learns from user corrections
        """)
    
    with col2:
        st.markdown("""
        **Performance Metrics:**
        - Average Error: Lower is better
        - Improvement Rate: Positive means improving
        - Feedback Count: More feedback = better accuracy
        """)
    
    # Export model data
    if st.button("💾 Export Model Data"):
        model_data = {
            'metrics': metrics,
            'export_date': datetime.now().isoformat()
        }
        
        json_str = json.dumps(model_data, indent=2)
        st.download_button(
            label="📥 Download Model Report",
            data=json_str,
            file_name=f"model_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def show_sample_csv_creator():
    """Create sample CSV files for testing"""
    st.header("📝 Create Sample CSV")
    
    st.markdown("""
    Generate sample student report card CSV files for testing the system.
    These files contain daily records with attendance, homework, exams, and teacher comments.
    """)
    
    st.markdown("---")
    
    # Sample CSV parameters
    col1, col2 = st.columns(2)
    
    with col1:
        student_name = st.text_input("Student Name", value="Sample Student", key="sample_name")
        num_records = st.slider("Number of Daily Records", min_value=5, max_value=50, value=20, key="sample_records")
    
    with col2:
        attendance_rate = st.slider("Attendance Rate (%)", min_value=0, max_value=100, value=90, key="sample_attendance")
        homework_completion = st.slider("Homework Completion (%)", min_value=0, max_value=100, value=85, key="sample_hw")
    
    if st.button("✨ Generate Sample CSV", type="primary"):
        # Generate sample data
        dates = pd.date_range(start='2025-01-01', periods=num_records, freq='D')
        
        data = []
        for date in dates:
            # Random attendance based on rate
            is_present = np.random.random() < (attendance_rate / 100)
            attendance = "Present" if is_present else "Absent"
            
            # Random homework/classwork issues
            hw_issue = np.random.random() > (homework_completion / 100)
            cw_issue = np.random.random() > (homework_completion / 100)
            
            # Random exam marks (out of 10)
            exam1 = np.random.randint(5, 11) if is_present else 0
            exam2 = np.random.randint(5, 11) if is_present else 0
            
            # Sample comments
            comments = [
                "Good participation in class",
                "Shows improvement",
                "Needs more practice",
                "Excellent work today",
                "Attentive during lessons",
                "Could focus more",
                "Great problem solving",
                "Good communication skills"
            ]
            comment = np.random.choice(comments) if is_present else "Absent"
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'attendance': attendance,
                'HW_issue': hw_issue,
                'CW_issue': cw_issue,
                'daily_exam1_subject': 'Math',
                'daily_exam1_mark': exam1,
                'daily_exam2_subject': 'English',
                'daily_exam2_mark': exam2,
                'teacher_comment': comment
            })
        
        df = pd.DataFrame(data)
        
        # Preview
        st.subheader("👁️ Preview")
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Total Records: {len(df)}")
        
        # Download
        csv_str = df.to_csv(index=False)
        filename = f"{student_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv_str,
            file_name=filename,
            mime="text/csv",
            type="primary"
        )
        
        st.success("✓ Sample CSV generated! Click the button above to download.")
        st.info("💡 Tip: Save this file in the data/ directory to have it auto-detected by the app.")


if __name__ == "__main__":
    main()
