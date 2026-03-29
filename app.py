import streamlit as st
from pypdf import PdfReader
from legal_crew import  auditeaza_contract_complet, genereaza_contract_favorabil, genereaza_document, repara_clauze_contract
import os
from ingest import run_ingestion

if 'audit_efectuat' not in st.session_state:
    st.session_state['audit_efectuat'] = False

if not os.path.exists("db_legal"):
    with st.spinner("Se configurează baza de date juridică pentru prima dată..."):
        run_ingestion()

        
# 1. Configurare Vizuală
st.set_page_config(page_title="Legal Genius Pro", page_icon="⚖️", layout="wide")

st.title("⚖️ Legal Genius Pro: Sistem Expert Juridic")
st.markdown("---")

# 2. Crearea Tab-urilor pentru o experiență 2-în-1
tab1, tab2 = st.tabs(["🔍 Audit Contract Existent", "✍️ Generare Contract Nou"])

# --- TAB 1: AUDIT JURIDIC ---
with tab1:
    st.header("Analiză și Identificare Riscuri")
    uploaded_file = st.file_uploader("Încarcă contractul PDF pentru audit", type="pdf", key="audit_upload")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text_contract = ""
        for page in reader.pages:
            text_contract += page.extract_text()
            
        with st.expander("Vezi textul extras din PDF"):
            st.write(text_contract)
            
        if st.button("🚀 Scanează Contractul (Audit Complet)"):
            with st.spinner("Analiză în curs..."):
                rezultat_crew = auditeaza_contract_complet(text_contract)
                
                # Verificăm dacă e obiect CrewOutput sau doar un String
                if hasattr(rezultat_crew, 'tasks_output') and len(rezultat_crew.tasks_output) >= 2:
                    # Varianta optimă: extragem task-urile separat
                    st.session_state['rezultat_legal'] = rezultat_crew.tasks_output[0].raw
                    st.session_state['rezultat_risc'] = rezultat_crew.tasks_output[1].raw
                else:
                    # Varianta de rezervă: dacă primim totul ca un singur text
                    full_text = str(rezultat_crew)
                    # Împărțim textul în două (aproximativ) sau îl punem pe tot în ambele
                    st.session_state['rezultat_legal'] = full_text
                    st.session_state['rezultat_risc'] = "Analiza de risc este inclusă în raportul de mai sus."
                
                st.session_state['audit_efectuat'] = True

        # 2. Afișarea rezultatelor (dacă există)
        if st.session_state.get('audit_efectuat'):
            st.error("⚖️ Raport de Audit și Analiză Riscuri")
            st.markdown(st.session_state['rezultat_legal'])
            
            # Afișăm și al doilea text doar dacă acesta chiar există și nu este doar un placeholder
            if "Analiza de risc este inclusă" not in st.session_state['rezultat_risc']:
                st.markdown("---")
                st.markdown(st.session_state['rezultat_risc'])

            # 3. Butonul de GENERARE CONTRACT NOU (folosește datele salvate)
            if st.button("✨ Generează Contractul Optimizat"):
                with st.spinner("Se reconstruiește contractul în beneficiul tău..."):
                    # Aici nu mai dă eroare pentru că luăm datele din st.session_state
                    contract_nou = genereaza_contract_favorabil(
                        text_contract, 
                        st.session_state['rezultat_legal'], 
                        st.session_state['rezultat_risc']
                    )
                    st.markdown("### 📄 Noul tău Contract (Varianta Ideală)")
                    st.text_area("Contract Rescris:", value=contract_nou, height=500)
                                
# --- TAB 2: GENERARE DOCUMENTE ---
with tab2:
    st.header("Redactare Contracte de la Zero")
    st.write("Introdu cerințele tale, iar AI-ul va consulta Codul Civil și Codul Muncii pentru a redacta documentul.")
    
    col1, col2 = st.columns(2)
    with col1:
        tip_contract = st.selectbox("Tipul de document", [
            "Contract Individual de Muncă",
            "Contract de Prestări Servicii",
            "Clauză de Confidențialitate (NDA)",
            "Act Adițional",
            "Contract de Închiriere"
        ])
    with col2:
        detalii_suplimentare = st.text_input("Detalii specifice (ex: salariu, durată, nume părți)")

    cerinta_finala = f"Redactează un {tip_contract}. Detalii: {detalii_suplimentare}"

    if st.button("Generează Documentul", key="btn_gen"):
        with st.spinner("Redactorul AI scrie documentul conform legii..."):
            document_final = genereaza_document(cerinta_finala)
            st.success("Document Generat!")
            st.text_area("📄 Document Rezultat", value=document_final, height=400)
            
            st.download_button(
                label="Descarcă Documentul (.txt)",
                data=str(document_final),
                file_name=f"{tip_contract.replace(' ', '_')}.txt",
                mime="text/plain"
            )

# Footer informativ
st.markdown("---")
st.caption("Powered by Llama 3.2 & RAG Technology. Toate datele sunt procesate local pentru confidențialitate maximă.")