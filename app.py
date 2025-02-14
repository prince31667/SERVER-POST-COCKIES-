from flask import Flask, request, render_template_string
import requests
import time
import os
import random

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Auto Comment - Created by Raghu ACC Rullx</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Created by Raghu ACC Rullx Boy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="token_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <button type="submit">Submit Your Details</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

def wait_for_next_comment():
    """10 min ke baad ek comment karega, fir next comment 15 min baad hoga"""
    if os.path.exists("time.txt"):
        with open("time.txt", "r") as f:
            last_time, last_delay = map(float, f.read().strip().split())
    else:
        last_time, last_delay = 0, 600  # Default: Pehla comment 10 min baad hoga

    current_time = time.time()
    time_difference = current_time - last_time

    if time_difference < last_delay:
        wait_time = last_delay - time_difference
        print(f"⏳ Waiting {int(wait_time)} seconds before next comment...")
        time.sleep(wait_time)

    # Next comment ke liye delay 15 min set karo
    next_delay = 900 if last_delay == 600 else 600  # 10 min → 15 min → 10 min

    # Naya time & delay save karo
    with open("time.txt", "w") as f:
        f.write(f"{time.time()} {next_delay}")

    print("✅ Now you can post the next comment!")

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"

    wait_for_next_comment()  # **Wait before posting**

    # **Ek Hi Comment Post Karega**
    current_token = tokens[0]  # Pehla token use karega
    current_comment = comments[0]  # Pehla comment use karega
    
    payload = {'message': current_comment, 'access_token': current_token}
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print(f"✅ Comment Posted: {current_comment}")
        return render_template_string(HTML_FORM, message="✅ 1 Comment Successfully Posted!")
    elif response.status_code == 400:
        print("❌ Invalid Token")
        return render_template_string(HTML_FORM, message="❌ Invalid Token!")
    else:
        print(f"⚠️ API Error: {response.status_code}")
        return render_template_string(HTML_FORM, message=f"⚠️ API Error: {response.status_code}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
