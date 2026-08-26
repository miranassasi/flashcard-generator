import streamlit as st
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# โหลด API Key จากไฟล์ .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI Flashcard Generator", page_icon="🗂️", layout="centered")

st.title("🗂️ AI Flashcard Generator")
st.write("แปลงสรุปบทเรียนหรือเลกเชอร์เป็น Flashcard สำหรับทบทวน")

# เช็คว่ามี API Key หรือยัง
if not api_key:
    st.error("ไม่พบ GEMINI_API_KEY กรุณาใส่คีย์ในไฟล์ .env ก่อนใช้งาน")
    st.stop()

client = genai.Client(api_key=api_key)

# ช่องรับข้อความจากผู้ใช้
notes_input = st.text_area(
    "เนื้อหาที่ต้องการทบทวน:",
    height=180,
    placeholder="วางข้อความ สรุป หรือบทความที่นี่..."
)

# แถบเลื่อนเลือกจำนวนการ์ด
num_cards = st.slider("จำนวน Flashcard ที่ต้องการสร้าง:", min_value=3, max_value=10, value=5)

# ตัวแปรเก็บประวัติการ์ด ไม่ให้หายเวลากดคลิกหน้าเว็บ
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

# ปุ่มกดสร้างการ์ด
if st.button("✨ สร้าง Flashcard", type="primary"):
    if not notes_input.strip():
        st.warning("กรุณาใส่เนื้อหาก่อนกดสร้าง")
    else:
        with st.spinner("AI กำลังวิเคราะห์และสร้าง Flashcard..."):
            prompt = f"จงสร้าง Flashcard จำนวน {num_cards} ข้อ จากเนื้อหานี้:\n{notes_input}"
            
            # สั่งให้โมเดลตอบกลับเป็น JSON Schema เท่านั้น
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "id": {"type": "INTEGER"},
                                "question": {"type": "STRING"},
                                "answer": {"type": "STRING"}
                            },
                            "required": ["id", "question", "answer"]
                        }
                    }
                ),
            )
            
            try:
                st.session_state.flashcards = json.loads(response.text)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการอ่านข้อมูล JSON: {e}")

# แสดงผล Flashcard ออกมาบนหน้าจอ
if st.session_state.flashcards:
    st.divider()
    st.subheader(f"📋 รายการ Flashcard ({len(st.session_state.flashcards)} ข้อ)")
    for card in st.session_state.flashcards:
        with st.expander(f"📌 ข้อที่ {card['id']}: {card['question']}"):
            st.success(f"เฉลย:")