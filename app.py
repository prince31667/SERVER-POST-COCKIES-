from flask import Flask, request, render_template_string
import requests
import time
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; border: none; }
        button { background-color: green; color: white; cursor: pointer; }
        input[type="file"] { background-color: #444; color: white; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="text" name="cookies" placeholder="Enter Facebook Cookies" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="text" name="comment" placeholder="Enter Comment" required><br>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 5)" required><br>
        <button type="submit">Submit</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

def parse_cookies(cookie_string):
    """Convert cookies from string to dictionary format"""
    cookies = {}
    for item in cookie_string.split("; "):
        key, value = item.split("=", 1)
        cookies[key] = value
    return cookies

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    cookies_string = request.form['cookies']
    post_url = request.form['post_url']
    comment = request.form['comment']
    interval = int(request.form['interval'])

    # Parse Cookies
    try:
        cookies = parse_cookies(cookies_string)
    except Exception:
        return render_template_string(HTML_FORM, message="❌ Invalid Cookies Format!")

    # Extract Post ID
    post_id = post_url.split("/")[-2] if "/posts/" in post_url else None
    if not post_id:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    # Facebook Comment URL
    url = f"https://m.facebook.com/{post_id}/comment/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Initialize Session
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)

    # Test Cookies Validity
    test_url = "https://m.facebook.com/"
    test_response = session.get(test_url)
    if "login" in test_response.url:
        return render_template_string(HTML_FORM, message="❌ Invalid Cookies! Please provide valid cookies.")

    # Post Comment
    payload = {"comment_text": comment}
    response = session.post(url, data=payload)

    if response.status_code == 200:
        message = "✅ Comment Posted Successfully!"
    else:
        message = "❌ Comment Failed! Cookies Expired or Invalid."

    # Randomized Delay to Avoid Detection
    time.sleep(interval + random.uniform(1, 3))

    return render_template_string(HTML_FORM, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
