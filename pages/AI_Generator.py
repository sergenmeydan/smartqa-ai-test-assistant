import streamlit as st
from database.models import (
    get_all_projects, 
    get_project_by_id,
    create_test_scenario
)
from services.claude_service import generate_test_scenarios
import json

st.set_page_config(
    page_title="AI Generator - SmartQA",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Test Generator")
st.markdown("""
Claude AI kullanarak otomatik test senaryoları oluşturun.
Projenizin detaylarına göre özelleştirilmiş test senaryoları alın.
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
    help="Test senaryoları oluşturmak istediğiniz projeyi seçin"
)

selected_project_id = project_names[selected_project_name]
selected_project = get_project_by_id(selected_project_id)

# Seçilen proje bilgileri
with st.expander("📋 Seçilen Proje Detayları", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Proje Adı:** {selected_project['name']}")
        st.markdown(f"**URL:** {selected_project['url'] if selected_project['url'] else 'Belirtilmemiş'}")
    with col2:
        st.markdown(f"**Açıklama:** {selected_project['description'] if selected_project['description'] else 'Belirtilmemiş'}")

st.markdown("---")

# Generator Ayarları
st.subheader("⚙️ Generator Ayarları")

col1, col2 = st.columns([3, 1])

with col1:
    num_scenarios = st.slider(
        "Kaç adet test senaryosu oluşturulsun?",
        min_value=3,
        max_value=10,
        value=5,
        help="Claude AI bu kadar test senaryosu üretecek"
    )

with col2:
    st.markdown("")
    st.markdown("")
    generate_button = st.button("✨ Test Senaryoları Üret", type="primary", use_container_width=True)

st.markdown("---")

# Test senaryoları üretme
if generate_button:
    with st.spinner("🤖 Claude AI test senaryoları oluşturuyor... (15-30 saniye sürebilir)"):
        
        # Claude'dan test senaryoları al
        result = generate_test_scenarios(
            project_name=selected_project['name'],
            project_url=selected_project['url'],
            project_description=selected_project['description'],
            num_scenarios=num_scenarios
        )
        
        # Hata kontrolü
        if result.startswith("Hata:"):
            st.error(f"❌ {result}")
            st.stop()
        
        try:
            # JSON parse et
            # Claude bazen markdown code block içinde döndürür, temizle
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            scenarios = data.get("test_scenarios", [])
            
            if len(scenarios) == 0:
                st.warning("⚠️ Test senaryosu oluşturulamadı. Lütfen tekrar deneyin.")
                st.stop()
            
            # Başarı mesajı
            st.success(f"✅ {len(scenarios)} adet test senaryosu başarıyla oluşturuldu!")
            
            # Senaryoları database'e kaydet
            saved_count = 0
            for scenario in scenarios:
                try:
                    create_test_scenario(
                        project_id=selected_project_id,
                        title=scenario['title'],
                        description=scenario['description'],
                        steps=scenario['steps'],
                        priority=scenario['priority'],
                        created_by_ai=True
                    )
                    saved_count += 1
                except Exception as e:
                    st.error(f"❌ Senaryo kaydedilemedi: {str(e)}")
            
            st.info(f"💾 {saved_count} test senaryosu database'e kaydedildi!")
            st.balloons()
            
            # Oluşturulan senaryoları göster
            st.markdown("---")
            st.subheader("📝 Oluşturulan Test Senaryoları")
            
            for idx, scenario in enumerate(scenarios, 1):
                with st.expander(f"**Test #{idx}: {scenario['title']}**", expanded=False):
                    
                    # Priority badge
                    priority_colors = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }
                    st.markdown(f"{priority_colors.get(scenario['priority'], '⚪')} **Priority:** {scenario['priority'].upper()}")
                    
                    # Description
                    st.markdown(f"**Açıklama:** {scenario['description']}")
                    
                    # Steps
                    st.markdown("**Test Adımları:**")
                    for step_idx, step in enumerate(scenario['steps'], 1):
                        st.markdown(f"{step_idx}. {step}")
            
            # Bilgilendirme
            st.markdown("---")
            st.info("🎯 Test senaryolarınızı **Test Execution** sayfasından çalıştırabilirsiniz!")
        
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON parse hatası: {str(e)}")
            st.code(result)
        except Exception as e:
            st.error(f"❌ Beklenmeyen hata: {str(e)}")

# Footer
st.markdown("---")
st.caption("💡 İpucu: Claude AI, projenizin URL ve açıklamasını analiz ederek ilgili test senaryoları oluşturur.")