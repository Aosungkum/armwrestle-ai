// Authentication Module
class AuthManager {
    constructor() {
        this.API_URL = 'https://armwrestle-ai-production.up.railway.app/api';
        this.token = localStorage.getItem('auth_token');
        // Safe JSON parsing with error handling
        try {
            const userStr = localStorage.getItem('user');
            this.user = userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('Error parsing user data from localStorage:', error);
            this.user = null;
        }
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

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                return { success: false, error: errorData.error || 'Login failed' };
            }

            const data = await response.json();

            if (data.success) {
                this.token = data.token;
                this.user = data.user;
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user', JSON.stringify(this.user));
                return { success: true, user: this.user };
            } else {
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Login failed' };
        }
    }

    // Logout user
    logout() {
        try {
            // Clear token and user data
            this.token = null;
            this.user = null;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            
            // Update UI immediately
            if (typeof updateUIForAuthState === 'function') {
                updateUIForAuthState();
            }
            
            // Determine redirect path based on current page
            const currentPath = window.location.pathname;
            const redirectPath = currentPath.includes('dashboard.html') ? 'index.html' : './index.html';
            
            // Redirect to home page
            window.location.href = redirectPath;
        } catch (error) {
            console.error('Logout error:', error);
            // Fallback: try to redirect anyway
            window.location.href = 'index.html';
        }
    }

    // Get authorization header
    getAuthHeader() {
        if (!this.token) {
            return {};
        }
        return {
            'Authorization': `Bearer ${this.token}`
        };
    }

    // Get user stats
    async getStats() {
        try {
            const response = await fetch(`${this.API_URL}/stats`, {
                headers: {
                    ...this.getAuthHeader()
                }
            });

            if (!response.ok) {
                console.error('Failed to fetch stats:', response.status);
                return { success: false, error: 'Failed to fetch statistics' };
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching stats:', error);
            return { success: false, error: 'Failed to fetch statistics' };
        }
    }

    // Get analysis history
    async getHistory() {
        try {
            const response = await fetch(`${this.API_URL}/history`, {
                headers: {
                    ...this.getAuthHeader()
                }
            });

            if (!response.ok) {
                console.error('Failed to fetch history:', response.status);
                return { success: false, error: 'Failed to fetch history' };
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching history:', error);
            return { success: false, error: 'Failed to fetch history' };
        }
    }

    // Create payment order for plan upgrade
    async createPaymentOrder(plan) {
        try {
            const formData = new FormData();
            formData.append('plan', plan);

            const response = await fetch(`${this.API_URL}/payment/create-order`, {
                method: 'POST',
                headers: {
                    ...this.getAuthHeader()
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to create payment order');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Payment order creation error:', error);
            return { success: false, error: 'Failed to create payment order' };
        }
    }

    // Verify payment and upgrade plan
    async verifyPayment(orderId, paymentId, signature) {
        try {
            const formData = new FormData();
            formData.append('razorpay_order_id', orderId);
            formData.append('razorpay_payment_id', paymentId);
            formData.append('razorpay_signature', signature);

            const response = await fetch(`${this.API_URL}/payment/verify`, {
                method: 'POST',
                headers: {
                    ...this.getAuthHeader()
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Payment verification failed');
            }

            const data = await response.json();
            
            if (data.success && data.user) {
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(this.user));
            }

            return data;
        } catch (error) {
            console.error('Payment verification error:', error);
            return { success: false, error: 'Payment verification failed' };
        }
    }

    // Legacy upgrade plan (for backward compatibility)
    async upgradePlan(plan) {
        // Redirect to payment flow
        return await this.initiatePayment(plan);
    }

    // Initiate Razorpay payment
    async initiatePayment(plan) {
        try {
            // Create payment order
            const orderData = await this.createPaymentOrder(plan);
            
            if (!orderData.success) {
                return { success: false, error: orderData.error || 'Failed to create payment order' };
            }

            const planNames = {
                'pro': 'Pro Plan',
                'coach': 'Coach Plan'
            };

            const planPrices = {
                'pro': '₹699',
                'coach': '₹2,499'
            };

            // Razorpay checkout options
            const options = {
                key: orderData.key_id,
                amount: orderData.amount,
                currency: orderData.currency,
                name: 'ArmWrestle AI',
                description: `Subscription: ${planNames[plan] || plan}`,
                order_id: orderData.order_id,
                handler: async (response) => {
                    // Payment successful, verify payment
                    const verifyResult = await this.verifyPayment(
                        response.razorpay_order_id,
                        response.razorpay_payment_id,
                        response.razorpay_signature
                    );

                    if (verifyResult.success) {
                        showNotification('Payment successful! Plan upgraded.', 'success');
                        if (typeof updateUIForAuthState === 'function') {
                            updateUIForAuthState();
                        }
                        if (typeof loadStats === 'function') {
                            await loadStats();
                        }
                    } else {
                        showNotification(verifyResult.error || 'Payment verification failed', 'error');
                    }
                },
                prefill: {
                    name: this.user?.name || '',
                    email: this.user?.email || '',
                },
                theme: {
                    color: '#e74c3c'
                },
                modal: {
                    ondismiss: () => {
                        showNotification('Payment cancelled', 'warning');
                    }
                }
            };

            // Open Razorpay checkout
            const razorpay = new Razorpay(options);
            razorpay.open();

            return { success: true, message: 'Payment window opened' };
        } catch (error) {
            console.error('Payment initiation error:', error);
            return { success: false, error: 'Failed to initiate payment' };
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
    
    if (!modal || !loginForm || !registerForm) return;
    
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
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.add('hidden');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('hidden');
}

function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) dropdown.classList.toggle('hidden');
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
        if (user && loginBtn && userMenu && userName && userPlan) {
            loginBtn.classList.add('hidden');
            userMenu.classList.remove('hidden');
            userName.textContent = user.name || 'User';
            userPlan.textContent = (user.plan || 'free').toUpperCase();
            userPlan.className = `plan-badge plan-${user.plan || 'free'}`;
        }
    } else {
        if (loginBtn) loginBtn.classList.remove('hidden');
        if (userMenu) userMenu.classList.add('hidden');
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
            <div class="stat-value">${(stats.plan || 'free').toUpperCase()}</div>
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