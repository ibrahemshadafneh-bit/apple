import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام أرشفة إبراهيم الاحترافي", layout="wide")

# 2. تصميم الواجهة (RTL)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    div[data-testid="stExpander"] div { text-align: right; direction: rtl; }
    th, td { text-align: right !important; }
    .stSelectbox label, .stTextInput label { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗄️ نظام تنظيم ملفات الوالد")

# 3. إعداد الاتصال بـ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # محاولة قراءة البيانات، إذا فشل بنرجع جدول فاضي بالعناوين المطلوبة
    try:
        data = conn.read(worksheet="Sheet1", ttl="0s")
        if data is None or data.empty:
            return pd.DataFrame(columns=["Name", "Size", "Color", "Location"])
        return data
    except:
        return pd.DataFrame(columns=["Name", "Size", "Color", "Location"])

# تحميل البيانات الحالية
df_existing = get_data()

# --- قسم إضافة ملف جديد ---
with st.expander("➕ إضافة ملف جديد للنظام", expanded=True):
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("שם מלא (الاسم الكامل بالعبرية)")
            size = st.selectbox("גودل (الحجم)", ["גדול", "בינוני", "קטן"])
        with col2:
            color_options = ["أسود", "أبيض", "رمادي", "أحمر", "بوردو", "أزرق", "أزرق سماوي", "أصفر", "ليلكي", "أخضر", "برتقالي"]
            color = st.selectbox("اللون", color_options)
            closet = st.text_input("مكان الملف (الخزانة)")
        
        submit = st.form_submit_button("حفظ الملف في القاعدة")

        if submit:
            if full_name:
                # فحص التكرار (فقط إذا الجدول مش فاضي)
                is_duplicate = False
                if not df_existing.empty and "Name" in df_existing.columns:
                    if full_name in df_existing['Name'].values:
                        is_duplicate = True

                if is_duplicate:
                    st.error(f"الاسم '{full_name}' مسجل مسبقاً!")
                else:
                    new_entry = pd.DataFrame([{
                        "Name": full_name,
                        "Size": size,
                        "Color": color,
                        "Location": closet
                    }])
                    # دمج البيانات الجديدة مع القديمة
                    updated_df = pd.concat([df_existing, new_entry], ignore_index=True)
                    # رفع التحديث لجوجل شيت
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.success(f"تم حفظ {full_name} بنجاح!")
                    st.balloons()
                    st.rerun()
            else:
                st.error("الرجاء إدخال الاسم!")

# --- عرض البيانات والبحث ---
st.divider()
st.subheader("🔍 استعراض وبحث في الملفات")

if not df_existing.empty and "Name" in df_existing.columns:
    search_query = st.text_input("ابحث عن اسم هنا...")
    
    # تحويل الحجم لفئة مرتبة عشان يظهر الكبير فوق
    df_existing['Size'] = pd.Categorical(df_existing['Size'], categories=["גדול", "בינוני", "קטن"], ordered=True)
    df_display = df_existing.sort_values(by=["Size", "Name"])

    if search_query:
        df_display = df_display[df_display['Name'].astype(str).str.contains(search_query, case=False, na=False)]

    st.table(df_display)

    # --- قسم الحذف ---
    st.divider()
    st.subheader("🗑️ إزالة ملف من النظام")
    person_to_delete = st.selectbox("اختر الاسم المراد حذفه:", df_display['Name'].tolist())
    
    if st.button("تأكيد الحذف", type="primary"):
        updated_df = df_existing[df_existing['Name'] != person_to_delete]
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success(f"تم حذف {person_to_delete} من النظام.")
        st.rerun()
else:
    st.info("النظام فارغ حالياً، ابدأ بإضافة الملفات من الأعلى.")