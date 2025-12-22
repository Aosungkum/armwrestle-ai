// Authentication Module
class AuthManager {
    constructor() {
        this.API_URL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('auth_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }

    // Check if user is logged in
    isAuthenticated() {
        return !!this.token;
    }

    // Get current user
    getCurrentUser() {
        return this.user;
    }

    // Register new user
    async register(email, name) {
        try {
            const formData = new FormData();
            formData.append('email', email);
            formData.append('name', name);

            const response = await fetch(`${this.API_URL}/register`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.token = data.token;
                this.user = data.user;
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                return { success: true, user: this.user };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: 'Registration failed' };
        }
    }

    // Login user
    async login(email) {
        try {
            const formData = new FormData();
            formData.append('email', email);

            const response = await fetch(`${this.API_URL}/login`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.token = data.token;
                this.user = data.user;
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                return { success: true, user: this.user };
            } else {
                return { success: false, error: 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Login failed' };
        }
    }

    // Logout user
    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        window.location.href = '/';
    }

    // Get authorization header
    getAuthHeader() {
        return {
            'Authorization': `Bearer ${this.token}`
        };
    }

    // Get user stats
    async getStats() {
        try {
            const response = await fetch(`${this.API_URL}/stats`, {
                headers: this.getAuthHeader()
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching stats:', error);
            return null;
        }
    }

    // Get analysis history
    async getHistory() {
        try {
            const response = await fetch(`${this.API_URL}/history`, {
                headers: this.getAuthHeader()
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching history:', error);
            return null;
        }
    }

    // Upgrade plan
    async upgradePlan(plan) {
        try {
            const formData = new FormData();
            formData.append('plan', plan);

            const response = await fetch(`${this.API_URL}/upgrade`, {
                method: 'POST',
                headers: this.getAuthHeader(),
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                this.user.plan = plan;
                localStorage.setItem('user', JSON.stringify(this.user));
            }

            return data;
        } catch (error) {
            console.error('Upgrade error:', error);
            return { success: false, error: 'Upgrade failed' };
        }
    }
}

// Initialize auth manager
const auth = new AuthManager();

// Show/hide auth modal
function showAuthModal(mode = 'login') {
    const modal = document.getElementById('authModal');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    modal.classList.remove('hidden');
    
    if (mode === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    }
}

function hideAuthModal() {
    document.getElementById('authModal').classList.add('hidden');
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    const result = await auth.login(email);
    
    if (result.success) {
        hideAuthModal();
        updateUIForAuthState();
        showNotification('Logged in successfully!', 'success');
    } else {
        showNotification(result.error || 'Login failed', 'error');
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Login';
}

// Handle registration
async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const name = document.getElementById('registerName').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';
    
    const result = await auth.register(email, name);
    
    if (result.success) {
        hideAuthModal();
        updateUIForAuthState();
        showNotification('Account created successfully!', 'success');
    } else {
        showNotification(result.error || 'Registration failed', 'error');
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Create Account';
}

// Update UI based on auth state
function updateUIForAuthState() {
    const loginBtn = document.getElementById('loginBtn');
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    const userPlan = document.getElementById('userPlan');
    
    if (auth.isAuthenticated()) {
        const user = auth.getCurrentUser();
        loginBtn.classList.add('hidden');
        userMenu.classList.remove('hidden');
        userName.textContent = user.name;
        userPlan.textContent = user.plan.toUpperCase();
        userPlan.className = `plan-badge plan-${user.plan}`;
    } else {
        loginBtn.classList.remove('hidden');
        userMenu.classList.add('hidden');
    }
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

// View user history
async function viewHistory() {
    const history = await auth.getHistory();
    
    if (history && history.success) {
        displayHistory(history.analyses);
    } else {
        showNotification('Failed to load history', 'error');
    }
}

// View user stats
async function viewStats() {
    const stats = await auth.getStats();
    
    if (stats && stats.success) {
        displayStats(stats.stats);
    } else {
        showNotification('Failed to load stats', 'error');
    }
}

// Display history in modal
function displayHistory(analyses) {
    const historyModal = document.getElementById('historyModal');
    const historyList = document.getElementById('historyList');
    
    historyList.innerHTML = analyses.map(analysis => `
        <div class="history-item">
            <div class="history-header">
                <strong>${analysis.technique_primary}</strong>
                <span class="history-date">${new Date(analysis.created_at).toLocaleDateString()}</span>
            </div>
            <div class="history-video">${analysis.video_filename}</div>
            <div class="history-risks">
                ${analysis.risk_data.length} risk(s) detected
            </div>
        </div>
    `).join('');
    
    historyModal.classList.remove('hidden');
}

// Display stats in modal
function displayStats(stats) {
    const statsModal = document.getElementById('statsModal');
    const statsContent = document.getElementById('statsContent');
    
    statsContent.innerHTML = `
        <div class="stat-card">
            <h3>Total Analyses</h3>
            <div class="stat-value">${stats.total_analyses}</div>
        </div>
        <div class="stat-card">
            <h3>Most Used Technique</h3>
            <div class="stat-value">${stats.most_common_technique || 'N/A'}</div>
        </div>
        <div class="stat-card">
            <h3>Today's Usage</h3>
            <div class="stat-value">${stats.daily_usage}</div>
        </div>
        <div class="stat-card">
            <h3>Current Plan</h3>
            <div class="stat-value">${stats.plan.toUpperCase()}</div>
        </div>
    `;
    
    statsModal.classList.remove('hidden');
}

// Initialize auth state on page load
document.addEventListener('DOMContentLoaded', () => {
    updateUIForAuthState();
    
    // Check if user needs to login for analysis
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        const originalClick = analyzeBtn.onclick;
        analyzeBtn.onclick = async (e) => {
            if (!auth.isAuthenticated()) {
                showNotification('Please login to analyze videos', 'warning');
                showAuthModal('login');
                return;
            }
            if (originalClick) originalClick(e);
        };
    }
});