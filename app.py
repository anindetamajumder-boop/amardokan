import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ফাইলের নামসমূহ
ORDER_FILE = 'dokan_hishab.csv'
USER_FILE = 'customers.csv'

# ফাইল তৈরি করার ফাংশন (এরর এড়াতে)
def initialize_files():
    if not os.path.exists(ORDER_FILE):
        pd.DataFrame(columns=['তারিখ', 'ক্রেতার নাম', 'পণ্য', 'পরিমাণ', 'মোট টাকা (₹)', 'পেমেন্ট মাধ্যম', 'স্ট্যাটাস']).to_csv(ORDER_FILE, index=False)
    if not os.path.exists(USER_FILE):
        pd.DataFrame(columns=['নাম', 'মোবাইল_নম্বর', 'পাসওয়ার্ড']).to_csv(USER_FILE, index=False)

initialize_files()

# সেশন স্টেট
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- লগইন ও রেজিস্ট্রেশন ---
if not st.session_state['logged_in']:
    st.title("🔐 ডিজিটাল দোকানে স্বাগতম")
    tab1, tab2 = st.tabs(["লগইন", "নতুন রেজিস্ট্রেশন"])

    with tab1:
        l_phone = st.text_input("মোবাইল নম্বর")
        l_pass = st.text_input("পাসওয়ার্ড", type="password")
        if st.button("লগইন"):
            user_df = pd.read_csv(USER_FILE)
            # মোবাইল নম্বর কলাম চেক করা
            user = user_df[(user_df['মোবাইল_নম্বর'].astype(str) == l_phone) & (user_df['পাসওয়ার্ড'].astype(str) == l_pass)]
            if not user.empty:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = user['নাম'].values[0]
                st.rerun()
            else:
                st.error("ভুল নম্বর বা পাসওয়ার্ড!")

    with tab2:
        r_name = st.text_input("আপনার নাম")
        r_phone = st.text_input("মোবাইল নম্বর")
        r_pass = st.text_input("পাসওয়ার্ড সেট করুন", type="password")
        if st.button("রেজিস্ট্রেশন করুন"):
            if r_name and r_phone and r_pass:
                user_df = pd.read_csv(USER_FILE)
                if r_phone in user_df['মোবাইল_নম্বর'].astype(str).values:
                    st.warning("এই নম্বরটি আগেই আছে।")
                else:
                    new_user = pd.DataFrame([[r_name, r_phone, r_pass]], columns=['নাম', 'মোবাইল_নম্বর', 'পাসওয়ার্ড'])
                    new_user.to_csv(USER_FILE, mode='a', header=False, index=False)
                    st.success("রেজিস্ট্রেশন সফল! এখন লগইন করুন।")

# --- মেইন অ্যাপ ---
else:
    st.sidebar.write(f"ব্যবহারকারী: {st.session_state['user_name']}")
    if st.sidebar.button("ল
