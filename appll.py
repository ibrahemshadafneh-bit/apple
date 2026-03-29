import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. إعداد الصفحة والواجهة بالعربي
st.set_page_config(page_title="نظام أرشفة إبراهيم", layout="wide")

st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    th, td { text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗄️ نظام تنظيم ملفات الوالد")

# 2. الربط مع Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(worksheet="Sheet1")

try:
    df_existing = get_data()
except:
    df_existing = pd.DataFrame(columns=["Name", "Size", "Color", "Location"])

# 3. قسم الإضافة
with st.expander("➕ إضافة ملف جديد", expanded=True):
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("الاسم الكامل (עברית/عربي)")
            size = st.selectbox("الحجم", ["גדול", "בינוني", "קטן"])
        with col2:
            color = st.selectbox("اللون", ["أسود", "أبيض", "رمادي", "أحمر", "أزرق", "أخضر"])
            closet = st.text_input("المكان (الخزانة)")
        
        if st.form_submit_button("حفظ"):
            if full_name:
                new_entry = pd.DataFrame([{"Name": full_name, "Size": size, "Color": color, "Location": closet}])
                updated_df = pd.concat([df_existing, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success(f"تم حفظ {full_name}!")
                st.rerun()

# 4. عرض البيانات والحذف
st.divider()
if not df_existing.empty:
    search = st.text_input("🔍 ابحث عن اسم...")
    df_show = df_existing[df_existing['Name'].str.contains(search, case=False)] if search else df_existing
    st.table(df_show)

    st.subheader("🗑️ حذف ملف")
    to_delete = st.selectbox("اختر الاسم لحذفه:", df_existing['Name'].tolist())
    if st.button("تأكيد الحذف", type="primary"):
        updated_df = df_existing[df_existing['Name'] != to_delete]
        conn.update(worksheet="Sheet1", data=updated_df)
        st.success("تم الحذف!")
        st.rerun()
else:
    st.info("لا توجد بيانات حالياً.")