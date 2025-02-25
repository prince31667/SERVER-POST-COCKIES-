from flask import Flask, request, render_template_string
import requests
import time
import random
import threading

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Comment - Anti-Ban Mode</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, button { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
    <script>
        function stopCommenting() {
            fetch('/stop', { method: 'POST' });
            alert('Commenting Stopped!');
        }
    </script>
</head>
<body>
    <h1>Facebook Auto Comment - Anti-Ban Mode</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Minimum Time Interval (Seconds)" required><br>
        <button type="submit">Start Safe Commenting</button>
    </form>
    <button onclick="stopCommenting()">Stop Commenting</button>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

running = False  # Control variable to stop commenting

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/stop', methods=['POST'])
def stop():
    global running
    running = False
    return "Stopping Commenting Process!"

@app.route('/submit', methods=['POST'])
def submit():
    global running
    running = True  # Allow commenting to start

    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"
    success_count = 0

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 9; Redmi 5A) AppleWebKit/537.36"
    ]

    def modify_comment(comment):
        """Spam से बचने के लिए Comment में Random Variations जोड़ें।"""
        emojis = ["🔥", "✅", "💯", "👏", "😊", "👍", "🙌", "🎉", "😉", "💪"]
        variations = ["!!", "!!!", "✔️", "...", "🤩", "💥"]
        invisible_chars = ["‎", "​", "‍"]  # Hidden Unicode characters

        # Add hidden characters randomly to avoid detection
        comment = "".join([char + random.choice(invisible_chars) if random.random() > 0.8 else char for char in comment])

        return f"{random.choice(variations)} {comment} {random.choice(emojis)}"

    def post_with_token(token, comment):
        """Facebook API को Modified Comment भेजेगा।"""
        headers = {
            "User-Agent": random.choice(user_agents),
            "Referer": "https://www.facebook.com/",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        payload = {'message': modify_comment(comment), 'access_token': token}

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            return response
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network Error: {e}")
            return None

    def commenting_process():
        nonlocal success_count
        token_index = 0
        cooldown_tokens = {}  # Dictionary to track blocked tokens and cooldown time

        while running:
            token = tokens[token_index % len(tokens)]
            comment = comments[token_index % len(comments)]

            # Check if the token is in cooldown
            if token in cooldown_tokens and time.time() < cooldown_tokens[token]:
                print(f"⏳ Token {token_index+1} in cooldown, skipping...")
                token_index += 1
                continue

            response = post_with_token(token, comment)

            if response and response.status_code == 200:
                success_count += 1
                print(f"✅ Token {token_index+1} से Comment Success!")
            else:
                print(f"❌ Token {token_index+1} Blocked, Adding Cooldown...")
                cooldown_tokens[token] = time.time() + random.randint(300, 600)  # Cooldown for 5-10 mins

            token_index += 1

            # **Safe Delay for Anti-Ban**
            safe_delay = interval + random.randint(10, 50)
            print(f"⏳ Waiting {safe_delay} seconds before next comment...")
            time.sleep(safe_delay)

    # Run commenting in a background thread
    thread = threading.Thread(target=commenting_process)
    thread.start()

    return render_template_string(HTML_FORM, message="✅ Commenting Started! Click 'Stop Commenting' to halt.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
