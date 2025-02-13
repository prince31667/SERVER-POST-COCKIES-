from flask import Flask, request, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Commenter - Created by Rocky Roy</title>
    <style>
        body { background-color: black; color: white; text-align: center; font-family: Arial, sans-serif; }
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Created by Rocky Roy</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="cookies_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval" placeholder="Interval in Seconds (e.g., 5)" required><br>
        <button type="submit">Start Commenting</button>
    </form>
    {% if message %}<p>{{ message }}</p>{% endif %}
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_FORM)

@app.route('/submit', methods=['POST'])
def submit():
    cookies_file = request.files['cookies_file']
    comment_file = request.files['comment_file']
    post_url = request.form['post_url']
    interval = int(request.form['interval'])

    cookies = cookies_file.read().decode('utf-8').strip()
    comments = comment_file.read().decode('utf-8').splitlines()

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Background mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.facebook.com/")
        
        # Inject cookies
        for cookie in cookies.split(";"):
            name, value = cookie.strip().split("=", 1)
            driver.add_cookie({"name": name, "value": value, "domain": ".facebook.com"})

        driver.get(post_url)
        time.sleep(5)  # Wait for page to load

        for comment in comments:
            try:
                comment_box = driver.find_element(By.XPATH, "//div[@aria-label='Write a comment…']")
                comment_box.click()
                time.sleep(2)

                comment_box.send_keys(comment)
                time.sleep(2)

                post_button = driver.find_element(By.XPATH, "//div[@aria-label='Press Enter to post.']")
                post_button.click()
                
                time.sleep(interval)
            except Exception as e:
                print(f"Error posting comment: {e}")
                continue

    finally:
        driver.quit()

    return render_template_string(HTML_FORM, message="✅ Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
