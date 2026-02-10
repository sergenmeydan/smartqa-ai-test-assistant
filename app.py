import streamlit as st
from datetime import datetime
from database.db import init_database
from database.models import get_dashboard_stats, get_all_projects

# Database'i başlat
init_database()

# Sayfa yapılandırması
st.set_page_config(
    page_title="SmartQA - AI Test Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile özelleştirme
st.markdown("""
    <style>
    /* Metrik kartlarını özelleştir */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Info box'ları özelleştir */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Başlıklar */
    h1 {
        color: #1E88E5;
    }
    
    h3 {
        color: #64B5F6;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar içeriği
with st.sidebar:
    st.markdown("# 🤖 SmartQA")
    st.markdown("### AI Test Assistant")
    st.markdown("---")
    
    # Bilgi kutusu
    st.info("""
    **🎯 Hoş Geldiniz!**
    
    Yapay zeka destekli test yönetim platformuna hoş geldiniz.
    """)
    
    st.markdown("---")
    
    # Hızlı İstatistikler
    stats = get_dashboard_stats()
    
    st.markdown("#### 📊 Hızlı Bakış")
    st.metric("📁 Projeler", stats['total_projects'])
    st.metric("🎯 Test Senaryoları", stats['total_scenarios'])
    st.metric("🐛 Bug Raporları", stats['total_bugs'])
    
    st.markdown("---")
    
    # Versiyon bilgisi
    st.caption("**Version:** 1.0.0")
    st.caption(f"📅 {datetime.now().strftime('%d.%m.%Y')}")

# Ana başlık
st.title("🤖 SmartQA - AI Test Assistant")
st.markdown("#### 🚀 Yapay Zeka Destekli Test Yönetim Platformu")

st.markdown("---")

# Dashboard metrikleri
st.subheader("📊 Dashboard Overview")

# Verileri çek
stats = get_dashboard_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📁 Toplam Proje",
        value=stats['total_projects'],
        delta=f"+{stats['total_projects']}" if stats['total_projects'] > 0 else "0",
        help="Sistemdeki toplam proje sayısı"
    )

with col2:
    st.metric(
        label="🎯 Test Senaryosu",
        value=stats['total_scenarios'],
        delta=f"+{stats['total_scenarios']}" if stats['total_scenarios'] > 0 else "0",
        help="Oluşturulan toplam test senaryosu sayısı"
    )

with col3:
    st.metric(
        label="✅ Başarı Oranı",
        value=f"{stats['success_rate']}%",
        delta=f"{stats['success_rate']}%" if stats['success_rate'] > 0 else "0%",
        help="Geçen testlerin yüzdesi",
        delta_color="normal" if stats['success_rate'] >= 70 else "inverse"
    )

with col4:
    st.metric(
        label="🐛 Bulunan Bug",
        value=stats['total_bugs'],
        delta=f"+{stats['total_bugs']}" if stats['total_bugs'] > 0 else "0",
        help="Rapor edilen toplam bug sayısı",
        delta_color="inverse"
    )

st.markdown("---")

# Platform Özellikleri
st.subheader("✨ Platform Özellikleri")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background-color: #1E3A5F; padding: 20px; border-radius: 10px; height: 180px;">
        <h3 style="color: #64B5F6;">📁 Proje Yönetimi</h3>
        <p style="color: #BBDEFB;">Test projelerinizi organize edin ve yönetin.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #1E3A5F; padding: 20px; border-radius: 10px; height: 180px;">
        <h3 style="color: #64B5F6;">🤖 AI Test Üretimi</h3>
        <p style="color: #BBDEFB;">Claude AI ile otomatik test senaryoları oluşturun.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background-color: #1E3A5F; padding: 20px; border-radius: 10px; height: 180px;">
        <h3 style="color: #64B5F6;">📝 Senaryo Yönetimi</h3>
        <p style="color: #BBDEFB;">Test senaryolarınızı düzenleyin, ekleyin, silin.</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background-color: #1E3A5F; padding: 20px; border-radius: 10px; height: 180px;">
        <h3 style="color: #64B5F6;">🐛 Bug Tracking</h3>
        <p style="color: #BBDEFB;">AI destekli profesyonel bug raporları oluşturun.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Hızlı Başlangıç Rehberi
st.subheader("🚀 Hızlı Başlangıç Rehberi")

step1, step2, step3, step4 = st.columns(4)

with step1:
    st.markdown("""
    ### 1️⃣ Proje Oluştur
    
    📁 **Projects** sayfasına gidin
    
    ➕ Yeni proje ekleyin
    
    📝 Proje detaylarını doldurun
    """)

with step2:
    st.markdown("""
    ### 2️⃣ Test Senaryoları
    
    🤖 **AI Generator** ile otomatik
    
    📝 veya **Test Scenarios** ile manuel
    
    ✏️ Senaryoları düzenleyin
    """)

with step3:
    st.markdown("""
    ### 3️⃣ Testleri Çalıştır
    
    ✅ **Test Execution** sayfası
    
    ▶️ Testleri çalıştırın
    
    📊 Sonuçları kaydedin
    """)

with step4:
    st.markdown("""
    ### 4️⃣ Bug Raporu
    
    🐛 **Bug Reports** sayfası
    
    🤖 AI ile otomatik oluştur
    
    🎫 Jira'ya gönder (yakında)
    """)

st.markdown("---")

# Son Aktiviteler ve Bilgilendirme
if stats['total_projects'] == 0:
    st.warning("""
    ### 👋 Platforma Hoş Geldiniz!
    
    Başlamak için:
    1. Sol menüden **📁 Projects** sayfasına gidin
    2. İlk projenizi oluşturun
    3. **🤖 AI Generator** ile test senaryoları oluşturun
    
    **İpucu:** Demo için "E-commerce Test" adında bir proje oluşturabilirsiniz.
    """)
else:
    # Proje listesi
    projects = get_all_projects()
    
    st.success("""
    ### ✅ Sistemde Aktif Projeleriniz Var!
    
    Aşağıdaki projelerle çalışabilirsiniz:
    """)
    
    for project in projects[:5]:  # İlk 5 projeyi göster
        with st.expander(f"📁 {project['name']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if project['url']:
                    st.markdown(f"**URL:** [{project['url']}]({project['url']})")
                st.markdown(f"**Oluşturma:** {project['created_at'][:10]}")
            with col2:
                if project['description']:
                    st.markdown(f"**Açıklama:** {project['description'][:100]}...")

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **💡 İpucu**
    
    Sol menüden istediğiniz sayfaya hızlıca ulaşabilirsiniz.
    """)

with col2:
    st.info("""
    **🎯 Özellikler**
    
    - AI Test Oluşturma
    - Manuel Düzenleme
    - Bug Tracking
    - Jira Entegrasyonu (Yakında)
    """)

with col3:
    st.info("""
    **📊 Raporlama**
    
    - Test Sonuçları
    - Başarı Oranları
    - Bug İstatistikleri
    - Proje Performansı
    """)

st.markdown("---")
st.caption("🤖 SmartQA - AI Test Assistant | Version 1.0.0")