⚖️ Legal Genius Pro: Sistem Expert Juridic (RAG + Multi-Agent)
Legal Genius Pro este o aplicație avansată de audit și generare de contracte, care utilizează tehnologia RAG (Retrieval-Augmented Generation) și un sistem de agenți AI coordonați pentru a oferi consultanță juridică de precizie.

Aplicația este optimizată pentru legislația din România și rulează folosind modelul Llama 3.3 70B prin infrastructura ultra-rapidă Groq.

🚀 Funcționalități Principale
🔍 Audit Contractual Inteligent: Identifică automat clauzele abuzive, nule sau riscante dintr-un document PDF încărcat.

⚖️ Analiză bazată pe Legi Reale: Sistemul consultă o bază de date locală (Codul Muncii, Codul Civil) înainte de a răspunde, eliminând halucinațiile AI.

✍️ Generare Documente: Redactează contracte noi (muncă, prestări servicii, NDA) conform cerințelor specifice, respectând normele legale.

✨ Optimizare Favorabilă: Rescrie contractele existente pentru a maximiza protecția semnatarului (angajat sau prestator).

🛠️ Tehnologii Utilizate
Framework AI: CrewAI (pentru orchestrarea agenților specializați).

LLM (Creierul): Llama 3.3 70B via Groq Cloud.

Interfață: Streamlit.

Bază de Date Vectorială: ChromaDB.

Embeddings: HuggingFace (all-MiniLM-L6-v2).

📋 Instalare și Configurare Locală
Dacă dorești să rulezi proiectul pe calculatorul tău:

Clonează repository-ul:

Bash
git clone https://github.com/utilizator/LegalGenius.git
cd LegalGenius
Instalează dependințele:

Bash
pip install -r requirements.txt
Configurează variabilele de mediu:
Creează un fișier .env în folderul rădăcină și adaugă cheia ta API:

Plaintext
GROQ_API_KEY=gsk_pune_cheia_ta_aici
Pregătește baza de date:
Pune fișierele tale PDF cu legi în folderul knowledge_base și rulează:

Bash
python ingest.py
Pornește aplicația:

Bash
streamlit run app.py
☁️ Deploy pe Streamlit Cloud
Proiectul este configurat pentru deploy automat. Asigură-te că adaugi GROQ_API_KEY în secțiunea Secrets din tabloul de bord Streamlit Cloud pentru ca agenții să poată comunica cu modelul Llama