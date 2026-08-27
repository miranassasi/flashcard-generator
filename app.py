import html
import json
import os
import random

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
st.set_page_config(page_title="FlashCard", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

STORAGE_FILE = "saved_deck.json"

# --- Data Models (Pydantic Schema) ---
class FlashcardItem(BaseModel):
    id: int = Field(description="Card sequence index")
    question: str = Field(description="The primary question, term, or concept to remember")
    answer: str = Field(description="Detailed answer, explanation, pinyin, or translation")
    category: str = Field(description="Broad category like Chinese, Science, Tech, History")
    tag: str = Field(description="Sub-topic tag like Vocabulary, Grammar, HSK, Biology")
    difficulty: str = Field(description="Difficulty level: Easy, Medium, or Hard")


class FlashcardDeck(BaseModel):
    cards: list[FlashcardItem] = Field(description="List of generated flashcards")


# ฟังก์ชันโหลดและบันทึกลง Local File อัตโนมัติ
def load_persisted_deck():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return SAMPLE_CARDS.copy()


def save_persisted_deck(cards):
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving deck locally: {e}")


def get_api_key():
    local_key = os.getenv("GEMINI_API_KEY")
    if local_key and local_key.strip():
        return local_key.strip()
    try:
        cloud_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        cloud_key = None
    return cloud_key.strip() if isinstance(cloud_key, str) and cloud_key.strip() else None


SAMPLE_CARDS = [
    {"id": 1, "question": "What is the capital of Japan?", "answer": "Tokyo is the capital and largest city of Japan.", "category": "Geography", "tag": "Asia", "difficulty": "Easy"},
    {"id": 2, "question": "Which ocean is the largest on Earth?", "answer": "The Pacific Ocean is the largest and deepest ocean basin.", "category": "Geography", "tag": "Oceans", "difficulty": "Medium"},
    {"id": 3, "question": "What does photosynthesis produce?", "answer": "It converts light energy into chemical energy, producing glucose and oxygen.", "category": "Science", "tag": "Biology", "difficulty": "Medium"},
    {"id": 4, "question": "Who wrote 'Pride and Prejudice'?", "answer": "Jane Austen wrote the novel, first published in 1813.", "category": "Literature", "tag": "Classics", "difficulty": "Easy"},
    {"id": 5, "question": "What is the purpose of a SQL JOIN?", "answer": "A JOIN combines rows from two or more tables using a related column.", "category": "Technology", "tag": "Databases", "difficulty": "Hard"},
    {"id": 6, "question": "What is the derivative of x²?", "answer": "The derivative of x² with respect to x is 2x.", "category": "Mathematics", "tag": "Calculus", "difficulty": "Hard"},
]


def css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    :root{--bg:#0d0e12;--surface:#1a1c23;--border:#2b2d38;--gold:#FFE600;--muted:#a0a5b5}
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:var(--bg);color:#fff}.block-container{max-width:1440px;padding:2rem 3rem 4rem}
    [data-testid="stSidebar"]{background:#121316;border-right:1px solid var(--border)}[data-testid="stSidebar"]>div:first-child{padding:1.5rem 1rem}
    h1,h2,h3{font-family:'Plus Jakarta Sans',sans-serif!important;color:#fff!important;letter-spacing:-.035em}h1{font-size:2.1rem!important;margin-bottom:.2rem!important}p,label,.stCaption{color:var(--muted)!important}
    .brand{padding:.25rem .75rem 1.75rem;font-family:'Plus Jakarta Sans';color:#fff;font-size:1.35rem;font-weight:800;letter-spacing:-.05em}.brand-mark{color:var(--gold);margin-right:.48rem}.nav-caption{color:#6f7483;font-size:.68rem;font-weight:700;letter-spacing:.12em;margin:1.4rem .75rem .45rem}
    [data-testid="stSidebar"] [data-testid="stButton"] button, [data-testid="stSidebar"] [data-testid="stDownloadButton"] button{background:transparent;color:#aeb3c2;border:0;border-radius:10px;text-align:left;padding:.65rem .75rem;font-weight:600}[data-testid="stSidebar"] [data-testid="stButton"] button:hover, [data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover{background:#20222a;color:#fff}[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:rgba(255,230,0,.16);color:var(--gold);box-shadow:inset 3px 0 0 var(--gold),0 0 16px rgba(255,230,0,.12)}
    [data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:#181a20!important;color:#fff!important;border:1px solid var(--border)!important;border-radius:12px!important}[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:var(--gold)!important;box-shadow:0 0 0 1px var(--gold)!important}
    .topbar{display:flex;justify-content:space-between;align-items:center;min-height:45px;margin-bottom:2.1rem}.crumb{color:var(--muted);font-size:.88rem}.crumb strong{color:#fff;font-weight:600}.top-icons{color:var(--muted);letter-spacing:.7rem;font-size:1.1rem}.eyebrow{color:var(--gold);font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.13em}.page-subtitle{color:var(--muted);font-size:.95rem;margin:.25rem 0 1.6rem}.stat-line{color:var(--muted);font-size:.88rem;margin-top:.4rem}.stat-line span{color:#fff;font-weight:700}
    .flashcard{background:linear-gradient(145deg,#20222a,#191b22);border:1px solid rgba(255,230,0,.55);border-radius:18px;min-height:370px;padding:30px 36px;display:flex;flex-direction:column;box-shadow:0 0 0 1px rgba(255,230,0,.12),0 16px 55px rgba(0,0,0,.32),0 0 45px rgba(255,230,0,.10)}.flashcard-head{display:flex;align-items:center;justify-content:space-between;color:var(--muted);font-size:.74rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.edit-icon{color:var(--gold);font-size:1rem}.flashcard-content{flex:1;display:flex;align-items:center;justify-content:center;text-align:center;padding:2rem 1rem;font-family:'Plus Jakarta Sans';font-size:clamp(1.55rem,3vw,2.55rem);font-weight:700;line-height:1.3;color:#fff}.flashcard.answer .flashcard-content{color:#f5f5f7;font-size:clamp(1.2rem,2.4vw,1.85rem);font-family:'DM Sans';font-weight:500}.badges{display:flex;gap:8px}.badge{border:1px solid #444652;background:#252730;border-radius:99px;color:#b9bdc9;font-size:.72rem;padding:5px 10px}.progress-meta{display:flex;justify-content:space-between;color:var(--muted);font-size:.83rem;margin:.3rem 0 .55rem}.progress-meta strong{color:#fff}[data-testid="stProgress"]>div>div{background:var(--gold)!important}
    .control-bar{background:#16181e;border:1px solid var(--border);border-radius:16px;padding:.55rem;max-width:780px;margin:1.65rem auto 0}[data-testid="stButton"] button, [data-testid="stDownloadButton"] button{border:1px solid #343641;background:#20222a;color:#e9eaf0;border-radius:11px;min-height:42px;font-weight:700}[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover{color:#fff;border-color:#595b66;background:#292b34}[data-testid="stButton"] button[kind="primary"], [data-testid="stDownloadButton"] button[kind="primary"]{background:var(--gold);border-color:var(--gold);color:#000000;font-weight:800;box-shadow:0 0 20px rgba(255,230,0,0.45),0 7px 18px rgba(255,230,0,.20)}[data-testid="stButton"] button[kind="primary"]:hover, [data-testid="stDownloadButton"] button[kind="primary"]:hover{background:#fff36a;color:#000000}
    .deck-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;min-height:190px;padding:20px;margin-bottom:1rem}.deck-card:hover{border-color:#535563}.deck-label{color:#777d8d;font-size:.67rem;letter-spacing:.12em;font-weight:800}.deck-question{color:#fff;font-family:'Plus Jakarta Sans';font-size:1.03rem;font-weight:700;line-height:1.35;margin:.6rem 0 .7rem}.deck-answer{color:#aeb3c2;font-size:.84rem;line-height:1.5;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.deck-footer{color:#7b8190;font-size:.7rem;margin-top:1rem}.empty-state{background:var(--surface);border:1px dashed #3b3d48;border-radius:18px;padding:4rem 2rem;text-align:center;color:var(--muted)}.empty-state h3{color:#fff!important;margin-bottom:.45rem}.filter-title{color:#808697;font-size:.75rem;font-weight:700;margin-top:.35rem}
    div[data-testid="stRadio"] label{background:#1b1d24;border:1px solid var(--border);border-radius:99px;padding:5px 13px;color:#b9bdc9!important}div[data-testid="stRadio"] label:has(input:checked){border-color:var(--gold);background:rgba(255,230,0,.14);color:var(--gold)!important;box-shadow:0 0 14px rgba(255,230,0,.12)}div[data-testid="stRadio"] label div:first-child{display:none}@media(max-width:800px){.block-container{padding:1.25rem 1rem 3rem}.flashcard{min-height:320px;padding:24px 20px}}
    </style>""", unsafe_allow_html=True)


def init_state():
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = load_persisted_deck()
    for key, value in {"card_idx": 0, "show_answer": False, "view": "Collection", "filter": "All"}.items():
        if key not in st.session_state:
            st.session_state[key] = value


def switch(view):
    st.session_state.view = view
    if view == "Study Mode":
        st.session_state.show_answer = False


def sidebar():
    with st.sidebar:
        st.markdown('<div class="brand"><span class="brand-mark">✦</span>FlashCard</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-caption">WORKSPACE</div>', unsafe_allow_html=True)
        if st.button("▦  My Collection", key="collection", use_container_width=True, type="primary" if st.session_state.view == "Collection" else "secondary"):
            switch("Collection")
            st.rerun()
        if st.button("◈  Study Mode", key="study", use_container_width=True, type="primary" if st.session_state.view == "Study Mode" else "secondary"):
            switch("Study Mode")
            st.rerun()
        st.markdown('<div class="nav-caption">CREATE & IMPORT</div>', unsafe_allow_html=True)
        if st.button("✦  AI Generator", key="generator", use_container_width=True, type="primary" if st.session_state.view == "Generator" else "secondary"):
            switch("Generator")
            st.rerun()
        if st.button("📥  Import Deck", key="import_deck", use_container_width=True, type="primary" if st.session_state.view == "Import" else "secondary"):
            switch("Import")
            st.rerun()


def topbar():
    st.markdown('<div class="topbar"><div class="crumb">Workspace <span style="color:#555b69">/</span> <strong>My flashcards</strong></div><div class="top-icons">⌕ ◌</div></div>', unsafe_allow_html=True)


def study_view():
    cards = st.session_state.flashcards
    if not cards:
        return empty("Your deck is ready for its first card", "Generate a deck or import a saved JSON file.")
    st.session_state.card_idx = min(st.session_state.card_idx, len(cards) - 1)
    card = cards[st.session_state.card_idx]
    n = st.session_state.card_idx + 1
    total = len(cards)
    
    st.markdown('<div class="eyebrow">Focused learning</div><h1>Study mode</h1><div class="page-subtitle">Take your time. Flip the card when you are ready.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="progress-meta"><span><strong>{n} of {total}</strong> cards</span><span>{int(n/total*100)}%</span></div>', unsafe_allow_html=True)
    st.progress(n / total)
    
    answer = st.session_state.show_answer
    text = card["answer"] if answer else card["question"]
    label = "Answer" if answer else "Question"
    cls = "flashcard answer" if answer else "flashcard"
    
    st.markdown(f'<div class="{cls}"><div class="flashcard-head"><span>{label}</span><span class="edit-icon">⌑</span></div><div class="flashcard-content">{html.escape(text)}</div><div class="badges"><span class="badge">{html.escape(card.get("category","General"))}</span><span class="badge">{html.escape(card.get("tag","Topic"))}</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="control-bar">', unsafe_allow_html=True)
    prev, flip, nxt = st.columns([1, 1.25, 1])
    with prev:
        if st.button("←  Previous", use_container_width=True, disabled=(n == 1)):
            st.session_state.card_idx -= 1
            st.session_state.show_answer = False
            st.rerun()
    with flip:
        if st.button("↻  Flip card", key="flip", type="primary", use_container_width=True):
            st.session_state.show_answer = not answer
            st.rerun()
    with nxt:
        if st.button("Next  →", use_container_width=True, disabled=(n == total)):
            st.session_state.card_idx += 1
            st.session_state.show_answer = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def collection_view():
    cards = st.session_state.flashcards
    head, actions = st.columns([2.5, 2.5])
    with head:
        st.markdown('<div class="eyebrow">Your library</div><h1>General knowledge</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-line"><span>{len(cards)}</span> cards · Auto-saved</div>', unsafe_allow_html=True)
    with actions:
        col_json, col_shuf, col_study = st.columns([1.1, 1, 1.2])
        st.markdown('<div style="height:1.9rem"></div>', unsafe_allow_html=True)
        with col_json:
            json_str = json.dumps(cards, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 Export JSON",
                data=json_str,
                file_name="flashcards_deck.json",
                mime="application/json",
                use_container_width=True
            )
        with col_shuf:
            if st.button("⤨ Shuffle", use_container_width=True):
                random.shuffle(st.session_state.flashcards)
                save_persisted_deck(st.session_state.flashcards)
                st.session_state.card_idx = 0
                st.rerun()
        with col_study:
            if st.button("▶ Study mode", type="primary", use_container_width=True):
                switch("Study Mode")
                st.rerun()
                
    st.markdown('<div class="filter-title">FILTER BY DIFFICULTY</div>', unsafe_allow_html=True)
    options = ["All", "Hard", "Medium", "Easy"]
    selected = st.radio("Filter cards", options, horizontal=True, label_visibility="collapsed", index=options.index(st.session_state.filter))
    st.session_state.filter = selected
    
    shown = cards if selected == "All" else [c for c in cards if c.get("difficulty") == selected]
    cols = st.columns(3)
    for i, card in enumerate(shown):
        with cols[i % 3]:
            st.markdown(f'<div class="deck-card"><div class="deck-label">QUESTION · {html.escape(card.get("difficulty","MEDIUM").upper())}</div><div class="deck-question">{html.escape(card["question"])}</div><div class="deck-answer">{html.escape(card["answer"])}</div><div class="deck-footer">{html.escape(card.get("category","General"))} · {html.escape(card.get("tag","Topic"))}</div></div>', unsafe_allow_html=True)
    with cols[len(shown) % 3]:
        if st.button("＋  Create New Card", key="create", use_container_width=True):
            switch("Generator")
            st.rerun()


def generator_view():
    st.markdown('<div class="eyebrow">Create with AI</div><h1>Flashcard generator</h1><div class="page-subtitle">Turn notes, vocabulary, or a study guide into a polished deck.</div>', unsafe_allow_html=True)
    form, preview = st.columns([1.15, .85], gap="large")
    with form:
        with st.container(border=True):
            notes = st.text_area("Study material", height=230, placeholder="Paste your notes, vocabulary list, or lesson content here…")
            count = st.slider("Number of cards", 3, 100, 12)
            st.caption("Gemini returns structured questions, answers, categories, tags, and difficulty levels.")
            if st.button("✦  Generate flashcards", type="primary", use_container_width=True):
                generate(notes, count)
    with preview:
        st.markdown('<div class="deck-card" style="min-height:255px"><div class="deck-label">HOW IT WORKS</div><div class="deck-question">Meaningful cards, ready to review.</div><div class="deck-answer">The generator finds key ideas, creates clear recall prompts, and adds useful organization metadata to every card.</div><div class="badges" style="margin-top:1.4rem"><span class="badge">Gemini 2.5 Flash</span><span class="badge">JSON output</span></div></div>', unsafe_allow_html=True)


def import_view():
    st.markdown('<div class="eyebrow">Load saved deck</div><h1>Import Flashcards</h1><div class="page-subtitle">Upload a previously exported JSON deck file to restore your cards.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        uploaded_file = st.file_uploader("Choose JSON deck file", type=["json"])
        if uploaded_file is not None:
            try:
                loaded_cards = json.load(uploaded_file)
                if isinstance(loaded_cards, list) and len(loaded_cards) > 0 and "question" in loaded_cards[0]:
                    if st.button("📥 Load into Collection", type="primary", use_container_width=True):
                        st.session_state.flashcards = loaded_cards
                        save_persisted_deck(loaded_cards)
                        st.session_state.card_idx = 0
                        st.session_state.show_answer = False
                        switch("Collection")
                        st.rerun()
                else:
                    st.error("Invalid file format. Please upload a JSON file exported from this app.")
            except Exception as e:
                st.error(f"Error reading JSON: {e}")


def generate(notes, count):
    if not notes.strip():
        return st.warning("Add some study material before generating cards.")
    key = get_api_key()
    if not key:
        return st.error("GEMINI_API_KEY is missing. Add it to your local .env file or Streamlit Cloud Secrets, then try again.")
    
    prompt = f"""
    You are an expert tutor creating study flashcards.
    Extract key terms or questions and generate exactly {count} distinct flashcards from the provided content.
    If the content contains vocabulary/terms (like Chinese words), put the term/word in 'question', and put the full translation, pinyin, and meaning in 'answer'.
    
    Content:
    {notes}
    """
    
    try:
        with st.spinner("Gemini is building your deck…"):
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FlashcardDeck,
                    max_output_tokens=65536
                )
            )
            data = json.loads(response.text)
            raw = data.get("cards", [])
            
        cards = [
            {
                "id": i + 1,
                "question": c.get("question", ""),
                "answer": c.get("answer", ""),
                "category": c.get("category", "Language"),
                "tag": c.get("tag", "Vocab"),
                "difficulty": str(c.get("difficulty", "Medium")).title()
            }
            for i, c in enumerate(raw) if c.get("question") and c.get("answer")
        ]
        
        if not cards:
            return st.error("Gemini returned no usable cards. Try adding more detailed text.")
            
        st.session_state.flashcards = cards
        save_persisted_deck(cards)  # บันทึกไฟล์ทันทีหลังเจนเสร็จ
        st.session_state.card_idx = 0
        st.session_state.show_answer = False
        switch("Collection")
        st.rerun()
    except Exception as error:
        st.error(f"Could not generate flashcards: {error}")


def empty(title, text):
    st.markdown(f'<div class="empty-state"><h3>{html.escape(title)}</h3><div>{html.escape(text)}</div></div>', unsafe_allow_html=True)


css()
init_state()
sidebar()
topbar()
{"Study Mode": study_view, "Generator": generator_view, "Collection": collection_view, "Import": import_view}[st.session_state.view]()