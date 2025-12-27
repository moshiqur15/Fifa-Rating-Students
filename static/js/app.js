// Student Rating System - Frontend JavaScript

// Global state
let currentAnalysis = null;

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Analyze student
async function analyzeStudent(event) {
    event.preventDefault();
    
    // Get form data
    const formData = {
        student_id: document.getElementById('student_id').value,
        attendance: parseFloat(document.getElementById('attendance').value),
        homework: parseFloat(document.getElementById('homework').value),
        classwork: parseFloat(document.getElementById('classwork').value),
        class_focus: parseFloat(document.getElementById('class_focus').value),
        exam: parseFloat(document.getElementById('exam').value),
        problem_solving: parseFloat(document.getElementById('problem_solving').value),
        communication: parseFloat(document.getElementById('communication').value),
        discipline: parseFloat(document.getElementById('discipline').value)
    };
    
    // Show loading
    showLoading(true);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        currentAnalysis = data;
        displayResults(data);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(data) {
    // Update overall rating
    document.getElementById('overall-rating').textContent = data.overall_rating.toFixed(1);
    document.getElementById('rating-tier').textContent = data.tier;
    document.getElementById('result-student-id').textContent = data.student_id;
    
    // Update category breakdown
    const categoryBars = document.getElementById('category-bars');
    categoryBars.innerHTML = '';
    
    Object.entries(data.all_scores).forEach(([category, score]) => {
        const barHTML = `
            <div class="category-bar">
                <div class="category-label">
                    <span>${category}</span>
                    <span>${score.toFixed(1)}/100</span>
                </div>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${score}%">
                        ${score.toFixed(0)}
                    </div>
                </div>
            </div>
        `;
        categoryBars.innerHTML += barHTML;
    });
    
    // Update recommendation
    document.getElementById('weak-category').textContent = 
        `${data.weak_category} (${data.all_scores[data.weak_category].toFixed(1)}/100)`;
    document.getElementById('recommendation-text').textContent = data.recommendation;
    
    // Update AI suggestions if available
    if (data.ai_suggestions) {
        document.getElementById('ai-section').style.display = 'block';
        document.getElementById('ai-content').textContent = data.ai_suggestions;
    } else {
        document.getElementById('ai-section').style.display = 'none';
    }
    
    // Show results
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

// Close results
function closeResults() {
    document.getElementById('results').style.display = 'none';
    currentAnalysis = null;
}

// Submit feedback
async function submitFeedback() {
    if (!currentAnalysis) {
        alert('No analysis to provide feedback for');
        return;
    }
    
    const actualRating = parseFloat(document.getElementById('actual-rating').value);
    
    if (isNaN(actualRating) || actualRating < 0 || actualRating > 100) {
        alert('Please enter a valid rating between 0 and 100');
        return;
    }
    
    const feedbackData = {
        student_id: currentAnalysis.student_id,
        predicted_rating: currentAnalysis.overall_rating,
        actual_rating: actualRating,
        weak_category: currentAnalysis.weak_category
    };
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        });
        
        if (!response.ok) {
            throw new Error('Feedback submission failed');
        }
        
        alert('✓ Feedback submitted successfully! The model will learn from your input.');
        document.getElementById('actual-rating').value = '';
        
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Handle CSV upload
async function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('CSV upload failed');
        }
        
        const data = await response.json();
        alert(`✓ Successfully analyzed ${data.count} students!\n\nResults:\n${data.results.map(r => `${r.student_id}: ${r.overall_rating.toFixed(1)}/100`).join('\n')}`);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
        event.target.value = ''; // Reset file input
    }
}

// Download sample CSV
function downloadSampleCSV() {
    const csvContent = `student_id,attendance,homework,classwork,class_focus,exam,problem_solving,communication,discipline
STU001,85,8,7,75,72,8,7,8
STU002,70,6,6,60,55,6,6,5
STU003,95,9,9,90,88,9,8,9`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_students.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Show/hide loading overlay
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

// Show performance modal
async function showPerformance() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/performance');
        if (!response.ok) {
            throw new Error('Failed to load performance data');
        }
        
        const data = await response.json();
        displayPerformance(data.metrics);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display performance metrics
function displayPerformance(metrics) {
    const content = document.getElementById('performance-content');
    
    const html = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Predictions</div>
                <div class="metric-value">${metrics.total_predictions}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Feedback Count</div>
                <div class="metric-value">${metrics.feedback_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Average Error</div>
                <div class="metric-value">${metrics.average_error.toFixed(2)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Improvement Rate</div>
                <div class="metric-value">${metrics.improvement_rate.toFixed(2)}%</div>
            </div>
        </div>
        
        <h4 style="margin-top: 2rem; margin-bottom: 1rem;">Current Weights</h4>
        <div class="weights-table">
            ${Object.entries(metrics.current_weights).map(([key, value]) => `
                <div class="weight-row">
                    <span>${key}</span>
                    <span>${value.toFixed(3)} (${(value * 100).toFixed(1)}%)</span>
                </div>
            `).join('')}
        </div>
    `;
    
    content.innerHTML = html;
    
    // Add dynamic styles
    const style = document.createElement('style');
    style.textContent = `
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        .metric-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }
        .weights-table {
            background: var(--bg-secondary);
            border-radius: 8px;
            overflow: hidden;
        }
        .weight-row {
            display: flex;
            justify-content: space-between;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
        }
        .weight-row:last-child {
            border-bottom: none;
        }
    `;
    if (!document.getElementById('dynamic-metrics-style')) {
        style.id = 'dynamic-metrics-style';
        document.head.appendChild(style);
    }
    
    document.getElementById('performance-modal').style.display = 'flex';
}

// Close performance modal
function closePerformance() {
    document.getElementById('performance-modal').style.display = 'none';
}

// Close modals on outside click
window.onclick = function(event) {
    const performanceModal = document.getElementById('performance-modal');
    if (event.target === performanceModal) {
        closePerformance();
    }
}

// Check API health on load
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('API Health:', data);
        
        if (!data.groq_available) {
            console.warn('Groq API not configured. AI suggestions will not be available.');
        }
    } catch (error) {
        console.error('Failed to check API health:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    console.log('Student Rating System loaded successfully!');
});
