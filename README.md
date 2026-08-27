## Set Up Virtual Environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
#  macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

flashcard-generator/
├── .env                  # Environment secrets (Local only, ignored by Git)
├── .gitignore            # Git exclusion rules
├── app.py                # Core application, UI components & Gemini logic
├── requirements.txt      # Python dependencies list
├── saved_deck.json       # Auto-saved local flashcard database
└── README.md             # Project documentation & guides