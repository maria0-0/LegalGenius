import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configurații de căi
KNOWLEDGE_DIR = "knowledge_base"
VECTOR_DB_DIR = "db_legal"

def run_ingestion():
    # 1. Verificăm dacă există folderul cu PDF-uri
    if not os.path.exists(KNOWLEDGE_DIR) or not os.listdir(KNOWLEDGE_DIR):
        print(f"❌ EROARE: Folderul '{KNOWLEDGE_DIR}' e gol sau lipsește.")
        return

    print("⏳ Pasul 1: Încărcăm PDF-urile juridice...")
    loader = DirectoryLoader(KNOWLEDGE_DIR, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    print(f"✅ Am încărcat {len(documents)} pagini.")

    print("⏳ Pasul 2: Tăiem textul în fragmente (Chunks)...")
    # Folosim Recursive pentru a nu tăia frazele juridice la jumătate
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Avem {len(chunks)} fragmente de text gata pentru procesare.")

    print("⏳ Pasul 3: Transformăm textul în vectori (Embeddings)...")
    # Acest model rulează local pe CPU/GPU-ul tău
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"⏳ Pasul 4: Salvăm totul în baza de date '{VECTOR_DB_DIR}'...")
    # Creăm și salvăm baza de date pe disc
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    
    print("🚀 SUCCES! Baza de date legală a fost creată.")
    print("Acum poți vedea folderul 'db_legal' în proiectul tău.")

if __name__ == "__main__":
    run_ingestion()