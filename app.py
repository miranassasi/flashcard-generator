import streamlit as st
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Flashcard Generator", page_icon="🗂️", layout="centered")

st.title("🗂️ AI Flashcard Generator")
st.write("แปลงสรุปบทเรียน คำศัพท์ หรือเลกเชอร์เป็น Flashcard สำหรับทบทวนความรู้")

if not api_key:
    st.error("ไม่พบ GEMINI_API_KEY กรุณาตรวจสอบการตั้งค่าในไฟล์ .env")
    st.stop()

client = genai.Client(api_key=api_key)

notes_input = st.text_area(
    "เนื้อหาที่ต้องการสร้าง Flashcard:",
    height=250,
    placeholder="วางข้อความ สรุปบทเรียน หรือชุดคำศัพท์ที่นี่..."
)

# ขยายแถบเลือกเป็นสูงสุด 100 ข้อ
num_cards = st.slider("จำนวน Flashcard ที่ต้องการสร้าง:", min_value=3, max_value=100, value=10)

if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

if st.button("✨ สร้าง Flashcard", type="primary"):
    if not notes_input.strip():
        st.warning("กรุณากรอกเนื้อหาก่อนกดสร้าง")
    else:
        with st.spinner(f"AI กำลังวิเคราะห์เนื้อหาและสร้าง Flashcard {num_cards} ข้อ (อาจใช้เวลาสักครู่)..."):
            prompt = f"""
            คุณคือผู้ช่วยสร้าง Flashcard อัจฉริยะสำหรับการทบทวนบทเรียนและท่องจำ
            จงอ่านเนื้อหาต่อไปนี้ แล้วสร้าง Flashcard จำนวน {num_cards} ข้อ
            
            ข้อกำหนดในการสร้าง:
            - question: ประเด็นคำถาม, คอนเซ็ปต์สำคัญ หรือคำศัพท์หลัก
            - answer: คำตอบ, คำอธิบายอย่างละเอียด, คำแปล หรือพินอิน (ห้ามเว้นว่างเด็ดขาด)
            
            เนื้อหาต้นฉบับ:
            {notes_input}
            """
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        max_output_tokens=32768,  # ขยาย Token ขาออกรองรับข้อมูลปริมาณมาก
                        response_schema={
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "id": {"type": "INTEGER"},
                                    "question": {"type": "STRING", "description": "คำถามหรือคำศัพท์หลัก"},
                                    "answer": {"type": "STRING", "description": "เฉลย คำแปล หรือคำอธิบายแบบสมบูรณ์"}
                                },
                                "required": ["id", "question", "answer"]
                            }
                        }
                    ),
                )
                
                st.session_state.flashcards = json.loads(response.text)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผลข้อมูล: {e}")

if st.session_state.flashcards:
    st.divider()
    st.subheader(f"📋 รายการ Flashcard ทั้งหมด ({len(st.session_state.flashcards)} ข้อ)")
    
    for card in st.session_state.flashcards:
        with st.expander(f"📌 ข้อที่ {card['id']}: {card['question']}"):
            st.success(f"**เฉลย / คำอธิบาย:**\n\n{card['answer']}")