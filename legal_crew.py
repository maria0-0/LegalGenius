import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Optimizare viteza procesare
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 1. Configurare Creier
my_llm = ChatOllama(model="llama3", base_url="http://localhost:11434", temperature=0.1) # Temperatura mica = precizie mare

# 2. Conectare la "Biblioteca de Legi"
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="db_legal", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 5}) # Luam mai mult context (5 fragmente)

# 3. DEFINIRE AGENȚI "ELITĂ"
avocat_detectiv = Agent(
    role='Detectiv Juridic specializat pe Contracte',
    goal='Să găsească clauze ilegale, abuzive sau care dezavantajează salariatul conform Codului Muncii.',
    backstory="""Ești cel mai temut avocat de dreptul muncii. Nu ești politicos. 
    Analizezi fiecare cuvânt pentru a vedea dacă încalcă drepturile salariatului[cite: 131, 132]. 
    Dacă o clauză este ambiguă, o marchezi ca RISC MAJOR.""",
    llm=my_llm,
    verbose=True
)

expert_legislativ = Agent(
    role='Expert în Legislația României',
    goal='Să valideze clauzele contractuale folosind strict articolele de lege din contextul oferit.',
    backstory="""Ești un expert care cunoaște Codul Muncii pe de rost. 
    Sarcina ta este să oferi temeiul legal (Articolul de lege) pentru fiecare risc găsit de Detectiv[cite: 38, 96, 109].""",
    llm=my_llm,
    verbose=True
)

# 4. FUNCȚIA DE ANALIZĂ AVANSATĂ
def ruleaza_analiza_profesionista(text_pdf):
    # Căutăm legile relevante în db_legal
    context_legal = "\n\n".join([d.page_content for d in retriever.invoke(text_pdf)])
    
    # Task 1: Identificare Riscuri
    t1 = Task(
        description=f"""Analizează acest contract: {text_pdf}. 
        Identifică 3 clauze care ar putea fi problematice pentru salariat. 
        Fii foarte specific și citează fragmentele din contract.""",
        agent=avocat_detectiv,
        expected_output="O listă tehnică cu clauzele suspecte și de ce sunt periculoase."
    )

    # Task 2: Validare cu Codul Muncii
    t2 = Task(
        description=f"""Analizează riscurile găsite anterior folosind acest context legal: {context_legal}.
        Spune clar: 'Această clauză încalcă Articolul X' sau 'Este conformă cu Articolul Y'.
        Răspunde obligatoriu în LIMBA ROMÂNĂ.""",
        agent=expert_legislativ,
        expected_output="Raport juridic final cu temei legal pentru fiecare observație."
    )

    crew = Crew(
        agents=[avocat_detectiv, expert_legislativ],
        tasks=[t1, t2],
        process=Process.sequential
    )
    
    return crew.kickoff()

if __name__ == "__main__":
    # Aici pui textul extras din PDF-ul tău sau o mostră
    proba_contract = "Salariatul va munci 12 ore pe zi. Orele suplimentare nu se plătesc."
    print(ruleaza_analiza_profesionista(proba_contract))