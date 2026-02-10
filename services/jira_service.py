import os
import requests
from dotenv import load_dotenv
import base64

load_dotenv()

# Jira konfigürasyonu
JIRA_URL = os.getenv("JIRA_URL", "")  # örn: https://your-domain.atlassian.net
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")  # örn: TEST

# Mock mode - Jira bilgileri yoksa demo modu
USE_MOCK_JIRA = not (JIRA_URL and JIRA_EMAIL and JIRA_API_TOKEN and JIRA_PROJECT_KEY)

def create_jira_issue(bug_title, bug_description, steps_to_reproduce, expected_result, actual_result, severity):
    """
    Jira'da bug issue oluştur
    """
    
    if USE_MOCK_JIRA:
        # MOCK MODE - Demo için
        import random
        mock_issue_key = f"BUG-{random.randint(1000, 9999)}"
        mock_url = f"https://demo.atlassian.net/browse/{mock_issue_key}"
        
        return {
            "success": True,
            "issue_key": mock_issue_key,
            "issue_url": mock_url,
            "message": "✅ Demo mode: Jira issue başarıyla oluşturuldu (simülasyon)"
        }
    
    else:
        # GERÇEK JIRA ENTEGRASYONU
        try:
            # Basic Auth için credentials
            auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
            auth_bytes = auth_string.encode('ascii')
            auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/json"
            }
            
            # Priority mapping
            priority_map = {
                "critical": "Highest",
                "high": "High",
                "medium": "Medium",
                "low": "Low"
            }
            
            # Issue body
            description_text = f"""
h2. Bug Açıklaması
{bug_description}

h2. Yeniden Üretme Adımları
{steps_to_reproduce}

h2. Beklenen Sonuç
{expected_result}

h2. Gerçekleşen Sonuç
{actual_result}

---
_Bu issue SmartQA - AI Test Assistant tarafından otomatik oluşturulmuştur._
"""
            
            payload = {
                "fields": {
                    "project": {
                        "key": JIRA_PROJECT_KEY
                    },
                    "summary": bug_title,
                    "description": description_text,
                    "issuetype": {
                        "name": "Bug"
                    },
                    "priority": {
                        "name": priority_map.get(severity, "Medium")
                    },
                    "labels": ["smartqa", "automated"]
                }
            }
            
            # API request
            response = requests.post(
                f"{JIRA_URL}/rest/api/3/issue",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_key = issue_data['key']
                issue_url = f"{JIRA_URL}/browse/{issue_key}"
                
                return {
                    "success": True,
                    "issue_key": issue_key,
                    "issue_url": issue_url,
                    "message": f"✅ Jira issue başarıyla oluşturuldu: {issue_key}"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Jira API hatası: {response.status_code} - {response.text}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Bağlantı hatası: {str(e)}"
            }


def test_jira_connection():
    """
    Jira bağlantısını test et
    """
    
    if USE_MOCK_JIRA:
        return {
            "success": True,
            "message": "⚠️ Demo mode aktif. Gerçek Jira bağlantısı için .env dosyasını yapılandırın.",
            "mock_mode": True
        }
    
    try:
        auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
        auth_bytes = auth_string.encode('ascii')
        auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{JIRA_URL}/rest/api/3/myself",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "success": True,
                "message": f"✅ Jira bağlantısı başarılı! Kullanıcı: {user_data.get('displayName', 'Unknown')}",
                "mock_mode": False
            }
        else:
            return {
                "success": False,
                "message": f"❌ Jira bağlantısı başarısız: {response.status_code}",
                "mock_mode": False
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Bağlantı hatası: {str(e)}",
            "mock_mode": False
        }