import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Configurare LLM
my_llm = ChatOllama(model="llama3", base_url="http://localhost:11434")

# 2. Unealta de căutare
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="db_legal", embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 2})

# 3. Definim Agenții
analist = Agent(
    role='Avocat Expert în Riscuri',
    goal='Identifică 3 probleme în contract.',
    backstory='Ești un expert juridic meticulos.',
    llm=my_llm,
    verbose=True
)

# 4. Funcția de rulare
def ruleaza(text):
    context = "\n\n".join([d.page_content for d in retriever.invoke(text)])
    
    task = Task(
        description=f"Analizează contractul: {text}\n\nFolosește acest context legal: {context}",
        agent=analist,
        expected_output="Raport de risc cu 3 puncte."
    )
    
    return Crew(agents=[analist], tasks=[task]).kickoff()

if __name__ == "__main__":
    print("🚀 Testăm agenții...")
    print(ruleaza("Contract: Plata la 200 de zile, fără retur."))