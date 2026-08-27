# ✦ FlashCard — AI-Powered Active Recall Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google GenAI SDK](https://img.shields.io/badge/Gemini%202.5%20Flash-Structured%20JSON-FFD043.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**FlashCard** คือเว็บแอปพลิเคชันสำหรับการทบทวนบทเรียนและท่องจำคำศัพท์ด้วยหลักการ **Active Recall** โดยแปลงเนื้อหาดิบ (Lecture Notes, คำศัพท์ภาษาจีน/อังกฤษ, สรุปบทเรียน) ให้กลายเป็นสำรับ Flashcard แบบมีโครงสร้าง พร้อมจัดหมวดหมู่และแบ่งระดับความยากอัตโนมัติด้วย **Gemini 2.5 Flash**

---

## 🧠 Learning Science Behind FlashCard

ระบบนี้พัฒนาขึ้นโดยอิงตามหลักการทำงานของสมองและการจดจำระยะยาว:

1. **Active Recall (การดึงความจำเชิงรุก):** 
   แทนที่จะอ่านทบทวนแบบผ่านตา (Passive Review) หน้าต่าง **Study Mode** จะบังคับให้สมองนึกคำตอบจากคำถามก่อนคลิกพลิกการ์ด การออกแรงค้นหาข้อมูลจากความทรงจำช่วยกระชับเส้นใยประสาท (Synapses) ทำให้จำได้แม่นยำยิ่งขึ้น
2. **Combating the Forgetting Curve:** 
   มนุษย์ลืมข้อมูลใหม่ได้มากกว่า 50–70% ใน 24 ชั่วโมงแรก การมีระบบ **Collection & Filter** ช่วยให้เลือกทบทวนเฉพาะข้อที่ยาก (`Hard`) ก่อนที่สมองจะลืมสนิท
3. **Randomized Reinforcement (Shuffle):** 
   ฟังก์ชันสับการ์ดช่วยป้องกันไม่ให้สมองจำแบบจำตำแหน่งหรือจำตามลำดับข้อ

---

## ✨ Key Features

- **⚡ Instant AI Deck Generation:** แปลงเนื้อหายาวๆ เป็น Flashcard ได้สูงสุด 100 ข้อต่อครั้ง พร้อมกำกับ Metadata (`Category`, `Tag`, `Difficulty`) ด้วย JSON Mode
- **🎯 Focused Study Mode:** โหมดฝึกท่องจำแบบโฟกัสทีละใบ พร้อมแอนิเมชันพลิกการ์ด (Flip Reveal) และ Progress Bar ติดตามความคืบหน้า
- **▦ Collection & Filter:** หน้ารวมคลังการ์ดทั้งหมด รองรับการสับการ์ด (`Shuffle`) และฟิลเตอร์กรองตามระดับความยาก (`Easy`, `Medium`, `Hard`)
- **💾 Auto Persistence & Import/Export:** บันทึกชุดการ์ดลงเครื่องอัตโนมัติ (`saved_deck.json`) ปิดเว็บแล้วเปิดใหม่ข้อมูลไม่หาย พร้อมปุ่ม Export และ Import ไฟล์ JSON
- **🎨 High-Contrast Obsidian UI:** ธีม Dark Charcoal ตัดด้วยสีเหลือง Neon Gold คมชัด สบายตาตามสไตล์ Modern SaaS

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend & UI** | Streamlit | เว็บเฟรมเวิร์ก Python พร้อม Custom CSS (DM Sans & Plus Jakarta Sans) |
| **AI Model & SDK** | Gemini 2.5 Flash | เรียกใช้งานผ่าน Official `google-genai` SDK |
| **Data Validation** | Pydantic v2 | กำหนด Strict Schema ควบคุม Structured JSON Output จากโมเดล |
| **Data Storage** | Local JSON Store | บันทึกและดึงสถานะการเรียนรู้อัตโนมัติ (`saved_deck.json`) |

---

## 🚀 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/miranassasi/flashcard-generator.git](https://github.com/miranassasi/flashcard-generator.git)
cd flashcard-generator

## How to use

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
