from flask import Flask, request, render_template_string
import requests
import time
import os

app = Flask(__name__)

# HTML Form (Interval Option Added)
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
        <input type="number" name="interval" placeholder="Interval in Minutes (e.g., 10)" required><br>
        <button type="submit">Submit Your Details</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

# Function: Wait Before Next Comment
def wait_for_next_comment(user_interval):
    """User-defined time (minutes) ke hisaab se wait karega"""
    if os.path.exists("time.txt"):
        with open("time.txt", "r") as f:
            last_time = float(f.read().strip())
    else:
        last_time = 0  # Pehla comment turant chalega

    current_time = time.time()
    time_difference = current_time - last_time

    wait_time = user_interval * 60  # Convert minutes to seconds

    if time_difference < wait_time:
        remaining_time = wait_time - time_difference
        print(f"⏳ Waiting {int(remaining_time)} more seconds before next comment...")
        time.sleep(remaining_time)

    # Save new time
    with open("time.txt", "w") as f:
        f.write(str(time.time()))

    print("✅ Now you can post the next comment!")

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    token_file = request.files['token_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    user_interval = int(request.form['interval'])  # User-defined interval (minutes)

    tokens = token_file.read().decode('utf-8').splitlines()
    comments = comment_file.read().decode('utf-8').splitlines()

    try:
        post_id = post_url.split("posts/")[1].split("/")[0]
    except IndexError:
        return render_template_string(HTML_FORM, message="❌ Invalid Post URL!")

    url = f"https://graph.facebook.com/{post_id}/comments"

    success_count = 0

    for i in range(len(comments)):
        wait_for_next_comment(user_interval)  # **Wait before posting**

        current_token = tokens[i % len(tokens)]  # Token ko rotate karega
        current_comment = comments[i]  # Next comment pick karega
        
        payload = {'message': current_comment, 'access_token': current_token}

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print(f"✅ Comment Posted: {current_comment}")
            success_count += 1
        elif response.status_code == 400:
            print("❌ Invalid Token")
            continue  # Invalid token, next token use karega
        else:
            print(f"⚠️ API Error: {response.status_code}")
            continue  # Other API errors ke liye skip karega

    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
