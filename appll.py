import streamlit as st
import pandas as pd
import os

# ملف الحفظ الدائم على جهازك
DATA_FILE = "data_storage.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE).to_dict('records')
    return []

def save_data(data):
    df = pd.DataFrame(data)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# إعداد الصفحة
st.set_page_config(page_title="نظام أرشفة إبراهيم الاحترافي", layout="wide")

# كود لتعديل الاتجاه لليمين RTL ليناسب العربية والعبرية
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-testid="stExpander"] div { text-align: right; direction: rtl; }
    th, td { text-align: right !important; }
    .stSelectbox label, .stTextInput label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗄️ نظام تنظيم ملفات الوالد")

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- قسم إضافة ملف جديد ---
with st.expander("➕ إضافة ملف جديد للنظام", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("שם מלא (الاسم الكامل بالعبرية)")
        size = st.selectbox("גודל (الحجم)", ["גדול", "بيנוני", "קטן"])
    with col2:
        # قائمة الألوان باللغة العربية كما طلبت
        color_options = [
            "أسود", "أبيض", "رمادي", "أحمر", "بوردو", 
            "أزرق", "أزرق سماوي", "أصفر", "ليلكي", "أخضر", "برتقالي"
        ]
        color = st.selectbox("اللون", color_options)
        closet = st.text_input("مكان الملف (الخزانة)")
    
    if st.button("حفظ الملف في القاعدة"):
        if full_name:
            new_entry = {
                "שם מלא": full_name,
                "الحجم": size,
                "اللون": color,
                "المكان": closet
            }
            st.session_state.data.append(new_entry)
            save_data(st.session_state.data)
            st.success(f"تم حفظ ملف {full_name} بنجاح!")
            st.balloons()
        else:
            st.error("الرجاء إدخال الاسم أولاً!")

# --- البحث والجدول المرتب ---
if st.session_state.data:
    st.divider()
    st.subheader("🔍 البحث في الملفات المرتبة (حسب الحجم ثم الأبجدية)")
    
    search_query = st.text_input("ابحث عن اسم هنا...")

    df = pd.DataFrame(st.session_state.data)
    
    # 1. الترتيب حسب الحجم (كبير، متوسط، صغير)
    df['الحجم'] = pd.Categorical(df['الحجم'], categories=["גדול", "بيנוني", "קטן"], ordered=True)
    
    # 2. الترتيب داخل كل حجم حسب الاسم أبجدياً (א-ת)
    df_sorted = df.sort_values(by=["الحجم", "שם מלא"]).reset_index(drop=True)

    # 3. تصفية البحث إذا كتب المستخدم شيئاً
    if search_query:
        df_display = df_sorted[df_sorted['שם מלא'].str.contains(search_query, case=False, na=False)]
    else:
        df_display = df_sorted

    if not df_display.empty:
        # عرض الجدول بشكل أنيق
        st.table(df_display)
    else:
        st.warning("لم يتم العثور على نتائج تطابق هذا الاسم.")

    # خيار مسح البيانات
    if st.button("تفريغ النظام نهائياً"):
        st.session_state.data = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()
else:
    st.info("النظام فارغ حالياً، ابدأ بإضافة الملفات من الأعلى.")