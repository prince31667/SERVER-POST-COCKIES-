from flask import Flask, request, render_template_string import requests import time import threading import random

app = Flask(name)

HTML_FORM = '''

<!DOCTYPE html><html>
<head>
    <title>🚀 Auto Comment - Created by Perfect Loser King Server</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🔥 Created by Rocky Roy 🔥</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <label>📂 Upload Access Token File:</label>
        <input type="file" name="token_file" accept=".txt"><br><label>🍪 Upload Cookies File:</label>
    <input type="file" name="cookies_file" accept=".txt" multiple><br>

    <label>💬 Upload Comments File:</label>
    <input type="file" name="comment_file" accept=".txt" required><br>

    <label>🔗 Enter Facebook Post URL:</label>
    <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>

    <label>⏳ Set Time Delay (Seconds):</label>
    <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 5)" required><br>

    <button type="submit">🚀 Start Commenting</button>
</form>

{% if message %}<p>{{ message }}</p>{% endif %}

</body>
</html>
'''@app.route('/') def index(): return render_template_string(HTML_FORM)

def post_comment(url, payload, headers=None): try: response = requests.post(url, data=payload, headers=headers) return response.status_code == 200 except Exception as e: print(f"⚠️ Error posting comment: {e}") return False

@app.route('/submit', methods=['POST']) def submit(): token_file = request.files.get('token_file') cookies_files = request.files.getlist('cookies_file') comment_file = request.files['comment_file'] post_url = request.form['post_url'] interval = int(request.form['interval'])

tokens = token_file.read().decode('utf-8').splitlines() if token_file else []
comments = comment_file.read().decode('utf-8').splitlines()
cookies_list = [file.read().decode('utf-8').strip() for file in cookies_files if file]

try:
    post_id = post_url.split("posts/")[1].split("/")[0]
except IndexError:
    return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

url = f"https://graph.facebook.com/{post_id}/comments"

def start_commenting():
    while True:
        for i, token in enumerate(tokens):
            comment = comments[i % len(comments)] + " " + random.choice(["😊", "🔥", "🚀", "💯", "💖"])
            delay = random.uniform(interval, interval + 5)
            headers = {'User-Agent': random.choice([
                'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A)',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            ])}
            
            if post_comment(url, {'message': comment, 'access_token': token}, headers):
                print(f"✅ Comment posted: {comment}")
            time.sleep(delay)

threading.Thread(target=start_commenting, daemon=True).start()
return render_template_string(HTML_FORM, message="✅ Auto-commenting started in the background!")

if name == 'main': app.run(host='0.0.0.0', port=10000)

