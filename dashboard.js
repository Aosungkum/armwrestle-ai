// Dashboard functionality

// Check authentication on load
document.addEventListener('DOMContentLoaded', async () => {
    // Redirect if not logged in
    if (!auth.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Update user info
    const user = auth.getCurrentUser();
    if (user) {
        const userNameEl = document.getElementById('userName');
        const dashboardUserNameEl = document.getElementById('dashboardUserName');
        const userPlanEl = document.getElementById('userPlan');
        
        if (userNameEl) userNameEl.textContent = user.name || 'User';
        if (dashboardUserNameEl) dashboardUserNameEl.textContent = user.name || 'User';
        if (userPlanEl) {
            userPlanEl.textContent = (user.plan || 'free').toUpperCase();
            userPlanEl.className = `plan-badge plan-${user.plan || 'free'}`;
        }
    }

    // Load dashboard data
    await loadStats();
    await loadHistory();
});

// Toggle user dropdown
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('hidden');
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const userMenu = document.querySelector('.user-menu');
    const dropdown = document.getElementById('userDropdown');
    
    if (userMenu && !userMenu.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

// Load user statistics
async function loadStats() {
    try {
        const response = await auth.getStats();
        
        if (response && response.success) {
            const stats = response.stats;
            
            document.getElementById('statTotalAnalyses').textContent = stats.total_analyses || 0;
            document.getElementById('statTopTechnique').textContent = stats.most_common_technique || 'N/A';
            document.getElementById('statDailyUsage').textContent = `${stats.daily_usage || 0}/${stats.plan === 'free' ? '1' : '∞'}`;
            document.getElementById('statPlan').textContent = stats.plan.toUpperCase();
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showNotification('Failed to load statistics', 'error');
    }
}

// Load analysis history
async function loadHistory() {
    const loadingEl = document.getElementById('loadingHistory');
    const containerEl = document.getElementById('historyContainer');
    const emptyStateEl = document.getElementById('emptyState');
    
    loadingEl.style.display = 'block';
    containerEl.innerHTML = '';
    emptyStateEl.classList.add('hidden');
    
    try {
        const response = await auth.getHistory();
        
        loadingEl.style.display = 'none';
        
        if (response && response.success && response.analyses.length > 0) {
            displayHistory(response.analyses);
        } else {
            emptyStateEl.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error loading history:', error);
        loadingEl.style.display = 'none';
        showNotification('Failed to load history', 'error');
    }
}

// Display history items
function displayHistory(analyses) {
    const container = document.getElementById('historyContainer');
    
    container.innerHTML = analyses.map(analysis => {
        const date = new Date(analysis.created_at);
        const dateStr = date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
        const timeStr = date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Count high risks
        const risks = JSON.parse(analysis.risk_data || '[]');
        const highRisks = risks.filter(r => r.level === 'high').length;
        
        return `
            <div class="history-card" onclick="showAnalysisDetail(${analysis.id})">
                <div class="history-card-header">
                    <div class="history-technique">
                        <span class="technique-badge">${analysis.technique_primary || 'Unknown'}</span>
                    </div>
                    <div class="history-date">
                        <div>${dateStr}</div>
                        <div class="history-time">${timeStr}</div>
                    </div>
                </div>
                <div class="history-card-body">
                    <div class="history-video-name">
                        📹 ${analysis.video_filename}
                    </div>
                    <div class="history-stats">
                        <span class="history-stat">
                            ${risks.length} Risk${risks.length !== 1 ? 's' : ''}
                        </span>
                        ${highRisks > 0 ? `
                            <span class="history-stat risk-high">
                                ⚠️ ${highRisks} High
                            </span>
                        ` : ''}
                    </div>
                </div>
                <div class="history-card-footer">
                    <span class="view-details">View Details →</span>
                </div>
            </div>
        `;
    }).join('');
}

// Show analysis detail
function showAnalysisDetail(analysisId) {
    // Get analysis from auth history
    auth.getHistory().then(response => {
        if (response && response.success) {
            const analysis = response.analyses.find(a => a.id === analysisId);
            
            if (analysis) {
                const modal = document.getElementById('detailModal');
                const title = document.getElementById('detailTitle');
                const content = document.getElementById('detailContent');
                
                const date = new Date(analysis.created_at);
                const dateStr = date.toLocaleDateString('en-US', { 
                    month: 'long', 
                    day: 'numeric', 
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const technique = JSON.parse(analysis.technique_data || '{}');
                const risks = JSON.parse(analysis.risk_data || '[]');
                const strength = JSON.parse(analysis.strength_data || '{}');
                const recommendations = JSON.parse(analysis.recommendations || '[]');
                
                title.textContent = `Analysis - ${dateStr}`;
                
                content.innerHTML = `
                    <div class="detail-section">
                        <h3>📹 Video</h3>
                        <p>${analysis.video_filename}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h3>🎯 Technique Detected</h3>
                        <div class="technique-badge">${analysis.technique_primary}</div>
                        <p style="margin-top: 0.5rem;">${technique.description || ''}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h3>⚠️ Injury Risk Assessment</h3>
                        ${risks.map(risk => `
                            <div class="risk-item risk-${risk.level}">
                                <div class="risk-title">
                                    ${risk.level === 'high' ? '⚠️' : risk.level === 'medium' ? '⚡' : '✓'} 
                                    ${risk.level.charAt(0).toUpperCase() + risk.level.slice(1)} Risk: ${risk.title}
                                </div>
                                <div class="risk-description">${risk.description}</div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="detail-section">
                        <h3>💪 Strength Analysis</h3>
                        ${Object.entries(strength).filter(([key]) => key !== 'summary').map(([key, value]) => `
                            <div class="stat-row">
                                <span class="stat-label">${key}</span>
                                <span class="stat-value">${value}</span>
                            </div>
                        `).join('')}
                        ${strength.summary ? `
                            <div class="analysis-summary">
                                <strong>Analysis:</strong> ${strength.summary}
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="detail-section">
                        <h3>🏋️ Training Recommendations</h3>
                        <ul class="recommendation-list">
                            ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                `;
                
                modal.classList.remove('hidden');
            }
        }
    });
}

// Close detail modal
function closeDetailModal() {
    document.getElementById('detailModal').classList.add('hidden');
}

// Show upgrade modal
function showUpgradeModal() {
    document.getElementById('upgradeModal').classList.remove('hidden');
}

// Close upgrade modal
function closeUpgradeModal() {
    document.getElementById('upgradeModal').classList.add('hidden');
}

// Handle upgrade - initiates Razorpay payment
async function handleUpgrade(plan) {
    try {
        showNotification('Opening payment gateway...', 'info');
        const result = await auth.initiatePayment(plan);
        
        if (result && result.success) {
            // Payment window opened, wait for user to complete payment
            // The payment handler in auth.js will handle success/error
            closeUpgradeModal();
        } else {
            showNotification(result.error || 'Failed to initiate payment. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Upgrade error:', error);
        showNotification('Upgrade failed. Please try again.', 'error');
    }
}

// Refresh stats
async function refreshStats() {
    showNotification('Refreshing statistics...', 'info');
    await loadStats();
    await loadHistory();
    showNotification('Statistics updated!', 'success');
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}