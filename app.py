import os
import requests
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# Facebook Auto-Comment Function
def post_comment(post_id, comment, cookies):
    url = f"https://m.facebook.com/{post_id}/comments"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookies
    }
    data = {"comment_text": comment, "submit": "Post"}

    response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200

# Web UI Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Auto-Commenter</title>
</head>
<body>
    <h2>Facebook Auto-Commenter</h2>
    <form method="POST">
        <label>Post URL:</label>
        <input type="text" name="post_url" required><br>

        <label>Comment:</label>
        <input type="text" name="comment" required><br>

        <label>Cookies:</label>
        <textarea name="cookies" required></textarea><br>

        <button type="submit">Post Comment</button>
    </form>
    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        post_url = request.form["post_url"]
        comment = request.form["comment"]
        cookies = request.form["cookies"]

        post_id = post_url.split("/")[-1] if "/" in post_url else post_url
        success = post_comment(post_id, comment, cookies)
        message = "✅ Comment Posted!" if success else "❌ Failed to Post Comment!"

    return render_template_string(HTML_TEMPLATE, message=message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render ke liye port bind
    app.run(host="0.0.0.0", port=port)
