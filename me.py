import streamlit as st
import pandas as pd
import os

# ফাইলের নামসমূহ
PRODUCTS_FILE = 'products.xlsx'

# ডাটা লোড করার ফাংশন
def load_data():
    if os.path.exists(PRODUCTS_FILE):
        try:
            df = pd.read_excel(PRODUCTS_FILE)
            # কলামের নামগুলো নিশ্চিত করা
            if df.empty:
                df = pd.DataFrame(columns=['Category', 'Product Name', 'Price', 'Unit'])
        except:
            df = pd.DataFrame(columns=['Category', 'Product Name', 'Price', 'Unit'])
    else:
        df = pd.DataFrame(columns=['Category', 'Product Name', 'Price', 'Unit'])
    return df

def save_data(df):
    df.to_excel(PRODUCTS_FILE, index=False)

# পেজ সেটআপ
st.set_page_config(page_title="আমার দোকান", layout="wide")

# সাইডবার মেনু
menu = ["বাজার করুন", "অ্যাডমিন প্যানেল"]
choice = st.sidebar.selectbox("মেনু", menu)

if choice == "বাজার করুন":
    st.title("🛍️ আমাদের পণ্যের তালিকা")
    df = load_data()
    
    if df.empty:
        st.info("বর্তমানে কোনো পণ্য তালিকায় নেই। অ্যাডমিন প্যানেল থেকে পণ্য যোগ করুন।")
    else:
        # পণ্যের তালিকা প্রদর্শন
        for index, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                # কলামের নাম সঠিকভাবে কল করা (১৭ নম্বর ছবির এরর ফিক্স)
                name = row.get('Product Name', 'অজানা পণ্য')
                price = row.get('Price', 0)
                cat = row.get('Category', 'সাধারণ')
                
                col1.write(f"*{name}*")
                col1.caption(f"ক্যাটাগরি: {cat}")
                col2.write(f"দাম: {price} টাকা")
                if col3.button("যোগ করুন", key=f"btn_{index}"):
                    st.toast(f"{name} ব্যাগে যোগ হয়েছে!")

elif choice == "অ্যাডমিন প্যানেল":
    st.title("⚙️ অ্যাডমিন প্যানেল")
    
    tab1, tab2 = st.tabs(["অর্ডার চেক", "পণ্য ম্যানেজমেন্ট"])
    
    with tab2:
        st.subheader("➕ নতুন পণ্য যোগ করুন")
        df = load_data()
        
        with st.form("product_form", clear_on_submit=True):
            p_name = st.text_input("পণ্যের নাম")
            p_cat = st.selectbox("ক্যাটাগরি", ["মুদিখানা", "সবজি", "ফল", "অন্যান্য"])
            p_price = st.number_input("দাম (টাকা)", min_value=1)
            p_unit = st.text_input("ইউনিট (যেমন: ১ কেজি)")
            
            submit = st.form_submit_button("তালিকায় যোগ করুন")
            
            if submit:
                if p_name:
                    new_data = pd.DataFrame([[p_cat, p_name, p_price, p_unit]], 
                                            columns=['Category', 'Product Name', 'Price', 'Unit'])
                    df = pd.concat([df, new_data], ignore_index=True)
                    save_data(df)
                    st.success(f"সফলভাবে '{p_name}' যোগ করা হয়েছে!")
                    st.rerun()
                else:
                    st.error("দয়া করে পণ্যের নাম লিখুন।")

        st.divider()
        st.subheader("🗑️ পণ্য মুছুন")
        if not df.empty:
            for i, row in df.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"{row['Product Name']} ({row['Price']} টাকা)")
                if c2.button("মুছুন", key=f"del_{i}"):
                    df = df.drop(i)
                    save_data(df)
                    st.rerun()
