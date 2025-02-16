from flask import Flask, request, render_template_string
import requests
import time
import random
import re

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Comment - Cookies Method</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; border: none; }
        button { background-color: green; color: white; cursor: pointer; }
        input[type="file"] { background-color: #444; color: white; }
    </style>
</head>
<body>
    <h1>Facebook Auto Comment (Cookies Method)</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="cookies_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
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

def get_fb_dtsg(session):
    """Fetch fb_dtsg token from Facebook"""
    response = session.get("https://m.facebook.com/")
    match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
    return match.group(1) if match else None

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    # Read Files
    try:
        cookies_string = request.files['cookies_file'].read().decode('utf-8').strip()
        comments = request.files['comment_file'].read().decode('utf-8').splitlines()
    except Exception:
        return render_template_string(HTML_FORM, message="❌ Invalid Cookies or Comment File!")

    cookies = parse_cookies(cookies_string)

    # Extract Post ID
    post_id_match = re.search(r'/posts/(\d+)', post_url)
    post_id = post_id_match.group(1) if post_id_match else None
    if not post_id:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://m.facebook.com/a/comment.php?ft_ent_identifier={post_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)

    # Get fb_dtsg token
    fb_dtsg = get_fb_dtsg(session)
    if not fb_dtsg:
        return render_template_string(HTML_FORM, message="❌ Failed to fetch fb_dtsg token!")

    success_count = 0
    for comment in comments:
        payload = {
            "fb_dtsg": fb_dtsg,
            "comment_text": comment
        }
        response = session.post(url, data=payload)

        if response.status_code == 200:
            success_count += 1
        else:
            return render_template_string(HTML_FORM, message="❌ Comment Failed! Cookies Expired or Invalid.")

        # Randomized Delay to Avoid Detection
        time.sleep(interval + random.uniform(1, 3))

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
