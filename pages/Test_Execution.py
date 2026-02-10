import streamlit as st
from database.models import (
    get_all_projects,
    get_project_by_id,
    get_scenarios_by_project,
    get_scenario_by_id,
    create_test_execution,
    get_executions_by_scenario
)
import json
from datetime import datetime

st.set_page_config(
    page_title="Test Execution - SmartQA",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Test Execution")
st.markdown("""
Test senaryolarınızı çalıştırın ve sonuçları kaydedin.
Pass/Fail durumlarını takip edin, notlar ekleyin.
""")

# Proje seçimi
projects = get_all_projects()

if len(projects) == 0:
    st.warning("⚠️ Henüz proje oluşturmadınız. Lütfen önce **Projects** sayfasından bir proje oluşturun.")
    st.stop()

# Proje seçim dropdown'ı
project_names = {f"{p['name']} (ID: {p['id']})": p['id'] for p in projects}
selected_project_name = st.selectbox(
    "🎯 Proje Seçin",
    options=list(project_names.keys()),
    help="Test çalıştırmak istediğiniz projeyi seçin"
)

selected_project_id = project_names[selected_project_name]
selected_project = get_project_by_id(selected_project_id)

# Test senaryolarını getir
scenarios = get_scenarios_by_project(selected_project_id)

if len(scenarios) == 0:
    st.info("📝 Bu projede henüz test senaryosu yok. **AI Generator** sayfasından test senaryoları oluşturabilirsiniz.")
    st.stop()

st.markdown("---")

# Test senaryoları listesi
st.subheader(f"📋 Test Senaryoları ({len(scenarios)} adet)")

# Her senaryo için kart
for scenario in scenarios:
    with st.expander(f"**{scenario['title']}**", expanded=False):
        
        # Priority badge
        priority_colors = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        priority_emoji = priority_colors.get(scenario['priority'], '⚪')
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"{priority_emoji} **Priority:** {scenario['priority'].upper()}")
            st.markdown(f"**Açıklama:** {scenario['description']}")
            
            if scenario['created_by_ai']:
                st.caption("🤖 AI tarafından oluşturuldu")
        
        with col2:
            st.caption(f"📅 {scenario['created_at'][:10]}")
        
        st.markdown("---")
        
        # Test adımlarını göster
        st.markdown("**📝 Test Adımları:**")
        
        try:
            steps = json.loads(scenario['steps'])
            for idx, step in enumerate(steps, 1):
                st.markdown(f"{idx}. {step}")
        except:
            st.markdown(scenario['steps'])
        
        st.markdown("---")
        
        # Test execution formu
        st.markdown("**🎯 Test Sonucu Kaydet**")
        
        with st.form(f"execution_form_{scenario['id']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status = st.selectbox(
                    "Test Durumu",
                    options=["pass", "fail", "blocked", "skipped"],
                    format_func=lambda x: {
                        "pass": "✅ Pass (Başarılı)",
                        "fail": "❌ Fail (Başarısız)",
                        "blocked": "🚫 Blocked (Engellendi)",
                        "skipped": "⏭️ Skipped (Atlandı)"
                    }[x],
                    key=f"status_{scenario['id']}"
                )
            
            with col2:
                st.markdown("")  # Spacing
            
            with col3:
                st.markdown("")  # Spacing
            
            notes = st.text_area(
                "Test Notları",
                placeholder="Test sırasında dikkat çeken noktalar, hatalar veya gözlemler...",
                height=100,
                key=f"notes_{scenario['id']}"
            )
            
            submit_button = st.form_submit_button("💾 Sonucu Kaydet", type="primary")
            
            if submit_button:
                # Test execution kaydet
                execution_id = create_test_execution(
                    scenario_id=scenario['id'],
                    status=status,
                    notes=notes
                )
                
                st.success(f"✅ Test sonucu kaydedildi! (Execution ID: {execution_id})")
                
                # Eğer fail ise bug report önerisi
                if status == "fail":
                    st.warning("⚠️ Test başarısız oldu! **Bug Reports** sayfasından bug raporu oluşturabilirsiniz.")
                
                st.rerun()
        
        # Geçmiş execution'ları göster
        executions = get_executions_by_scenario(scenario['id'])
        
        if len(executions) > 0:
            st.markdown("---")
            st.markdown(f"**📊 Geçmiş Çalıştırmalar ({len(executions)} adet)**")
            
            for exe in executions[:5]:  # Son 5 execution
                status_emoji = {
                    "pass": "✅",
                    "fail": "❌",
                    "blocked": "🚫",
                    "skipped": "⏭️"
                }
                
                exe_emoji = status_emoji.get(exe['status'], '❓')
                
                col1, col2, col3 = st.columns([2, 2, 3])
                
                with col1:
                    st.caption(f"{exe_emoji} {exe['status'].upper()}")
                
                with col2:
                    st.caption(f"📅 {exe['executed_at'][:16]}")
                
                with col3:
                    if exe['notes']:
                        st.caption(f"💬 {exe['notes'][:50]}...")

# Footer
st.markdown("---")
st.caption("💡 İpucu: Başarısız testler için Bug Reports sayfasından detaylı bug raporu oluşturabilirsiniz.")