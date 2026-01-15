import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ফাইলের নামসমূহ
ORDER_FILE = 'dokan_hishab.csv'
USER_FILE = 'customers.csv'

# পেজ সেটআপ
st.set_page_config(page_title="আমার ডিজিটাল দোকান", layout="centered")

# ফাইলগুলো না থাকলে তৈরি করা
if not os.path.exists(ORDER_FILE):
    pd.DataFrame(columns=['তারিখ', 'ক্রেতার নাম', 'পণ্য', 'পরিমাণ', 'মোট টাকা (₹)', 'পেমেন্ট মাধ্যম', 'স্ট্যাটাস']).to_csv(ORDER_FILE, index=False)
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=['নাম', 'মোবাইল নম্বর', 'পাসওয়ার্ড']).to_csv(USER_FILE, index=False)

# লগইন স্টেট চেক করা (সেশন হ্যান্ডলিং)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# --- ১. লগইন ও রেজিস্ট্রেশন পেজ (যদি লগইন না থাকে) ---
if not st.session_state['logged_in']:
    st.title("🔐 ডিজিটাল দোকানে স্বাগতম")
    tab1, tab2 = st.tabs(["লগইন করুন", "নতুন রেজিস্ট্রেশন"])

    with tab1:
        st.subheader("লগইন")
        login_phone = st.text_input("মোবাইল নম্বর", key="l_phone")
        login_pass = st.text_input("পাসওয়ার্ড", type="password", key="l_pass")
        if st.button("ভেতরে প্রবেশ করুন"):
            user_df = pd.read_csv(USER_FILE)
            user = user_df[(user_df['মোবাইল নম্বর'].astype(str) == login_phone) & (user_df['পাসওয়ার্ড'].astype(str) == login_pass)]
            if not user.empty:
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = user['নাম'].values[0]
                st.rerun() # পেজ রিফ্রেশ করে অ্যাপে ঢুকবে
            else:
                st.error("ভুল নম্বর বা পাসওয়ার্ড! আবার চেষ্টা করুন।")

    with tab2:
        st.subheader("নতুন কাস্টমার ফর্ম")
        reg_name = st.text_input("আপনার নাম")
        reg_phone = st.text_input("মোবাইল নম্বর (এটিই আপনার আইডি)")
        reg_pass = st.text_input("একটি পাসওয়ার্ড দিন", type="password")
        
        if st.button("রেজিস্ট্রেশন সম্পন্ন করুন"):
            if reg_name and reg_phone and reg_pass:
                user_df = pd.read_csv(USER_FILE)
                if reg_phone in user_df['মোবাইল নম্বর'].astype(str).values:
                    st.warning("এই নম্বর দিয়ে আগে থেকেই রেজিস্ট্রেশন করা আছে।")
                else:
                    new_user = pd.DataFrame([[reg_name, reg_phone, reg_pass]], columns=['নাম', 'মোবাইল নম্বর', 'পাসওয়ার্ড'])
                    new_user.to_csv(USER_FILE, mode='a', header=False, index=False)
                    st.success("রেজিস্ট্রেশন সফল! এখন লগইন ট্যাবে গিয়ে লগইন করুন।")
            else:
                st.error("সবগুলো ঘর পূরণ করুন।")

# --- ২. মেইন অ্যাপ (লগইন করার পর যা আসবে) ---
else:
    st.sidebar.title(f"স্বাগতম, {st.session_state['user_name']}!")
    if st.sidebar.button("লগ আউট"):
        st.session_state['logged_in'] = False
        st.rerun()

    menu = ["🛒 কেনাকাটা (অর্ডার)", "📊 আমার আগের হিসাব"]
    choice = st.sidebar.selectbox("কি করতে চান?", menu)

    if choice == "🛒 কেনাকাটা (অর্ডার)":
        st.title("🛍️ পণ্য অর্ডার করুন")
        
        # পণ্যের তালিকা
        product_list = [
            "আটা (Atta)", "চিনি (Sugar)", "লবণ (Salt)", "সর্ষের তেল", "মুসুর ডাল",
            "নাসির বিড়ি", "আকিজ বিড়ি", "কেষ্ট বিড়ি", "৫১ নম্বর বিড়ি",
            "গোল্ড ফ্লেক (Gold Flake)", "উইলস (Wills)", "নেভি কাট", "ফ্ল্যাক", "ক্লাসিক", "মার্লবোরো"
        ]
        
        product = st.selectbox("পণ্য নির্বাচন করুন", product_list)
        amount = st.number_input("পরিমাণ (কেজি/পিস)", min_value=1.0, step=1.0)
        price = st.number_input("মোট দাম (₹ টাকা)", min_value=0)
        
        pay_method = st.selectbox("পেমেন্ট মাধ্যম", ["Google Pay", "PhonePe", "Paytm", "Cash"])
        paid = st.checkbox("আমি পেমেন্ট করেছি")

        if st.button("অর্ডার কনফার্ম করুন"):
            if price > 0:
                now = datetime.now().strftime("%d-%m-%Y %H:%M")
                status = "Paid" if paid else "Due"
                new_order = pd.DataFrame([[now, st.session_state['user_name'], product, amount, price, pay_method, status]], 
                                         columns=['তারিখ', 'ক্রেতার নাম', 'পণ্য', 'পরিমাণ', 'মোট টাকা (₹)', 'পেমেন্ট মাধ্যম', 'স্টাতাস'])
                new_order.to_csv(ORDER_FILE, mode='a', header=False, index=False)
                st.success("অর্ডার সফল হয়েছে!")
                st.balloons()

    elif choice == "📊 আমার আগের হিসাব":
        st.title("📋 আপনার কেনাকাটার ইতিহাস")
        order_df = pd.read_csv(ORDER_FILE)
        my_orders = order_df[order_df['ক্রেতার নাম'] == st.session_state['user_name']]
        
        if not my_orders.empty:
            st.dataframe(my_orders, use_container_width=True)
            total = my_orders['মোট টাকা (₹)'].sum()
            st.subheader(f"আপনার মোট কেনাকাটা: ₹ {total}")
        else:
            st.info("আপনার কোনো অর্ডার ইতিহাস নেই।")

    # পেমেন্ট তথ্য সাইডবারে
    st.sidebar.divider()
    st.sidebar.markdown("### ⚡ পেমেন্ট UPI")
    st.sidebar.write("UPI: *yourname@okaxis*")
