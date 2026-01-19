import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# ফাইলের নামসমূহ
PRODUCTS_FILE = 'products.xlsx'
ORDERS_FILE = 'orders.csv'
USERS_FILE = 'users.csv'

# ডাটা লোড করার ফাংশন
def load_data():
    if os.path.exists(PRODUCTS_FILE):
        df = pd.read_excel(PRODUCTS_FILE)
    else:
        df = pd.DataFrame(columns=['Category', 'Product Name', 'Price', 'Unit'])
    return df

def save_products(df):
    df.to_excel(PRODUCTS_FILE, index=False)

# পেজ সেটআপ (আপনার আগের ডিজাইনের মতো)
st.set_page_config(page_title="আমার দোকান", layout="wide")

# সাইডবার মেনু
menu = ["বাজার করুন", "অর্ডার ট্র্যাকিং", "অ্যাডমিন প্যানেল"]
choice = st.sidebar.selectbox("মেনু", menu)

if choice == "বাজার করুন":
    st.header("🛍️ আমাদের পণ্যের তালিকা")
    products = load_data()
    if products.empty:
        st.info("দুঃখিত, বর্তমানে কোনো পণ্য নেই।")
    else:
        # এখানে আপনার আগের শপিং কোড থাকবে
        for index, row in products.iterrows():
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"*{row['Product Name']}* ({row['Category']})")
            col2.write(f"দাম: {row['Price']} টাকা")
            if col3.button(f"যোগ করুন", key=f"add_{index}"):
                st.success(f"{row['Product Name']} যোগ করা হয়েছে!")

elif choice == "অ্যাডমিন প্যানেল":
    st.header("⚙️ অ্যাডমিন ম্যানেজমেন্ট")
    
    # অ্যাডমিন ট্যাব
    tab1, tab2 = st.tabs(["অর্ডার ম্যানেজমেন্ট", "পণ্য ম্যানেজমেন্ট"])
    
    with tab1:
        st.subheader("📦 নতুন অর্ডার সমূহ")
        # এখানে অর্ডারের লিস্ট দেখাবে
        st.write("বর্তমানে কোনো নতুন অর্ডার নেই।")

    with tab2:
        st.subheader("🍎 নতুন পণ্য যোগ করুন")
        products = load_data()
        
        with st.form("add_product_form"):
            new_cat = st.text_input("ক্যাটাগরি (যেমন: মুদিখানা)")
            new_name = st.text_input("পণ্যের নাম")
            new_price = st.number_input("দাম (টাকা)", min_value=1)
            new_unit = st.text_input("ইউনিট (যেমন: ১ কেজি / ১ পিস)")
            submit = st.form_submit_button("পণ্যটি তালিকায় যোগ করুন")
            
            if submit:
                if new_name and new_cat:
                    new_row = {'Category': new_cat, 'Product Name': new_name, 'Price': new_price, 'Unit': new_unit}
                    products = pd.concat([products, pd.DataFrame([new_row])], ignore_index=True)
                    save_products(products)
                    st.success(f"সফলভাবে '{new_name}' যোগ করা হয়েছে!")
                    st.info("দ্রষ্টব্য: অনলাইনে সেভ করার জন্য আপনার GitHub-এ ফাইলটি আপডেট হওয়া প্রয়োজন।")
                else:
                    st.error("দয়া করে নাম এবং ক্যাটাগরি লিখুন।")

        st.divider()
        st.subheader("📋 বর্তমান পণ্য তালিকা ও ডিলিট অপশন")
        if not products.empty:
            for idx, row in products.iterrows():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"{row['Product Name']} - {row['Price']} টাকা")
                if c2.button("মুছে ফেলুন", key=f"del_{idx}"):
                    products = products.drop(idx)
                    save_products(products)
                    st.warning("পণ্যটি মুছে ফেলা হয়েছে। পেজটি রিফ্রেশ করুন।")
                    st.rerun()
