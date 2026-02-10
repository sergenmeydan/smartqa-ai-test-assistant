import streamlit as st
from database.models import (
    get_all_projects,
    get_project_by_id,
    get_scenarios_by_project,
    get_scenario_by_id,
    create_test_scenario,
    update_test_scenario,
    delete_test_scenario
)
import json

st.set_page_config(
    page_title="Test Scenarios - SmartQA",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Test Scenarios Manager")
st.markdown("""
Test senaryolarınızı görüntüleyin, düzenleyin, silin veya yeni senaryolar ekleyin.
Manuel test senaryoları oluşturabilir veya mevcut senaryoları güncelleyebilirsiniz.
""")

st.markdown("---")

# Proje seçimi
projects = get_all_projects()

if len(projects) == 0:
    st.warning("⚠️ Henüz proje oluşturmadınız. Lütfen önce **Projects** sayfasından bir proje oluşturun.")
    st.stop()

project_names = {f"{p['name']} (ID: {p['id']})": p['id'] for p in projects}
selected_project_name = st.selectbox(
    "🎯 Proje Seçin",
    options=list(project_names.keys()),
    help="Test senaryolarını yönetmek istediğiniz projeyi seçin"
)

selected_project_id = project_names[selected_project_name]
selected_project = get_project_by_id(selected_project_id)

st.markdown("---")

# Tab yapısı
tab1, tab2 = st.tabs(["📋 Mevcut Senaryolar", "➕ Yeni Senaryo Ekle"])

# ============= TAB 1: Mevcut Senaryolar =============
with tab1:
    scenarios = get_scenarios_by_project(selected_project_id)
    
    if len(scenarios) == 0:
        st.info("📝 Bu projede henüz test senaryosu yok. **'Yeni Senaryo Ekle'** sekmesinden manuel olarak ekleyebilir veya **AI Generator** sayfasından otomatik oluşturabilirsiniz.")
    else:
        st.subheader(f"📋 Test Senaryoları ({len(scenarios)} adet)")
        
        for scenario in scenarios:
            with st.expander(f"**{scenario['title']}**", expanded=False):
                
                # Priority badge
                priority_colors = {
                    "critical": "🔥",
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                priority_emoji = priority_colors.get(scenario['priority'], '⚪')
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"{priority_emoji} **Priority:** {scenario['priority'].upper()}")
                    if scenario['created_by_ai']:
                        st.caption("🤖 AI tarafından oluşturuldu")
                
                with col2:
                    st.caption(f"📅 {scenario['created_at'][:10]}")
                
                with col3:
                    # Sil butonu
                    if st.button("🗑️ Tüm Senaryoyu Sil", key=f"delete_scenario_{scenario['id']}", type="secondary"):
                        delete_test_scenario(scenario['id'])
                        st.success("✅ Test senaryosu silindi!")
                        st.rerun()
                
                st.markdown("---")
                
                # Session state için key
                session_key = f"edit_steps_{scenario['id']}"
                
                # Steps'i parse et ve session state'e yükle
                try:
                    current_steps = json.loads(scenario['steps'])
                except:
                    current_steps = [scenario['steps']]
                
                # İlk yüklemede session state'e kaydet
                if session_key not in st.session_state:
                    st.session_state[session_key] = current_steps.copy()
                
                # Düzenleme formu
                st.markdown("### ✏️ Senaryoyu Düzenle")
                
                edit_title = st.text_input(
                    "Başlık",
                    value=scenario['title'],
                    key=f"edit_title_{scenario['id']}"
                )
                
                edit_description = st.text_area(
                    "Açıklama",
                    value=scenario['description'],
                    height=80,
                    key=f"edit_desc_{scenario['id']}"
                )
                
                # Test adımları
                st.markdown("**Test Adımları:**")
                
                # Her adım için input ve sil butonu
                for idx, step in enumerate(st.session_state[session_key]):
                    col_step, col_delete = st.columns([5, 1])
                    
                    with col_step:
                        new_value = st.text_input(
                            f"Adım {idx + 1}",
                            value=step,
                            key=f"step_input_{scenario['id']}_{idx}"
                        )
                        # Session state'i güncelle
                        st.session_state[session_key][idx] = new_value
                    
                    with col_delete:
                        st.markdown("")
                        st.markdown("")
                        if len(st.session_state[session_key]) > 1:  # En az 1 adım kalmalı
                            if st.button("🗑️", key=f"delete_step_{scenario['id']}_{idx}", help="Bu adımı sil"):
                                st.session_state[session_key].pop(idx)
                                st.rerun()
                
                # Yeni adım ekle butonu
                if st.button("➕ Yeni Adım Ekle", key=f"add_step_{scenario['id']}", type="secondary"):
                    st.session_state[session_key].append("")
                    st.rerun()
                
                # Priority
                priority_options = ["critical", "high", "medium", "low"]
                current_priority = scenario['priority']
                
                if current_priority not in priority_options:
                    current_priority = "medium"
                
                edit_priority = st.selectbox(
                    "Öncelik",
                    options=priority_options,
                    index=priority_options.index(current_priority),
                    format_func=lambda x: {
                        "critical": "🔥 Critical (Kritik)",
                        "high": "🔴 High (Yüksek)",
                        "medium": "🟡 Medium (Orta)",
                        "low": "🟢 Low (Düşük)"
                    }[x],
                    key=f"edit_priority_{scenario['id']}"
                )
                
                # Kaydet butonu
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("💾 Değişiklikleri Kaydet", key=f"save_{scenario['id']}", type="primary"):
                        # Boş adımları temizle
                        clean_steps = [step.strip() for step in st.session_state[session_key] if step.strip()]
                        
                        if not edit_title or len(clean_steps) == 0:
                            st.error("❌ Başlık ve en az bir adım gereklidir!")
                        else:
                            update_test_scenario(
                                scenario_id=scenario['id'],
                                title=edit_title,
                                description=edit_description,
                                steps=clean_steps,
                                priority=edit_priority
                            )
                            # Session state temizle
                            if session_key in st.session_state:
                                del st.session_state[session_key]
                            st.success("✅ Test senaryosu güncellendi!")
                            st.rerun()

# ============= TAB 2: Yeni Senaryo Ekle =============
with tab2:
    st.subheader("➕ Manuel Test Senaryosu Oluştur")
    
    # Başarı mesajı için session state
    if 'scenario_created' in st.session_state and st.session_state['scenario_created']:
        st.success(f"✅ Test senaryosu başarıyla oluşturuldu! (ID: {st.session_state.get('last_scenario_id', 'N/A')})")
        st.balloons()
        st.session_state['scenario_created'] = False
        st.info("🎯 **Mevcut Senaryolar** sekmesinden senaryonuzu görebilir ve düzenleyebilirsiniz!")
    
    with st.form("new_scenario_form", clear_on_submit=True):
        new_title = st.text_input(
            "Test Senaryosu Başlığı *",
            placeholder="örn: Kullanıcı Login Testi"
        )
        
        new_description = st.text_area(
            "Açıklama *",
            placeholder="Bu test senaryosunun amacı...",
            height=100
        )
        
        st.markdown("**Test Adımları *:**")
        st.caption("Her adımı ayrı bir satıra yazın")
        
        new_steps_text = st.text_area(
            "Test Adımları (her satır bir adım)",
            placeholder="Login sayfasına git\nKullanıcı adı ve şifre gir\nGiriş butonuna tıkla\nDashboard'a yönlendirildiğini doğrula",
            height=150,
            label_visibility="collapsed"
        )
        
        new_priority = st.selectbox(
            "Öncelik *",
            options=["critical", "high", "medium", "low"],
            index=2,  # Default: medium
            format_func=lambda x: {
                "critical": "🔥 Critical (Kritik)",
                "high": "🔴 High (Yüksek)",
                "medium": "🟡 Medium (Orta)",
                "low": "🟢 Low (Düşük)"
            }[x]
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("✨ Senaryoyu Oluştur", type="primary")
        
        if submit_button:
            if not new_title or not new_description or not new_steps_text:
                st.error("❌ Lütfen tüm zorunlu alanları doldurun!")
            else:
                # Adımları listeye çevir
                steps_list = [step.strip() for step in new_steps_text.split('\n') if step.strip()]
                
                if len(steps_list) == 0:
                    st.error("❌ En az bir test adımı eklemelisiniz!")
                else:
                    # Senaryoyu oluştur
                    scenario_id = create_test_scenario(
                        project_id=selected_project_id,
                        title=new_title,
                        description=new_description,
                        steps=steps_list,
                        priority=new_priority,
                        created_by_ai=False
                    )
                    
                    # Session state'e kaydet
                    st.session_state['scenario_created'] = True
                    st.session_state['last_scenario_id'] = scenario_id
                    st.rerun()
    
    # Örnek format göster
    with st.expander("💡 İpucu: Test Adımları Nasıl Yazılır?", expanded=False):
        st.markdown("""
        **Örnek Test Senaryosu:**
        
        **Başlık:** Kullanıcı Login Testi
        
        **Açıklama:** Kayıtlı kullanıcının sisteme başarılı şekilde giriş yapabilmesini test eder
        
        **Test Adımları:**
```
        Login sayfasına git
        Geçerli email adresi gir (test@example.com)
        Geçerli şifre gir
        'Giriş Yap' butonuna tıkla
        Dashboard sayfasına yönlendirildiğini doğrula
        Kullanıcı adının header'da göründüğünü kontrol et
```
        
        **Öncelik:** High
        """)

# Footer
st.markdown("---")
st.caption("💡 **İpucu:** AI Generator ile otomatik senaryolar oluşturabilir, buradan manuel olarak düzenleyebilirsiniz.")