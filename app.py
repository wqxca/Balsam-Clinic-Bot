import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

# 1. إعدادات الصفحة
st.set_page_config(page_title="عيادات بلسم الطبية", page_icon="🏥", layout="centered")

# 2. إخفاء شعارات وعلامات Streamlit المائية باستخدام CSS
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. إعداد الاتصال
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

system_prompt = """
أنت مساعد طبي ذكي ومباشر لـ 'عيادات بلسم الطبية'.
مهمتك توجيه المريض للعيادة المناسبة (باطنية، أسنان، جلدية، طب أسرة) بناءً على أعراضه.
قواعد صارمة:
1. ممنوع ديباجة التعاطف الطويلة.
2. وجه المريض للعيادة المناسبة فوراً.
3. اشرح سبب التوجيه بجملة واحدة.
4. اختم بتمني السلامة ولا تطرح أي سؤال إضافي إطلاقاً.
كن عملياً ومختصراً.
"""

MAX_ATTEMPTS = 10

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.messages.append({"role": "assistant", "content": "أهلاً بك في عيادات بلسم الطبية، اخبرني بما تشعر به اليوم لتوجيهك للعيادة المناسبة؟"})
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

# 4. القائمة الجانبية (Sidebar) لزر محادثة جديدة
with st.sidebar:
    st.title("⚙️ خيارات")
    if st.button("🗑️ بدء محادثة جديدة", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": system_prompt}]
        st.session_state.messages.append({"role": "assistant", "content": "أهلاً بك في عيادات بلسم الطبية، اخبرني بما تشعر به اليوم لتوجيهك للعيادة المناسبة؟"})
        st.session_state.attempts = 0
        st.rerun()

# 5. واجهة المحادثة الرئيسية
st.title("🏥 المساعد الذكي - عيادات بلسم")

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

if st.session_state.attempts >= MAX_ATTEMPTS:
    st.warning("انتهت جلستك الحالية لليوم. نتمنى لك الصحة والعافية!")
    st.stop()

user_input = st.chat_input("اكتبي أعراضك هنا...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.attempts += 1
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.5, 
        )
        
        bot_reply = completion.choices[0].message.content
        with st.chat_message("assistant"):
            st.write(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()
        
    except Exception as e:
        st.error(f"⚠️ عذراً، حصل خطأ تقني: {e}")
        st.session_state.attempts -= 1