import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Optimizare viteză
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 1. Configurare Llama 3.2
# Reducem temperatura la 0 pentru viteză și predictibilitate
my_llm = ChatOllama(
    model="llama3.2", 
    base_url="http://localhost:11434", 
    temperature=0, 
    num_ctx=4096, # 8192 e mult pentru audit rapid, 4096 e "sweet spot"
    repeat_penalty=1.2,
    top_p=0.9
)

# 2. Conectare la Biblioteca de Legi
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="db_legal", embedding_function=embeddings)
# k=3 este suficient pentru a găsi legile relevante și a rula instantaneu pe local
retriever = db.as_retriever(search_kwargs={"k": 3})

# ============================================================
# 3. AGENȚI SPECIALIZAȚI — PROMPTURI ANTI-HALUCINARE EXTREMĂ
# ============================================================

expert_legal = Agent(
    role='Auditor Juridic Forensic',
    goal="Identifică clauze ilegale STRICT pe baza legilor date. Fără halucinații.",
    backstory="""Ești auditor juridic. Regula de aur: dacă legea nu o spune explicit, NU inventezi.
    
    INSTRUCȚIUNI CRITICE:
    1. LIMBA: RĂSPUNZI DOAR ÎN LIMBA ROMÂNĂ.
    2. RESTRICȚIE TEXT: FĂRĂ INTRODUCERI ("Iată analiza", "Sigur!"). Începi DIRECT cu formatul cerut.
    3. ANTI-HALUCINARE: NU INVENTA NUMERE DE ARTICOLE (Ex: Art. 999). Dacă nu apare în textul legislativ, spui "conform legislației" sau citezi doar extrasul legal oferit.
    4. STRICT: Bazează-te STRICT pe contextul legislativ oferit. Ce nu e în context, tratează cu maximă precauție.""",
    llm=my_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=120
)

avocat_aparator = Agent(
    role='Analist de Riscuri Contractuale',
    goal="Identifică strict clauzele periculoase și dezechilibrate. Explică simplu.",
    backstory="""Ești analist de risc contractual vizând interesele angajatului/prestatorului.
    
    INSTRUCȚIUNI CRITICE:
    1. LIMBA: RĂSPUNZI DOAR ÎN LIMBA ROMÂNĂ.
    2. RESTRICȚIE TEXT: FĂRĂ BLA-BLA ("Mai jos sunt riscurile..."). Furnizezi DIRECT forma finală analitică.
    3. ANTI-HALUCINARE: Analizează DOAR textul existent în contract, nu inventa clauze care nu există acolo.
    4. TON: Clar, direct, explicat la obiect.""",
    llm=my_llm,
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=120
)

redactor_juridic = Agent(
    role='Redactor Juridic',
    goal="Redactează documentul juridic folosind STRICT regulile primite.",
    backstory="""Ești redactor de contracte ireproșabile.
    
    INSTRUCȚIUNI CRITICE:
    1. LIMBA: RĂSPUNZI DOAR ÎN LIMBA ROMÂNĂ.
    2. RESTRICȚIE TEXT: AFIȘEAZĂ DOAR TEXTUL DOCUMETULUI. Fără "Acesta este contractul:", "Am terminat...".
    3. ANTI-HALUCINARE: Când introduci drepturi, folosește doar drepturi aplicabile în România, nu inventa concepte străine.
    4. FORMAT: Folosește o structură de PĂRȚI, OBIECT, DREPTURI, OBLIGAȚII, art.1, art.2.""",
    llm=my_llm,
    allow_delegation=False,
    verbose=True,
    max_iter=3,
    max_execution_time=120
)

avocat_redactor = Agent(
    role='Reparator de Clauze',
    goal="Corectează 1 la 1 clauzele semnalate, rescriindu-le legal.",
    backstory="""Ești expert în rescriere și reparare.
    
    INSTRUCȚIUNI CRITICE:
    1. LIMBA: RĂSPUNZI DOAR ÎN LIMBA ROMÂNĂ.
    2. RESTRICȚIE TEXT: Fără cuvinte de introducere. Doar o listă structurată cu corecturile.
    3. Fără adăugiri superflue. Rescrie strict respectând spiritul comercial dar în legalitate absolută.""",
    llm=my_llm,
    allow_delegation=False,
    verbose=True,
    max_iter=3,
    max_execution_time=120
)

arhitect_contracte = Agent(
    role='Optimizator Contractual Pro-Semnatar',
    goal="Combină contractul vechi cu corecturile și generează varianta avantajoasă 100%.",
    backstory="""Ești strategul care domină negocierea.
    
    INSTRUCȚIUNI CRITICE:
    1. LIMBA: RĂSPUNZI DOAR ÎN LIMBA ROMÂNĂ.
    2. RESTRICȚIE TEXT: Răspunde DIRECT prin textul documentului refăcut, urmat de tabel. NICIUN alt comentariu ("Aici aveți contractul...").
    3. Fii curajos dar legal: minimizează durata preavizului pentru plecare, maximează concediul.""",
    llm=my_llm,
    allow_delegation=False,
    verbose=True,
    max_iter=3,
    max_execution_time=120
)

# ============================================================
# 4. FUNCȚII — TASK-URI
# ============================================================

def repara_clauze_contract(raport_audit, text_original):
    t_repara = Task(
        description=f"""
        DOCUMENTE DE LUCRU:
        RAPORT DE AUDIT (probleme găsite):
        {raport_audit}
        
        TEXT ORIGINAL CONTRACT:
        {text_original}
        
        CERINȚĂ:
        Răspunde STRICT cu clauzele afectate, corectate, folosind acest EXACT ȘABLON:
        
        ❌ Original: [clauza]
        ✅ Corectat: [forma legală]
        💡 Motiv: [motiv scurt]
        ---
        
        REGULI IMPORTANTE:
        - FĂRĂ text introductiv la începutul răspunsului.
        - NU rescrie ce e deja legal.
        - RESPINGE FĂRĂ PĂRUT DE RĂU orice abuz de genul: "disponibilitate", "confidențialitate neplătită extinsă", "preaviz uriaș".
        - RESPUNS UNIC ÎN ROMÂNĂ.
        - ATENȚIE: MEREU trebuie să începi răspunsul tău EXACT cu aceste cuvinte "Final Answer: " urmat imediat de text.
        """,
        agent=avocat_redactor,
        expected_output="O listă structurată strict cu clauzele corectate."
    )
    
    crew = Crew(agents=[avocat_redactor], tasks=[t_repara])
    return crew.kickoff()


def auditeaza_contract_complet(text_contract):
    # Reducem drastic limita de caractere la 3000 pentru viteză optimă pe Llama local
    text_de_analizat = text_contract[:3000]
    if len(text_contract) > 3000:
        text_de_analizat += "\n\n[...TEXT TRUNCHIAT DIN CAUZA LIMITELOR DE PROCESARE. ANALIZĂ PARȚIALĂ...]"

    # Facem query-ul dinamic pe baza primei părți a contractului
    # Astfel DB-ul va ști dacă e un contract de muncă sau unul de prestări servicii (B2B)
    intro_contract = text_contract[:200].replace('\n', ' ')
    query_audit = f"Contract: {intro_contract}. Subiecte: clauze abuzive, reziliere, obligații, penalități, drepturi."
    docs = retriever.invoke(query_audit)
    context_din_legi = "\n\n".join([d.page_content for d in docs])
    
    t1 = Task(
        description=f"""
        DOCUMENTE DE ANALIZAT:
        CONTRACT ORIGINAL (AUDITEAZĂ ASTA):
        {text_de_analizat}
        
        CONTEXT LEGISLAȚIE EXTRAS (BAZEAZĂ-TE 100% PE ASTA PENTRU A EVITA HALUCINAȚIILE):
        {context_din_legi}
        
        CERINȚĂ: 
        1. Caută nelegalități (Timp muncă depășit, preaviz ilegal, lipsă repaus repaus minimal, clauze nescrise nule).
        2. RĂSPUNDE STRICT PE BAZA LEGISLAȚIEI EXtrase, Dar ESTE STRICT INTERZIS SĂ DAI NUMERE DE LEGI (ex. "conform art. 75"). Acest contract poate fi B2B și nu se aplică pe Codul Muncii cu numere fixe. Explică doar de ce principiul legal e încălcat.
        3. Identifică doar 3-5 ilegalități majore pentru a fi fluid și concis.
        
        FORMAT (PRODUCE STRICT ACEST FORMAT, NIMIC EXTRA):
        ## 🔴 NULE ABSOLUT 
        - [clauză] -> de ce încalcă legea.
        
        ## 🟠 ABUZIVE
        - [clauză] -> explicație de dezechilibru.
        
        Atenție: DĂ DIRECT RĂSPUNSUL FĂRĂ NICIUN TEXT ÎNAINTE. ÎN ROMÂNĂ.
        ATENȚIE: MEREU trebuie să începi răspunsul tău EXACT cu aceste cuvinte "Final Answer: " urmat imediat de text.
        """,
        agent=expert_legal,
        expected_output="Raport de audit cu categorii clare, fără introduceri, bazat pe 3-5 ilegalități majore."
    )
    
    t2 = Task(
        description=f"""
        CONTRACT ORIGINAL (PENTRU RISCURI):
        {text_de_analizat}
        
        CERINȚĂ:
        Identifică vulnerabilități și capcane de practică:
        - Angajatorul te poate da afară ușor dar tu ai preaviz 30+ zile? 
        - Restricții ascunse post angajare?
        - Responsabilități exagerate pentru salariu fix?
        Fii scurt: identifică doar 3-5 capcane majore.
        
        REGULĂ STRICTĂ: EXPLICĂ RISCUL COMERCIAL. ESTE STRICT INTERZIS SĂ CITEZI NUMERE DE LEGI (ex. "art. 75", "art. 123", "Legea 53" etc). ACESTA POATE FI UN CONTRACT B2B (Codul Civil) IAR TU NU EȘTI JURIST. Nu asocia clauzele cu legislația, explică doar de ce e o "țeapă" logică și practică.
        
        FORMAT (FĂRĂ INTRODUCERE! DOAR RĂSPUNS STRUCTURAT):
        
        🔴 **Risc Critic**: [clauza] - [ce te afectează pe tine ca om]
        🟠 **Risc Mediu**: [clauza] - [disconfort]
        
        Verdict final direct la sfârșit.
        ATENȚIE: MEREU trebuie să începi răspunsul tău EXACT cu aceste cuvinte "Final Answer: " urmat imediat de text.
        """,
        agent=avocat_aparator,
        expected_output="Analiză scurtă de riscuri practice, bazată pe 3-5 capcane, făr text extra, clară, română."
    )

    # IMPORTANT: Dacă Llama se blochează, încearcă să rulezi doar UN task prima dată
    crew = Crew(
        agents=[expert_legal, avocat_aparator], 
        tasks=[t1, t2], 
        process=Process.sequential,
        verbose=True
    )
    return crew.kickoff()


def genereaza_document(cerinta):
    context = "\n\n".join([d.page_content for d in retriever.invoke(cerinta)])
    
    t1 = Task(
        description=f"""
        CERINȚĂ: {cerinta}
        
        CONTEXT LEGAL (BAZEAZĂ-TE 100% PE ASTA, FĂRĂ INVENȚII):
        {context}
        
        EXTRAGE REGULILE, DREPTURILE ȘI INTERDICȚIILE.
        - Regula 1 
        - Regula 2
        
        ATENȚIE: MEREU trebuie să începi răspunsul tău EXACT cu aceste cuvinte "Final Answer: " urmat imediat de text.
        """,
        agent=expert_legal,
        expected_output="Lista de reguli legale. Gata."
    )
    
    t2 = Task(
        description=f"""
        CERINȚĂ: {cerinta}
        
        REDACTEAZĂ ÎNTREGUL CONTRACT. 
        NU PUNE TEXT DE PREZENTARE. Începe cu titlul contractului.
        Trebuie să acopere totul: Părți, Obiect, Durată, Bani, Obligații, Drepturi Minime(Concediu), Reziliere, Forță Majoră.
        Folosește "DE COMPLETAT" unde nu ai date.
        ROMÂNĂ doar.
        ATENȚIE: MEREU trebuie să începi răspunsul tău EXACT cu aceste cuvinte "Final Answer: " urmat imediat de text.
        """,
        agent=redactor_juridic,
        expected_output="Documentul juridic finalizat și complet, afișat direct."
    )
    
    crew = Crew(agents=[expert_legal, redactor_juridic], tasks=[t1, t2], process=Process.sequential)
    return crew.kickoff()


def genereaza_contract_favorabil(text_original, audit_legal, analiza_risc):
    t_rewrite = Task(
        description=f"""
        RESCRIE INTEGRAL CONTRACTUL SĂ FIE ÎN AVANTAJUL TOTAL AL SEMNATARULUI.
        
        ACTE:
        1. ORIGINAL:
        {text_original[:3000]}
        2. ILEGALITĂȚI De șters/modificat:
        {audit_legal}
        3. RISCURI De tăiat:
        {analiza_risc}
        
        REGULI EXTREM DE STRICTE:
        1. EȘTI OBLIGAT SĂ SCRII TOT TEXTUL CONTRACTULUI NOU ÎN ÎNTREGIME, DE LA PUNCT LA PUNCT, conform originalului dar cu clauzele abuzive schimbate în favoarea prestatorului/angajatului.
        2. Marchează fiecare titlu modificat cu: "Art. X [MODIFICAT ÎN FAVOAREA TA]".
        3. Fii dur: taie confidențialitățile infinite, echilibrează preavizele, adaugă concediu legal complet.
        
        Atenție: MEREU trebuie să începi răspunsul tău EXACT cu "Final Answer: " urmat de acest șablon OBLIGATORIU:
        Final Answer: 
        ### CONTRACTUL NOU COMPLET
        [Scrie aici, fără nicio introducere, întreg contractul modificat de la primul la ultimul articol]
        
        ### REZUMATUL MODIFICĂRILOR
        | Ce am modificat | Ce era înainte | Noua formă protectoare |
        [Tabelul aici]
        """,
        agent=arhitect_contracte,
        expected_output="Contract final optimizat, urmat de tabel. Fără alte texte în plus."
    )
    
    crew = Crew(agents=[arhitect_contracte], tasks=[t_rewrite])
    return crew.kickoff()