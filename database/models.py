from database.db import get_connection
import json
from datetime import datetime

# ============= PROJECTS =============

def create_project(name, url, description):
    """Yeni proje oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (name, url, description) VALUES (?, ?, ?)",
        (name, url, description)
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id

def get_all_projects():
    """Tüm projeleri getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
    projects = cursor.fetchall()
    conn.close()
    return projects

def get_project_by_id(project_id):
    """ID'ye göre proje getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    conn.close()
    return project

def delete_project(project_id):
    """Proje sil"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# ============= TEST SCENARIOS =============

def create_test_scenario(project_id, title, description, steps, priority="medium", created_by_ai=False):
    """Yeni test senaryosu oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Steps'i JSON string'e çevir
    steps_json = json.dumps(steps, ensure_ascii=False)
    
    cursor.execute(
        """INSERT INTO test_scenarios 
           (project_id, title, description, steps, priority, created_by_ai) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (project_id, title, description, steps_json, priority, created_by_ai)
    )
    conn.commit()
    scenario_id = cursor.lastrowid
    conn.close()
    return scenario_id

def get_scenarios_by_project(project_id):
    """Projeye ait tüm test senaryolarını getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM test_scenarios WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,)
    )
    scenarios = cursor.fetchall()
    conn.close()
    return scenarios

def get_scenario_by_id(scenario_id):
    """ID'ye göre test senaryosu getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_scenarios WHERE id = ?", (scenario_id,))
    scenario = cursor.fetchone()
    conn.close()
    return scenario

# ============= TEST SCENARIOS ============= 

def update_test_scenario(scenario_id, title, description, steps, priority):
    """Test senaryosunu güncelle"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Steps'i JSON string'e çevir
    if isinstance(steps, list):
        steps_json = json.dumps(steps, ensure_ascii=False)
    else:
        steps_json = steps
    
    cursor.execute(
        """UPDATE test_scenarios 
           SET title = ?, description = ?, steps = ?, priority = ? 
           WHERE id = ?""",
        (title, description, steps_json, priority, scenario_id)
    )
    conn.commit()
    conn.close()

def delete_test_scenario(scenario_id):
    """Test senaryosunu sil"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # İlk önce bu senaryoya ait execution'ları sil
    cursor.execute("DELETE FROM test_executions WHERE scenario_id = ?", (scenario_id,))
    
    # Sonra senaryoyu sil
    cursor.execute("DELETE FROM test_scenarios WHERE id = ?", (scenario_id,))
    
    conn.commit()
    conn.close()

# ============= TEST EXECUTIONS =============

def create_test_execution(scenario_id, status, notes=""):
    """Test execution oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_executions (scenario_id, status, notes) VALUES (?, ?, ?)",
        (scenario_id, status, notes)
    )
    conn.commit()
    execution_id = cursor.lastrowid
    conn.close()
    return execution_id

def get_executions_by_scenario(scenario_id):
    """Senaryoya ait tüm execution'ları getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM test_executions WHERE scenario_id = ? ORDER BY executed_at DESC",
        (scenario_id,)
    )
    executions = cursor.fetchall()
    conn.close()
    return executions

# ============= BUG REPORTS =============

def create_bug_report(execution_id, title, severity, description, 
                     steps_to_reproduce, expected_result, actual_result, ai_generated=False):
    """Bug raporu oluştur"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO bug_reports 
           (execution_id, title, severity, description, steps_to_reproduce, 
            expected_result, actual_result, ai_generated) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (execution_id, title, severity, description, steps_to_reproduce, 
         expected_result, actual_result, ai_generated)
    )
    conn.commit()
    bug_id = cursor.lastrowid
    conn.close()
    return bug_id

def get_all_bug_reports():
    """Tüm bug raporlarını getir"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bug_reports ORDER BY created_at DESC")
    bugs = cursor.fetchall()
    conn.close()
    return bugs

# ============= İSTATİSTİKLER =============

def get_dashboard_stats():
    """Dashboard için istatistikler"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Toplam proje sayısı
    cursor.execute("SELECT COUNT(*) as count FROM projects")
    total_projects = cursor.fetchone()['count']
    
    # Toplam test senaryosu
    cursor.execute("SELECT COUNT(*) as count FROM test_scenarios")
    total_scenarios = cursor.fetchone()['count']
    
    # Toplam execution
    cursor.execute("SELECT COUNT(*) as count FROM test_executions")
    total_executions = cursor.fetchone()['count']
    
    # Pass olan testler
    cursor.execute("SELECT COUNT(*) as count FROM test_executions WHERE status = 'pass'")
    passed_tests = cursor.fetchone()['count']
    
    # Başarı oranı
    success_rate = round((passed_tests / total_executions * 100), 1) if total_executions > 0 else 0
    
    # Toplam bug sayısı
    cursor.execute("SELECT COUNT(*) as count FROM bug_reports")
    total_bugs = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'total_projects': total_projects,
        'total_scenarios': total_scenarios,
        'success_rate': success_rate,
        'total_bugs': total_bugs
    }