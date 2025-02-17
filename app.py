import requests
import time

# 🔹 Facebook पोस्ट ID
post_id = "555023942715392"

# 🔹 Facebook कुकीज़ (अपनी वैध Cookies डालें)
cookies = {
    "datr": "OiqtZ7kwfUef3svGUSdK4QWY",
    "sb": "OiqtZ0HC_GuEQ9hu3IQY-K2p",
    "c_user": "61559728229012",
    "xs": "6:jefp00XZqPIsoQ:2:1739401810:-1:4885",
    "fr": "0HPDRxqyG4iGJICOc.AWWmSxFA1MGyKgzQRZlP2G5bb0eBvl-17w3Z0g.BnrSo6..AAA.0.0.BnrToP.AWVr9bobbVo"
}

# 🔹 Facebook Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded"
}

# 🔹 Comment Payload (जो कमेंट पोस्ट होगा)
comment_text = "SAMART X3 YASH H3R3"

# 🔹 Facebook GraphQL API का URL
url = f"https://www.facebook.com/api/graphql/"

# 🔹 डेटा (Payload)
payload = {
    "ft_ent_identifier": post_id,
    "comment_text": comment_text
}

# 🔹 10 बार कमेंट करने के लिए लूप
for i in range(10):  # आप जितनी बार चाहें उतनी बार चला सकते हैं
    response = requests.post(url, headers=headers, cookies=cookies, data=payload)

    if response.status_code == 200:
        print(f"✅ [{i+1}] सफलतापूर्वक Comment पोस्ट हो गया: {comment_text}")
    else:
        print(f"❌ [{i+1}] Error: {response.text}")

    # 🔹 170 सेकंड (2 मिनट 50 सेकंड) का डिले
    print("⏳ अगला कमेंट 170 सेकंड बाद पोस्ट होगा...")
    time.sleep(170)
