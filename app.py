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
    cookies = {}
    for item in cookie_string.split("; "):
        key, value = item.split("=", 1)
        cookies[key] = value
    return cookies

def extract_post_id(url):
    match = re.search(r"(?:posts/|permalink.php\?story_fbid=|fbid=)(\d+)", url)
    return match.group(1) if match else None

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    try:
        cookies_string = request.files['cookies_file'].read().decode('utf-8').strip()
        comments = request.files['comment_file'].read().decode('utf-8').splitlines()
    except Exception:
        return render_template_string(HTML_FORM, message="❌ Invalid Cookies or Comment File!")

    cookies = parse_cookies(cookies_string)

    post_id = extract_post_id(post_url)
    if not post_id:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    session = requests.Session()
    session.cookies.update(cookies)

    # **Step 1: CSRF Token Lo**
    home_page = session.get("https://m.facebook.com/home.php")
    fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', home_page.text)
    jazoest_match = re.search(r'name="jazoest" value="(.*?)"', home_page.text)

    if not fb_dtsg_match or not jazoest_match:
        return render_template_string(HTML_FORM, message="❌ Failed to get CSRF token. Invalid cookies!")

    fb_dtsg = fb_dtsg_match.group(1)
    jazoest = jazoest_match.group(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://m.facebook.com",
        "Referer": f"https://m.facebook.com/{post_id}"
    }

    success_count = 0
    for comment in comments:
        payload = {
            "fb_dtsg": fb_dtsg,
            "jazoest": jazoest,
            "comment_text": comment
        }

        comment_url = f"https://m.facebook.com/a/comment.php?ft_ent_identifier={post_id}"
        response = session.post(comment_url, data=payload, headers=headers)

        if "comment" in response.url:
            success_count += 1
        else:
            return render_template_string(HTML_FORM, message="❌ Comment Failed! Check Cookies.")

        time.sleep(interval + random.uniform(1, 5))

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
