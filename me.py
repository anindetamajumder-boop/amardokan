import streamlit as st
import pandas as pd
import os
from datetime import datetime

# লাইভ লোকেশনের জন্য এই লাইব্রেরিটি জরুরি। 
# যদি এরর দেখায়, টার্মিনালে লিখুন: pip install streamlit-js-eval
try:
    from streamlit_js_eval import get_geolocation
except ImportError:
    get_geolocation = None

# --- সেটিংস ও ডাটাবেস ---
SHOP_NAME = "Anindeta"
ADMIN_PASSWORD = "rajsona" 
USER_DB = 'users.csv'
ORDER_DB = 'orders.csv'
EXCEL_FILE = 'products.xlsx'
DUE_DB = 'customer_dues.csv'

# ডাটাবেস কলাম কনফিগারেশন
db_config = {
    USER_DB: ['Name', 'Phone', 'Password', 'Address', 'Pincode'], 
    ORDER_DB: ['Date', 'Customer', 'Phone', 'Items', 'Total', 'Status', 'Payment', 'Location', 'Pincode'], 
    DUE_DB: ['Phone', 'Total_Due']
}

# ফাইলগুলো তৈরি বা আপডেট করা (ফিক্সড)
for file, cols in db_config.items():
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    else:
        df_tmp = pd.read_csv(file)
        for col in cols:
            if col not in df_tmp.columns:
                df_tmp[col] = "N/A"
        df_tmp.to_csv(file, index=False)

if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=['Type', 'Name', 'Price']).to_excel(EXCEL_FILE, index=False)

st.set_page_config(page_title=SHOP_NAME, layout="wide")

# স্টেট ম্যানেজমেন্ট
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'cart' not in st.session_state: st.session_state['cart'] = []
if 'admin_unlocked' not in st.session_state: st.session_state['admin_unlocked'] = False

# --- ১. কাস্টমার লগইন ও রেজিস্ট্রেশন ---
if not st.session_state['logged_in']:
    st.markdown(f"<h1 style='text-align: center; color: #d32f2f;'>🛍️ {SHOP_NAME}</h1>", unsafe_allow_html=True)
    input_phone = st.text_input("আপনার ফোন নম্বর দিন", key="login_phone")
    
    if input_phone:
        df_u = pd.read_csv(USER_DB)
        user_row = df_u[df_u['Phone'].astype(str) == str(input_phone)]
        
        if not user_row.empty:
            u_pass = st.text_input("পাসওয়ার্ড দিন", type="password")
            if st.button("লগইন"):
                if str(user_row.iloc[0]['Password']) == str(u_pass):
                    st.session_state.update({
                        'logged_in': True, 
                        'u_name': user_row.iloc[0]['Name'], 
                        'u_phone': input_phone, 
                        'u_pincode': user_row.iloc[0]['Pincode']
                    })
                    st.rerun()
                else:
                    st.error("ভুল পাসওয়ার্ড!")
        else:
            st.warning("আপনি নতুন কাস্টমার! রেজিস্ট্রেশন করুন।")
            with st.form("reg_form"):
                n = st.text_input("নাম")
                pw = st.text_input("পাসওয়ার্ড (গোপন রাখুন)", type="password")
                addr = st.text_area("পুরো ঠিকানা")
                pin = st.text_input("পিনকোড")
                if st.form_submit_button("রেজিস্ট্রেশন সম্পন্ন করুন"):
                    if n and pw and pin:
                        pd.DataFrame([[n, input_phone, pw, addr, pin]], columns=db_config[USER_DB]).to_csv(USER_DB, mode='a', header=False, index=False)
                        pd.DataFrame([[input_phone, 0]], columns=['Phone', 'Total_Due']).to_csv(DUE_DB, mode='a', header=False, index=False)
                        st.session_state.update({'logged_in': True, 'u_name': n, 'u_phone': input_phone, 'u_pincode': pin})
                        st.rerun()
                    else:
                        st.error("সবগুলো ঘর পূরণ করুন!")

# --- ২. মূল অ্যাপ (লগইন হওয়ার পর) ---
else:
    menu = st.sidebar.radio("মেনু", ["🏠 বাজার করুন", "🛒 বর্তমান ব্যাগ", "👤 প্রোফাইল", "⚙️ অ্যাডমিন প্যানেল"])

    if menu == "🏠 বাজার করুন":
        st.subheader(f"হ্যালো, {st.session_state['u_name']}!")
        df_p = pd.read_excel(EXCEL_FILE)
        cols = st.columns(3)
        for i, row in df_p.iterrows():
            with cols[i % 3]:
                st.info(f"*{row['Name']}*\n\nদাম: ₹{row['Price']}")
                if st.button(f"ব্যাগে নিন", key=f"p_{i}"):
                    st.session_state['cart'].append({"Name": f"{row['Name']} ({row['Type']})", "Price": row['Price']})
                    st.toast(f"{row['Name']} যোগ হয়েছে")

    elif menu == "🛒 বর্তমান ব্যাগ":
        col_hist, col_cart = st.columns([1, 1])
        with col_hist:
            st.markdown("### 📜 আগের অর্ডার")
            df_o = pd.read_csv(ORDER_DB)
            my_old = df_o[df_o['Phone'].astype(str) == str(st.session_state['u_phone'])]
            st.dataframe(my_old[['Date', 'Items', 'Total', 'Status']], use_container_width=True)
        
        with col_cart:
            st.markdown("### 🛍️ চেকআউট")
            if not st.session_state['cart']:
                st.info("আপনার ব্যাগ খালি।")
            else:
                st.warning("লোকেশন পারমিশন 'Allow' করুন")
                loc = get_geolocation() if get_geolocation else None
                
                st.table(pd.DataFrame(st.session_state['cart']))
                pay_m = st.selectbox("পেমেন্ট পদ্ধতি", ["নগদ", "বাকি (Credit)"])
                
                if st.button("🚀 অর্ডার সম্পন্ন করুন"):
                    map_url = "No Location Shared"
                    if loc and 'coords' in loc:
                        map_url = f"https://www.google.com/maps?q={loc['coords']['latitude']},{loc['coords']['longitude']}"
                    
                    total = sum(item['Price'] for item in st.session_state['cart'])
                    items = ", ".join(item['Name'] for item in st.session_state['cart'])
                    
                    new_ord = [datetime.now().strftime("%d/%m/%Y"), st.session_state['u_name'], st.session_state['u_phone'], items, total, "অপেক্ষমান", pay_m, map_url, st.session_state['u_pincode']]
                    pd.DataFrame([new_ord], columns=db_config[ORDER_DB]).to_csv(ORDER_DB, mode='a', header=False, index=False)
                    st.session_state['cart'] = []
                    st.success("অর্ডার সফল হয়েছে!")
                    st.rerun()

    elif menu == "👤 প্রোফাইল":
        st.subheader("👤 প্রোফাইল এডিট করুন")
        df_u = pd.read_csv(USER_DB)
        idx = df_u[df_u['Phone'].astype(str) == str(st.session_state['u_phone'])].index[0]
        with st.form("p_edit"):
            n = st.text_input("নাম", value=df_u.loc[idx, 'Name'])
            pw = st.text_input("নতুন পাসওয়ার্ড", value=df_u.loc[idx, 'Password'])
            pin = st.text_input("পিনকোড", value=df_u.loc[idx, 'Pincode'])
            if st.form_submit_button("আপডেট করুন"):
                df_u.at[idx, 'Name'], df_u.at[idx, 'Password'], df_u.at[idx, 'Pincode'] = n, pw, pin
                df_u.to_csv(USER_DB, index=False)
                st.session_state['u_name'] = n
                st.session_state['u_pincode'] = pin
                st.success("তথ্য আপডেট হয়েছে!")
                st.rerun()

    elif menu == "⚙️ অ্যাডমিন প্যানেল":
        if not st.session_state['admin_unlocked']:
            st.subheader("🔑 অ্যাডমিন লক")
            lock_pass = st.text_input("মাস্টার পাসওয়ার্ড দিন", type="password")
            if st.button("আনলক করুন"):
                if lock_pass == ADMIN_PASSWORD:
                    st.session_state['admin_unlocked'] = True
                    st.rerun()
                else:
                    st.error("ভুল পাসওয়ার্ড!")
        else:
            st.sidebar.button("🔒 লক অ্যাডমিন", on_click=lambda: st.session_state.update({'admin_unlocked': False}))
            t1, t2 = st.tabs(["🆕 নতুন অর্ডার", "📦 ডাটা ম্যানেজমেন্ট"])
            
            with t1:
                df_o = pd.read_csv(ORDER_DB)
                pending = df_o[df_o['Status'] == 'অপেক্ষমান']
                for i, r in pending.iterrows():
                    with st.expander(f"{r['Customer']} (পিন: {r['Pincode']}) - ₹{r['Total']}"):
                        st.write(f"আইটেম: {r['Items']}")
                        if "http" in str(r['Location']):
                            st.markdown(f"[📍 ম্যাপে লোকেশন দেখুন]({r['Location']})")
                        if st.button("কনফার্ম করুন", key=f"c_{i}"):
                            df_o.at[i, 'Status'] = 'Confirmed'
                            df_o.to_csv(ORDER_DB, index=False)
                            st.rerun()

            with t2:
                st.write("### সব অর্ডারের তালিকা")
                st.dataframe(pd.read_csv(ORDER_DB), use_container_width=True)

    if st.sidebar.button("🚪 লগআউট"):
        st.session_state.clear()
        st.rerun()