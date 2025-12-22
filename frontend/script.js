// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const videoInput = document.getElementById('videoInput');
const videoPreview = document.getElementById('videoPreview');
const previewVideo = document.getElementById('previewVideo');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const newAnalysisBtn = document.getElementById('newAnalysis');
const progressFill = document.getElementById('progressFill');

let selectedFile = null;

// Upload Area Click Handler
uploadArea.addEventListener('click', () => {
    videoInput.click();
});

// Drag and Drop Handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--primary)';
    uploadArea.style.background = '#f8f9fa';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--accent)';
    uploadArea.style.background = 'white';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--accent)';
    uploadArea.style.background = 'white';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File Input Change Handler
videoInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Handle File Selection
function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/quicktime'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a valid video file (MP4, MOV, or AVI)');
        return;
    }
    
    // Validate file size (100MB)
    if (file.size > 100 * 1024 * 1024) {
        alert('File size must be less than 100MB');
        return;
    }
    
    selectedFile = file;
    
    // Show video preview
    const url = URL.createObjectURL(file);
    previewVideo.src = url;
    
    uploadArea.classList.add('hidden');
    videoPreview.classList.remove('hidden');
}

// Analyze Button Handler
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    // Hide preview, show loading
    videoPreview.classList.add('hidden');
    loadingState.classList.remove('hidden');
    
    // Simulate analysis (replace with actual API call)
    await simulateAnalysis();
    
    // Show results
    loadingState.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    // Display mock results
    displayResults();
});

// Simulate Analysis Process
function simulateAnalysis() {
    return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            progressFill.style.width = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                resolve();
            }
        }, 100);
    });
}

// Display Analysis Results
function displayResults() {
    // Technique Results
    const techniqueResults = document.getElementById('techniqueResults');
    techniqueResults.innerHTML = `
        <div class="technique-badge">Primary: Top Roll</div>
        <div class="technique-badge">Transition: Hook Attempt at 0:04</div>
        <p style="margin-top: 1rem; color: var(--text-light);">
            You initiated with a top roll technique and attempted to transition to a hook at the 4-second mark. 
            The transition was partially successful but lacked power.
        </p>
    `;
    
    // Injury Risk Results
    const injuryResults = document.getElementById('injuryResults');
    injuryResults.innerHTML = `
        <div class="risk-item risk-high">
            <div class="risk-title">⚠️ High Risk: Elbow Ligament Stress</div>
            <div class="risk-description">
                Detected high elbow flare angle (42°) at 0:07. This increases UCL injury risk.
                Recommended: Reduce elbow angle to below 35° during engagement.
            </div>
        </div>
        <div class="risk-item risk-medium">
            <div class="risk-title">⚠️ Medium Risk: Wrist Collapse</div>
            <div class="risk-description">
                Wrist lost stability at 0:11, showing 15° backward flex under pressure.
                Recommended: Focus on wrist curls and static holds.
            </div>
        </div>
        <div class="risk-item risk-low">
            <div class="risk-title">✓ Low Risk: Shoulder Position</div>
            <div class="risk-description">
                Shoulder alignment maintained throughout match. Good form detected.
            </div>
        </div>
    `;
    
    // Strength Analysis Results
    const strengthResults = document.getElementById('strengthResults');
    strengthResults.innerHTML = `
        <div class="stat-row">
            <span class="stat-label">Back Pressure</span>
            <span class="stat-value">Strong (7/10)</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Wrist Control</span>
            <span class="stat-value">Weak (4/10)</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Side Pressure</span>
            <span class="stat-value">Moderate (6/10)</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Endurance Drop</span>
            <span class="stat-value">23% after 6 seconds</span>
        </div>
        <p style="margin-top: 1rem; padding: 1rem; background: #fff3e0; border-radius: 8px;">
            <strong>Analysis:</strong> You lost primarily due to wrist weakness, not arm strength. 
            Your back pressure was solid, but wrist collapsed under opponent's pronation attack.
        </p>
    `;
    
    // Training Recommendations
    const trainingResults = document.getElementById('trainingResults');
    trainingResults.innerHTML = `
        <ul class="recommendation-list">
            <li><strong>Wrist Curls (3x15)</strong> - Focus on pronation strength to prevent collapse</li>
            <li><strong>Static Wrist Holds (4x30s)</strong> - Build endurance in top position</li>
            <li><strong>Elbow Position Drills</strong> - Practice keeping elbow angle below 35°</li>
            <li><strong>Hook Transition Practice</strong> - Improve power during technique changes</li>
            <li><strong>Endurance Training</strong> - Add 2-3 longer rounds (15s+) to build stamina</li>
        </ul>
        <div style="margin-top: 1.5rem; padding: 1rem; background: #e8f5e9; border-radius: 8px;">
            <strong>Recommended Focus:</strong> Your primary weakness is wrist pronation under load. 
            Follow this 3-week plan focusing on pronator exercises and wrist stability work.
        </div>
    `;
}

// New Analysis Button Handler
newAnalysisBtn.addEventListener('click', () => {
    // Reset everything
    selectedFile = null;
    videoInput.value = '';
    previewVideo.src = '';
    progressFill.style.width = '0%';
    
    // Show upload area again
    resultsSection.classList.add('hidden');
    uploadArea.classList.remove('hidden');
});

// Smooth Scroll for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// API Call Function (for backend integration)
async function analyzeVideo(videoFile) {
    const formData = new FormData();
    formData.append('video', videoFile);
    
    try {
        const response = await fetch('http://localhost:8000/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error analyzing video:', error);
        alert('Failed to analyze video. Please try again.');
        return null;
    }
}

// Function to display real API results
function displayAPIResults(data) {
    // Technique Results
    document.getElementById('techniqueResults').innerHTML = `
        <div class="technique-badge">Primary: ${data.technique.primary}</div>
        ${data.technique.transitions.map(t => 
            `<div class="technique-badge">Transition: ${t.type} at ${t.timestamp}s</div>`
        ).join('')}
        <p style="margin-top: 1rem; color: var(--text-light);">${data.technique.description}</p>
    `;
    
    // Injury Risks
    document.getElementById('injuryResults').innerHTML = data.risks.map(risk => `
        <div class="risk-item risk-${risk.level}">
            <div class="risk-title">${risk.level === 'high' ? '⚠️' : '✓'} ${risk.level === 'high' ? 'High' : risk.level === 'medium' ? 'Medium' : 'Low'} Risk: ${risk.title}</div>
            <div class="risk-description">${risk.description}</div>
        </div>
    `).join('');
    
    // Strength Analysis
    document.getElementById('strengthResults').innerHTML = Object.entries(data.strength).map(([key, value]) => `
        <div class="stat-row">
            <span class="stat-label">${key}</span>
            <span class="stat-value">${value}</span>
        </div>
    `).join('') + `
        <p style="margin-top: 1rem; padding: 1rem; background: #fff3e0; border-radius: 8px;">
            <strong>Analysis:</strong> ${data.strength.summary}
        </p>
    `;
    
    // Training Recommendations
    document.getElementById('trainingResults').innerHTML = `
        <ul class="recommendation-list">
            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    `;
}