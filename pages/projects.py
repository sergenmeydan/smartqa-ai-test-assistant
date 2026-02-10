import streamlit as st
from database.models import (
    create_project, 
    get_all_projects, 
    delete_project,
    get_scenarios_by_project
)
from datetime import datetime

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Projects - SmartQA",
    page_icon="📁",
    layout="wide"
)

# Sayfa başlığı ve açıklama
st.title("📁 Projects")
st.markdown("""
Projelerinizi yönetin, yeni projeler oluşturun ve mevcut projeleri düzenleyin.
Test senaryolarınız projelere bağlı olarak organize edilir.
""")

st.markdown("---")

# Tab yapısı
tab1, tab2 = st.tabs(["📋 Proje Listesi", "➕ Yeni Proje Oluştur"])

# ============= TAB 1: Proje Listesi =============
with tab1:
    st.subheader("📋 Mevcut Projeler")
    
    projects = get_all_projects()
    
    if len(projects) == 0:
        st.info("👋 Henüz proje oluşturmadınız. Yeni proje oluşturmak için **'Yeni Proje Oluştur'** sekmesine gidin.")
    else:
        # Her proje için bir card
        for project in projects:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### 🎯 {project['name']}")
                    if project['url']:
                        st.markdown(f"🔗 [{project['url']}]({project['url']})")
                    if project['description']:
                        st.markdown(f"_{project['description']}_")
                    
                    # Test senaryosu sayısı
                    scenarios = get_scenarios_by_project(project['id'])
                    st.caption(f"📊 {len(scenarios)} test senaryosu")
                
                with col2:
                    st.caption(f"📅 {project['created_at'][:10]}")
                
                with col3:
                    # Sil butonu
                    if st.button("🗑️ Sil", key=f"delete_{project['id']}", type="secondary"):
                        delete_project(project['id'])
                        st.success(f"✅ {project['name']} silindi!")
                        st.rerun()
                
                st.markdown("---")

# ============= TAB 2: Yeni Proje Oluştur =============
with tab2:
    st.subheader("➕ Yeni Proje Oluştur")
    
    with st.form("new_project_form"):
        project_name = st.text_input(
            "Proje Adı *",
            placeholder="örn: E-commerce Test Projesi",
            help="Projenize açıklayıcı bir isim verin"
        )
        
        project_url = st.text_input(
            "Proje URL",
            placeholder="https://demo.example.com",
            help="Test edeceğiniz web sitesinin URL'si (opsiyonel)"
        )
        
        project_description = st.text_area(
            "Açıklama",
            placeholder="Bu proje e-commerce platformunun test süreçlerini kapsar...",
            help="Projeniz hakkında detaylı açıklama yazın",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("✨ Proje Oluştur", type="primary", use_container_width=True)
        
        if submit_button:
            if not project_name:
                st.error("❌ Proje adı zorunludur!")
            else:
                # Proje oluştur
                project_id = create_project(project_name, project_url, project_description)
                st.success(f"✅ Proje başarıyla oluşturuldu! (ID: {project_id})")
                st.balloons()
                
                # Bilgilendirme
                st.info("🎯 Şimdi **AI Generator** sayfasına giderek bu proje için test senaryoları oluşturabilirsiniz!")
                
                # Formu temizlemek için rerun
                st.rerun()

# Footer
st.markdown("---")
st.caption("💡 İpucu: Projelerinizi organize tutmak için açıklayıcı isimler kullanın.")