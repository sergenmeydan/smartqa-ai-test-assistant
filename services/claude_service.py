import os
import json
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# DEMO MODE: API key yoksa veya krediniz bittiyse mock data kullan
USE_MOCK_AI = True  # False yapınca gerçek API kullanır

def generate_test_scenarios(project_name, project_url, project_description, num_scenarios=5):
    """
    Proje bilgilerine göre test senaryoları üret
    """
    
    if USE_MOCK_AI:
        # MOCK DATA - Demo için
        mock_scenarios = [
            {
                "title": "Kullanıcı Kayıt İşlemi Testi",
                "description": "Yeni kullanıcının başarılı bir şekilde kayıt olabilmesini doğrular",
                "steps": [
                    "Ana sayfada 'Kayıt Ol' butonuna tıkla",
                    "Gerekli bilgileri doldur (ad, email, şifre)",
                    "Şartlar ve koşulları kabul et checkbox'ını işaretle",
                    "'Hesap Oluştur' butonuna tıkla",
                    "Email doğrulama mesajının geldiğini kontrol et",
                    "Başarılı kayıt mesajının göründüğünü doğrula"
                ],
                "priority": "high"
            },
            {
                "title": "Login Fonksiyonelliği Testi",
                "description": "Kayıtlı kullanıcının sisteme giriş yapabilmesini test eder",
                "steps": [
                    "Login sayfasına git",
                    "Geçerli email ve şifre gir",
                    "'Giriş Yap' butonuna tıkla",
                    "Dashboard sayfasına yönlendirildiğini doğrula",
                    "Kullanıcı adının header'da göründüğünü kontrol et"
                ],
                "priority": "high"
            },
            {
                "title": "Ürün Arama Fonksiyonu Testi",
                "description": "Kullanıcının ürün arayabilmesini ve sonuçları görebilmesini test eder",
                "steps": [
                    "Ana sayfadaki arama kutusuna bir ürün adı yaz",
                    "Enter tuşuna bas veya ara butonuna tıkla",
                    "Arama sonuçlarının yüklendiğini bekle",
                    "İlgili ürünlerin listelendiğini doğrula",
                    "Sonuç sayısının gösterildiğini kontrol et"
                ],
                "priority": "medium"
            },
            {
                "title": "Sepete Ürün Ekleme Testi",
                "description": "Ürünlerin sepete eklenebilmesini ve sepet içeriğinin doğru gösterilmesini test eder",
                "steps": [
                    "Bir ürün detay sayfasına git",
                    "Ürün miktarını seç",
                    "'Sepete Ekle' butonuna tıkla",
                    "Sepet ikonundaki sayının arttığını doğrula",
                    "Sepet sayfasına git",
                    "Eklenen ürünün sepette göründüğünü kontrol et"
                ],
                "priority": "high"
            },
            {
                "title": "Şifre Sıfırlama Testi",
                "description": "Kullanıcının unutulan şifresini sıfırlayabilmesini test eder",
                "steps": [
                    "Login sayfasında 'Şifremi Unuttum' linkine tıkla",
                    "Kayıtlı email adresini gir",
                    "'Sıfırlama Linki Gönder' butonuna tıkla",
                    "Email'in geldiğini kontrol et",
                    "Email'deki linke tıkla",
                    "Yeni şifre oluştur ve kaydet",
                    "Yeni şifre ile login olabildiğini doğrula"
                ],
                "priority": "medium"
            },
            {
                "title": "Ödeme İşlemi Testi",
                "description": "Kullanıcının sepetteki ürünleri satın alabilmesini test eder",
                "steps": [
                    "Sepete en az bir ürün ekle",
                    "'Ödemeye Geç' butonuna tıkla",
                    "Teslimat adresini doldur",
                    "Ödeme yöntemi seç (Kredi Kartı)",
                    "Kart bilgilerini gir",
                    "'Siparişi Tamamla' butonuna tıkla",
                    "Sipariş onay sayfasının göründüğünü doğrula"
                ],
                "priority": "critical"
            },
            {
                "title": "Ürün Filtreleme Testi",
                "description": "Kategori ve fiyat filtrelerinin doğru çalıştığını test eder",
                "steps": [
                    "Ürün listesi sayfasına git",
                    "Bir kategori seç (örn: Elektronik)",
                    "Sadece seçilen kategorideki ürünlerin göründüğünü doğrula",
                    "Fiyat aralığı belirle (örn: 100-500 TL)",
                    "Filtrelerin uygulandığını ve sonuçların değiştiğini kontrol et"
                ],
                "priority": "medium"
            },
            {
                "title": "Profil Bilgileri Güncelleme Testi",
                "description": "Kullanıcının profil bilgilerini güncelleyebilmesini test eder",
                "steps": [
                    "Profil sayfasına git",
                    "'Bilgilerimi Düzenle' butonuna tıkla",
                    "Ad, telefon gibi bilgileri güncelle",
                    "'Kaydet' butonuna tıkla",
                    "Başarı mesajının göründüğünü doğrula",
                    "Güncellemelerin kaydedildiğini kontrol et"
                ],
                "priority": "low"
            },
            {
                "title": "Responsive Tasarım Testi",
                "description": "Web sitesinin mobil cihazlarda düzgün görüntülendiğini test eder",
                "steps": [
                    "Tarayıcıyı mobil görünüme al (veya gerçek mobil cihaz kullan)",
                    "Ana sayfanın düzgün yüklendiğini kontrol et",
                    "Menünün hamburger ikon olarak göründüğünü doğrula",
                    "Sayfa içi elementlerin mobilde okunabilir olduğunu kontrol et",
                    "Butonların tıklanabilir boyutta olduğunu test et"
                ],
                "priority": "medium"
            },
            {
                "title": "Logout İşlemi Testi",
                "description": "Kullanıcının güvenli bir şekilde çıkış yapabilmesini test eder",
                "steps": [
                    "Login olmuş bir kullanıcı ile devam et",
                    "Kullanıcı menüsünden 'Çıkış Yap' seçeneğine tıkla",
                    "Login sayfasına yönlendirildiğini doğrula",
                    "Tarayıcı back tuşu ile geri gidildiğinde korumalı sayfalara erişilemediğini kontrol et"
                ],
                "priority": "high"
            }
        ]
        
        # Kullanıcının istediği kadar senaryo döndür
        selected_scenarios = mock_scenarios[:num_scenarios]
        
        result = {
            "test_scenarios": selected_scenarios
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    else:
        # GERÇEK API KULLANIMI
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "Hata: ANTHROPIC_API_KEY bulunamadı!"
        
        try:
            client = Anthropic(api_key=api_key)
        except TypeError:
            import anthropic
            client = anthropic.Client(api_key=api_key)
        
        prompt = f"""
Sen bir profesyonel Software Test Engineer'sın. Aşağıdaki proje için test senaryoları oluştur.

PROJE BİLGİLERİ:
- Proje Adı: {project_name}
- URL: {project_url if project_url else 'Belirtilmemiş'}
- Açıklama: {project_description if project_description else 'Belirtilmemiş'}

GÖREV:
{num_scenarios} adet detaylı test senaryosu oluştur. Her test senaryosu için:
- Açıklayıcı bir başlık
- Test senaryosunun amacını anlatan bir açıklama
- Adım adım test adımları (minimum 3, maksimum 7 adım)
- Öncelik seviyesi (high, medium, low)

ÇIKTI FORMATI (JSON):
{{
  "test_scenarios": [
    {{
      "title": "Test senaryosu başlığı",
      "description": "Test senaryosunun amacı",
      "steps": [
        "Adım 1: ...",
        "Adım 2: ...",
        "Adım 3: ..."
      ],
      "priority": "high"
    }}
  ]
}}

Sadece JSON formatında yanıt ver, başka açıklama ekleme.
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            return result
        
        except Exception as e:
            return f"Hata: {str(e)}"


def generate_bug_report(test_title, test_steps, failure_notes):
    """
    Başarısız test için bug raporu üret
    """
    
    if USE_MOCK_AI:
        # MOCK BUG REPORT
        mock_bug = {
            "title": f"Bug: {test_title} - Fonksiyon Çalışmıyor",
            "severity": "high",
            "description": f"'{test_title}' test senaryosu çalıştırılırken beklenmedik bir hata ile karşılaşıldı. {failure_notes}",
            "steps_to_reproduce": f"1. Test senaryosundaki adımları takip et\n2. {test_steps[:100]}...\n3. Hata oluşur",
            "expected_result": "İşlem başarılı bir şekilde tamamlanmalı ve kullanıcıya onay mesajı gösterilmeli.",
            "actual_result": f"İşlem başarısız oldu. {failure_notes}"
        }
        
        return json.dumps(mock_bug, ensure_ascii=False, indent=2)
    
    else:
        # GERÇEK API KULLANIMI
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "Hata: ANTHROPIC_API_KEY bulunamadı!"
        
        try:
            client = Anthropic(api_key=api_key)
        except TypeError:
            import anthropic
            client = anthropic.Client(api_key=api_key)
        
        prompt = f"""
Sen bir profesyonel Software Test Engineer'sın. Başarısız olan bir test için detaylı bug raporu oluştur.

TEST BİLGİLERİ:
- Test Adı: {test_title}
- Test Adımları: {test_steps}
- Hata Notları: {failure_notes}

GÖREV:
Profesyonel bir bug raporu oluştur. Aşağıdaki bilgileri içermeli:

ÇIKTI FORMATI (JSON):
{{
  "title": "Bug başlığı (kısa ve açıklayıcı)",
  "severity": "critical/high/medium/low",
  "description": "Bug'ın detaylı açıklaması",
  "steps_to_reproduce": "1. Adım\\n2. Adım\\n3. Adım",
  "expected_result": "Beklenen sonuç",
  "actual_result": "Gerçekleşen sonuç"
}}

Sadece JSON formatında yanıt ver, başka açıklama ekleme.
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            return result
        
        except Exception as e:
            return f"Hata: {str(e)}"