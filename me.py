import streamlit as st
import pandas as pd
import os

# ফাইলের নাম
PRODUCTS_FILE = 'products.xlsx'

def load_data():
    if os.path.exists(PRODUCTS_FILE):
        try:
            df = pd.read_excel(PRODUCTS_FILE)
            # কলামের নামগুলো পরিষ্কার করা (Error ফিক্স করার জন্য)
            df.columns = [c.strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame(columns=['Category', 'Product Name', 'Price', 'Unit'])
    return pd.DataFrame(columns=['Category', 'Product Name', 'Price', 'Unit'])

def save_data(df):
    df.to_excel(PRODUCTS_FILE, index=False)

st.set_page_config(page_title="আমার দোকান", layout="wide")

# সাইডবার মেনু
menu = ["বাজার করুন", "অ্যাডমিন প্যানেল"]
choice = st.sidebar.selectbox("মেনু", menu)

if choice == "বাজার করুন":
    st.title("🛍️ আমাদের পণ্যের তালিকা")
    df = load_data()
    
    if df.empty:
        st.info("তালিকায় কোনো পণ্য নেই। অ্যাডমিন প্যানেল থেকে যোগ করুন।")
    else:
        for index, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                # .get ব্যবহার করা হয়েছে যাতে নাম না মিললেও অ্যাপ বন্ধ না হয় (Error Handling)
                name = row.get('Product Name', 'Unknown')
                price = row.get('Price', 0)
                cat = row.get('Category', 'N/A')
                
                col1.write(f"*{name}* ({cat})")
                col2.write(f"দাম: {price} টাকা")
                if col3.button("যোগ করুন", key=f"add_{index}"):
                    st.toast(f"{name} যোগ হয়েছে")

elif choice == "অ্যাডমিন প্যানেল":
    st.title("⚙️ অ্যাডমিন কন্ট্রোল")
    
    # ট্যাব সুবিধা (আপনার আগের স্টাইল অনুযায়ী)
    tab1, tab2 = st.tabs(["অর্ডার ম্যানেজমেন্ট", "পণ্য ম্যানেজমেন্ট"])
    
    with tab1:
        st.subheader("📦 কাস্টমার অর্ডার")
        st.write("এখনো কোনো নতুন অর্ডার আসেনি।")

    with tab2:
        st.subheader("➕ নতুন পণ্য যোগ করুন")
        df = load_data()
        
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("পণ্যের নাম")
            cat = st.selectbox("ক্যাটাগরি", ["মুদিখানা", "সবজি", "ফল", "অন্যান্য"])
            price = st.number_input("দাম", min_value=0)
            unit = st.text_input("ইউনিট (যেমন: ১ কেজি)")
            
            if st.form_submit_button("তালিকায় যোগ করুন"):
                if name:
                    new_row = pd.DataFrame([{'Category': cat, 'Product Name': name, 'Price': price, 'Unit': unit}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"{name} যোগ করা হয়েছে!")
                    st.rerun()

        st.divider()
        st.subheader("🗑️ পণ্য মুছুন")
        for i, row in df.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(f"{row.get('Product Name')} - {row.get('Price')} টাকা")
            if c2.button("মুছুন", key=f"del_{i}"):
                df = df.drop(i)
                save_data(df)
                st.rerun()
