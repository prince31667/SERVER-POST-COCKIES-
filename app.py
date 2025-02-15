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
    <title>Auto Comment - Created by Rocky Roy</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; border: none; }
        button { background-color: green; color: white; cursor: pointer; }
        input[type="file"] { background-color: #444; color: white; }
    </style>
</head>
<body>
    <h1>Created by Rocky Roy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt"><br>
        <input type="file" name="cookies_file" accept=".txt"><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="min_interval" placeholder="Min Interval (Sec)" required><br>
        <input type="number" name="max_interval" placeholder="Max Interval (Sec)" required><br>
        <button type="submit">Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

def extract_post_id(post_url):
    """Extract Post ID from Facebook URL"""
    match = re.search(r'posts/(\d+)', post_url)
    return match.group(1) if match else None

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    post_url = request.form['post_url']
    min_interval = int(request.form['min_interval'])
    max_interval = int(request.form['max_interval'])

    # Remove tracking parameters
    post_url = re.sub(r'[\?&]fbclid=[^&]+', '', post_url)

    # Read files
    try:
        comments = request.files['comment_file'].read().decode('utf-8').splitlines()
        
        token = None
        if 'token_file' in request.files and request.files['token_file'].filename:
            token = request.files['token_file'].read().decode('utf-8').strip()

        cookies = None
        if 'cookies_file' in request.files and request.files['cookies_file'].filename:
            cookies = request.files['cookies_file'].read().decode('utf-8').strip()
        
    except Exception:
        return render_template_string(HTML_FORM, message="❌ फाइलें सही नहीं हैं!")

    post_id = extract_post_id(post_url)
    if not post_id:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    comment_url = f"https://m.facebook.com/{post_id}/comment/"
    graph_url = f"https://graph.facebook.com/{post_id}/comments"

    # Setup session & headers
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"https://m.facebook.com/{post_id}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://m.facebook.com",
        "Connection": "keep-alive"
    }
    session.headers.update(headers)

    # Add cookies to session if available
    if cookies:
        cookies_dict = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in cookies.split("; ")}
        session.cookies.update(cookies_dict)

    success_count = 0

    for comment in comments:
        success = False

        # Try Cookies Method First
        if cookies:
            payload = {'comment_text': comment}
            response = session.post(comment_url, data=payload)
            if response.status_code == 200:
                success = True
                success_count += 1
                print(f"✅ [Cookies] Comment Posted: {comment}")
        
        # If Cookies Fail, Try Token Method
        if not success and token:
            payload = {'message': comment, 'access_token': token}
            response = requests.post(graph_url, data=payload)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ [Token] Comment Posted: {comment}")
            else:
                print(f"❌ Failed to post: {comment}")
                return render_template_string(HTML_FORM, message="❌ Token और Cookies दोनों Invalid हैं!")

        # Randomized Delay
        delay = random.uniform(min_interval, max_interval)
        print(f"Waiting {delay:.2f} seconds before next comment...")
        time.sleep(delay)

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
