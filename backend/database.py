import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class Database:
    def __init__(self, db_path: str = "armwrestle.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                plan TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_filename TEXT NOT NULL,
                technique_primary TEXT,
                technique_data TEXT,
                risk_data TEXT,
                strength_data TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Usage stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # User operations
    def create_user(self, email: str, name: str) -> int:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (email, name) VALUES (?, ?)',
                (email, name)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            # User already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_user_plan(self, user_id: int, plan: str):
        """Update user's subscription plan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE users SET plan = ? WHERE id = ?',
            (plan, user_id)
        )
        conn.commit()
        conn.close()
    
    # Analysis operations
    def save_analysis(self, user_id: Optional[int], video_filename: str, 
                     analysis_data: Dict[str, Any]) -> int:
        """Save video analysis results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        technique = analysis_data.get('technique', {})
        
        cursor.execute('''
            INSERT INTO analyses 
            (user_id, video_filename, technique_primary, technique_data, 
             risk_data, strength_data, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            video_filename,
            technique.get('primary', ''),
            json.dumps(technique),
            json.dumps(analysis_data.get('risks', [])),
            json.dumps(analysis_data.get('strength', {})),
            json.dumps(analysis_data.get('recommendations', []))
        ))
        
        conn.commit()
        analysis_id = cursor.lastrowid
        conn.close()
        
        return analysis_id
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """Get analysis by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            # Parse JSON fields
            data['technique_data'] = json.loads(data['technique_data'])
            data['risk_data'] = json.loads(data['risk_data'])
            data['strength_data'] = json.loads(data['strength_data'])
            data['recommendations'] = json.loads(data['recommendations'])
            return data
        return None
    
    def get_user_analyses(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's recent analyses"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analyses 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        analyses = []
        for row in rows:
            data = dict(row)
            data['technique_data'] = json.loads(data['technique_data'])
            data['risk_data'] = json.loads(data['risk_data'])
            data['strength_data'] = json.loads(data['strength_data'])
            data['recommendations'] = json.loads(data['recommendations'])
            analyses.append(data)
        
        return analyses
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute(
            'SELECT COUNT(*) as count FROM analyses WHERE user_id = ?',
            (user_id,)
        )
        total_analyses = cursor.fetchone()['count']
        
        # Most common technique
        cursor.execute('''
            SELECT technique_primary, COUNT(*) as count 
            FROM analyses 
            WHERE user_id = ? 
            GROUP BY technique_primary 
            ORDER BY count DESC 
            LIMIT 1
        ''', (user_id,))
        
        most_common = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_analyses': total_analyses,
            'most_common_technique': most_common['technique_primary'] if most_common else None,
            'technique_count': most_common['count'] if most_common else 0
        }
    
    # Usage tracking
    def log_action(self, user_id: Optional[int], action: str):
        """Log user action for analytics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO usage_stats (user_id, action) VALUES (?, ?)',
            (user_id, action)
        )
        conn.commit()
        conn.close()
    
    def get_daily_usage(self, user_id: int) -> int:
        """Get number of analyses today"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM analyses 
            WHERE user_id = ? 
            AND DATE(created_at) = DATE('now')
        ''', (user_id,))
        
        count = cursor.fetchone()['count']
        conn.close()
        
        return count
    
    def check_usage_limit(self, user_id: int, plan: str) -> bool:
        """Check if user has exceeded their plan limits"""
        daily_usage = self.get_daily_usage(user_id)
        
        limits = {
            'free': 1,
            'pro': float('inf'),
            'coach': float('inf')
        }
        
        return daily_usage < limits.get(plan, 1)