import pandas as pd

# ৭৫০টি ফাঁকা পণ্যের ঘর তৈরি করা
total_products = 750
data = {
    'Name': [f'পণ্য {i}' for i in range(1, total_products + 1)],
    'Price': [0] * total_products
}

df = pd.DataFrame(data)

# এক্সেল ফাইল হিসেবে সেভ করা
file_name = 'products.xlsx'
df.to_excel(file_name, index=False)

print(f"✅ অভিনন্দন! {file_name} তৈরি হয়েছে যেখানে {total_products}টি ঘর আছে।")
print("এখন আপনি এই ফাইলটি ওপেন করে আপনার আসল পণ্যের নাম ও দাম লিখে সেভ করুন।")