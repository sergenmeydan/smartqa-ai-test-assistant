import streamlit as st
from database.models import (
    get_all_projects,
    get_project_by_id,
    get_scenarios_by_project,
    get_scenario_by_id,
    get_executions_by_scenario,
    create_bug_report,
    get_all_bug_reports
)
from services.claude_service import generate_bug_report
from services.jira_service import create_jira_issue, test_jira_connection
import json

st.set_page_config(
    page_title="Bug Reports - SmartQA",
    page_icon="🐛",
    layout="wide"
)

st.title("🐛 Bug Reports")
st.markdown("""
Başarısız testler için profesyonel bug raporları oluşturun.
AI ile otomatik bug raporu üretin veya manuel olarak oluşturun.
""")

st.markdown("---")

# Tab yapısı
tab1, tab2 = st.tabs(["➕ Yeni Bug Raporu Oluştur", "📋 Bug Raporları Listesi"])

# ============= TAB 1: Yeni Bug Raporu =============
with tab1:
    st.subheader("➕ Yeni Bug Raporu Oluştur")
    
    # Proje seçimi
    projects = get_all_projects()
    
    if len(projects) == 0:
        st.warning("⚠️ Henüz proje oluşturmadınız.")
        st.stop()
    
    project_names = {f"{p['name']} (ID: {p['id']})": p['id'] for p in projects}
    selected_project_name = st.selectbox(
        "🎯 Proje Seçin",
        options=list(project_names.keys()),
        key="bug_project_select"
    )
    
    selected_project_id = project_names[selected_project_name]
    
    # Test senaryolarını getir
    scenarios = get_scenarios_by_project(selected_project_id)
    
    if len(scenarios) == 0:
        st.info("📝 Bu projede henüz test senaryosu yok.")
        st.stop()
    
    # Sadece fail olan execution'ları bul
    failed_scenarios = []
    for scenario in scenarios:
        executions = get_executions_by_scenario(scenario['id'])
        for execution in executions:
            if execution['status'] == 'fail':
                failed_scenarios.append({
                    'scenario': scenario,
                    'execution': execution
                })
    
    if len(failed_scenarios) == 0:
        st.info("✅ Bu projede başarısız test yok. Bug raporu oluşturmak için önce bir testi 'fail' olarak işaretleyin.")
    else:
        st.markdown("---")
        
        # Başarısız test seçimi
        failed_test_options = {
            f"{item['scenario']['title']} - {item['execution']['executed_at'][:16]}": item
            for item in failed_scenarios
        }
        
        selected_test_name = st.selectbox(
            "❌ Başarısız Test Seçin",
            options=list(failed_test_options.keys()),
            help="Bug raporu oluşturmak istediğiniz başarısız testi seçin"
        )
        
        selected_item = failed_test_options[selected_test_name]
        selected_scenario = selected_item['scenario']
        selected_execution = selected_item['execution']
        
        # Seçilen test detayları
        with st.expander("📋 Test Detayları", expanded=True):
            st.markdown(f"**Test Adı:** {selected_scenario['title']}")
            st.markdown(f"**Açıklama:** {selected_scenario['description']}")
            st.markdown(f"**Test Notları:** {selected_execution['notes'] if selected_execution['notes'] else 'Yok'}")
            
            try:
                steps = json.loads(selected_scenario['steps'])
                st.markdown("**Test Adımları:**")
                for idx, step in enumerate(steps, 1):
                    st.markdown(f"{idx}. {step}")
            except:
                st.markdown(f"**Test Adımları:** {selected_scenario['steps']}")
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🤖 AI ile Otomatik Bug Raporu")
            st.markdown("Claude AI, test bilgilerini analiz ederek profesyonel bir bug raporu oluşturabilir.")
        
        with col2:
            st.markdown("")
            st.markdown("")
            generate_ai_button = st.button("✨ AI ile Oluştur", type="primary", use_container_width=True)
        
        if generate_ai_button:
            with st.spinner("🤖 Claude AI bug raporu oluşturuyor..."):
                
                # Test adımlarını string'e çevir
                try:
                    steps = json.loads(selected_scenario['steps'])
                    steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
                except:
                    steps_text = selected_scenario['steps']
                
                # AI'dan bug raporu al
                result = generate_bug_report(
                    test_title=selected_scenario['title'],
                    test_steps=steps_text,
                    failure_notes=selected_execution['notes'] or "Belirtilmemiş"
                )
                
                if result.startswith("Hata:"):
                    st.error(f"❌ {result}")
                else:
                    try:
                        # JSON parse et
                        if "```json" in result:
                            result = result.split("```json")[1].split("```")[0].strip()
                        elif "```" in result:
                            result = result.split("```")[1].split("```")[0].strip()
                        
                        bug_data = json.loads(result)
                        
                        # Session state'e kaydet (form için)
                        st.session_state['ai_bug_title'] = bug_data['title']
                        st.session_state['ai_bug_severity'] = bug_data['severity']
                        st.session_state['ai_bug_description'] = bug_data['description']
                        st.session_state['ai_bug_steps'] = bug_data['steps_to_reproduce']
                        st.session_state['ai_bug_expected'] = bug_data['expected_result']
                        st.session_state['ai_bug_actual'] = bug_data['actual_result']
                        
                        st.success("✅ Bug raporu oluşturuldu! Aşağıdaki formu inceleyin ve düzenleyebilirsiniz.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Parse hatası: {str(e)}")
        
        st.markdown("---")
        
        # Bug report formu
        st.markdown("### 📝 Bug Raporu Formu")
        
        with st.form("bug_report_form"):
            
            bug_title = st.text_input(
                "Bug Başlığı *",
                value=st.session_state.get('ai_bug_title', ''),
                placeholder="örn: Login sayfası çöküyor",
                help="Kısa ve açıklayıcı bir başlık"
            )
            
            severity = st.selectbox(
                "Severity (Önem Derecesi) *",
                options=["critical", "high", "medium", "low"],
                index=["critical", "high", "medium", "low"].index(
                    st.session_state.get('ai_bug_severity', 'medium')
                ),
                format_func=lambda x: {
                    "critical": "🔥 Critical (Kritik)",
                    "high": "🔴 High (Yüksek)",
                    "medium": "🟡 Medium (Orta)",
                    "low": "🟢 Low (Düşük)"
                }[x]
            )
            
            description = st.text_area(
                "Açıklama *",
                value=st.session_state.get('ai_bug_description', ''),
                placeholder="Bug'ın detaylı açıklaması...",
                height=100
            )
            
            steps_to_reproduce = st.text_area(
                "Yeniden Üretme Adımları *",
                value=st.session_state.get('ai_bug_steps', ''),
                placeholder="1. Adım\n2. Adım\n3. Adım",
                height=120
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                expected_result = st.text_area(
                    "Beklenen Sonuç *",
                    value=st.session_state.get('ai_bug_expected', ''),
                    placeholder="Ne olması gerekiyordu?",
                    height=80
                )
            
            with col2:
                actual_result = st.text_area(
                    "Gerçekleşen Sonuç *",
                    value=st.session_state.get('ai_bug_actual', ''),
                    placeholder="Ne oldu?",
                    height=80
                )
            
            submit_button = st.form_submit_button("💾 Bug Raporunu Kaydet", type="primary")
            
            if submit_button:
                if not bug_title or not description or not steps_to_reproduce:
                    st.error("❌ Lütfen zorunlu alanları doldurun!")
                else:
                    # Bug raporu oluştur
                    bug_id = create_bug_report(
                        execution_id=selected_execution['id'],
                        title=bug_title,
                        severity=severity,
                        description=description,
                        steps_to_reproduce=steps_to_reproduce,
                        expected_result=expected_result,
                        actual_result=actual_result,
                        ai_generated='ai_bug_title' in st.session_state
                    )
                    
                    st.success(f"✅ Bug raporu başarıyla kaydedildi! (Bug ID: {bug_id})")
                    st.balloons()
                    
                    # Session state temizle
                    for key in ['ai_bug_title', 'ai_bug_severity', 'ai_bug_description', 
                               'ai_bug_steps', 'ai_bug_expected', 'ai_bug_actual']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.rerun()

# ============= TAB 2: Bug Raporları Listesi =============
with tab2:
    st.subheader("📋 Tüm Bug Raporları")
    
    # Jira bağlantı testi
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("")
    with col2:
        if st.button("🔗 Jira Bağlantısını Test Et", type="secondary"):
            with st.spinner("Bağlantı test ediliyor..."):
                result = test_jira_connection()
                if result['success']:
                    if result.get('mock_mode'):
                        st.warning(result['message'])
                    else:
                        st.success(result['message'])
                else:
                    st.error(result['message'])
    
    st.markdown("---")
    
    bugs = get_all_bug_reports()
    
    if len(bugs) == 0:
        st.info("👋 Henüz bug raporu oluşturmadınız.")
    else:
        st.markdown(f"**Toplam {len(bugs)} bug raporu bulundu.**")
        st.markdown("---")
        
        # Her bug için kart
        for bug in bugs:
            with st.expander(f"**#{bug['id']} - {bug['title']}**", expanded=False):
                
                # Severity badge
                severity_colors = {
                    "critical": "🔥",
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                severity_emoji = severity_colors.get(bug['severity'], '⚪')
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"{severity_emoji} **Severity:** {bug['severity'].upper()}")
                    if bug['ai_generated']:
                        st.caption("🤖 AI tarafından oluşturuldu")
                
                with col2:
                    st.caption(f"📅 {bug['created_at'][:10]}")
                
                st.markdown("---")
                
                st.markdown(f"**📝 Açıklama:**")
                st.markdown(bug['description'])
                
                st.markdown(f"**🔄 Yeniden Üretme Adımları:**")
                st.code(bug['steps_to_reproduce'], language=None)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**✅ Beklenen Sonuç:**")
                    st.markdown(bug['expected_result'])
                
                with col2:
                    st.markdown(f"**❌ Gerçekleşen Sonuç:**")
                    st.markdown(bug['actual_result'])
                
                st.markdown("---")
                
                # Butonlar - 3 kolon
                col1, col2, col3 = st.columns([2, 2, 2])
                
                with col1:
                    # TXT indirme butonu
                    bug_text = f"""
BUG REPORT #{bug['id']}
==================

Title: {bug['title']}
Severity: {bug['severity'].upper()}
Date: {bug['created_at'][:10]}

Description:
{bug['description']}

Steps to Reproduce:
{bug['steps_to_reproduce']}

Expected Result:
{bug['expected_result']}

Actual Result:
{bug['actual_result']}
"""
                    st.download_button(
                        label="📄 TXT İndir",
                        data=bug_text,
                        file_name=f"bug_report_{bug['id']}.txt",
                        mime="text/plain",
                        key=f"download_txt_{bug['id']}"
                    )
                
                with col2:
                    # Markdown indirme butonu
                    bug_markdown = f"""# Bug Report #{bug['id']}

## {bug['title']}

**Severity:** {severity_emoji} {bug['severity'].upper()}  
**Date:** {bug['created_at'][:10]}  
**AI Generated:** {'Yes' if bug['ai_generated'] else 'No'}

---

## 📝 Description

{bug['description']}

---

## 🔄 Steps to Reproduce
```
{bug['steps_to_reproduce']}
```

---

## ✅ Expected Result

{bug['expected_result']}

---

## ❌ Actual Result

{bug['actual_result']}

---

*Generated by SmartQA - AI Test Assistant*
"""
                    st.download_button(
                        label="📝 MD İndir",
                        data=bug_markdown,
                        file_name=f"bug_report_{bug['id']}.md",
                        mime="text/markdown",
                        key=f"download_md_{bug['id']}"
                    )
                
                with col3:
                    # JIRA BUTONU
                    if st.button("🎫 Jira'da Task Aç", key=f"jira_{bug['id']}", type="primary"):
                        with st.spinner("Jira issue oluşturuluyor..."):
                            result = create_jira_issue(
                                bug_title=f"[SmartQA] {bug['title']}",
                                bug_description=bug['description'],
                                steps_to_reproduce=bug['steps_to_reproduce'],
                                expected_result=bug['expected_result'],
                                actual_result=bug['actual_result'],
                                severity=bug['severity']
                            )
                            
                            if result['success']:
                                st.success(result['message'])
                                
                                # Issue URL'i göster
                                if 'issue_url' in result:
                                    st.markdown(f"**🔗 Jira Link:** [{result['issue_key']}]({result['issue_url']})")
                                    st.balloons()
                            else:
                                st.error(result['message'])

# Footer
st.markdown("---")
st.caption("💡 **İpucu:** AI ile oluşturulan bug raporlarını istediğiniz gibi düzenleyebilir ve Jira'ya gönderebilirsiniz.")