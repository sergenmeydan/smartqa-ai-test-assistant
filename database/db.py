import sqlite3
from datetime import datetime
import os

DATABASE_PATH = "database/smartqa.db"

def get_connection():
    """SQLite bağlantısı oluştur"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Dict gibi erişim için
    return conn

def init_database():
    """Database tablolarını oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Projects tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Test Scenarios tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            steps TEXT,  -- JSON formatında
            priority TEXT DEFAULT 'medium',  -- low, medium, high
            status TEXT DEFAULT 'active',  -- draft, active, archived
            created_by_ai BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # Test Executions tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER NOT NULL,
            status TEXT NOT NULL,  -- pass, fail, blocked, skipped
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (scenario_id) REFERENCES test_scenarios (id)
        )
    ''')
    
    # Bug Reports tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bug_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            severity TEXT DEFAULT 'medium',  -- low, medium, high, critical
            description TEXT,
            steps_to_reproduce TEXT,
            expected_result TEXT,
            actual_result TEXT,
            ai_generated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (execution_id) REFERENCES test_executions (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database başarıyla oluşturuldu!")

# İlk çalıştırmada database'i oluştur
if not os.path.exists(DATABASE_PATH):
    os.makedirs("database", exist_ok=True)
    init_database()