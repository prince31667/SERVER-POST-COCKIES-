from flask import Flask, request, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
        input, textarea { width: 300px; padding: 10px; margin: 5px; border-radius: 5px; }
        button { background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Facebook Auto Commenter</h1>
    <form method="POST" action="/submit" enctype="multipart/form-data">
        <input type="file" name="cookies_file" accept=".txt" required><br>
        <input type="file" name="comment_file" accept=".txt" required><br>
        <input type="text" name="post_url" placeholder="Enter Facebook Post URL" required><br>
        <input type="number" name="interval_min" placeholder="Min Interval (seconds)" required><br>
        <input type="number" name="interval_max" placeholder="Max Interval (seconds)" required><br>
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
    interval_min = int(request.form['interval_min'])
    interval_max = int(request.form['interval_max'])

    cookies = cookies_file.read().decode('utf-8').strip()
    comments = comment_file.read().decode('utf-8').splitlines()

    # Setup Selenium with undetected_chromedriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Open Facebook
    driver.get("https://www.facebook.com/")
    time.sleep(3)  # Allow page to load

    # Inject cookies
    for cookie in cookies.split("; "):
        key, value = cookie.split("=", 1)
        driver.add_cookie({"name": key, "value": value})

    # Reload page with authenticated session
    driver.get(post_url)
    time.sleep(5)  # Wait for post to load

    success_count = 0
    for comment in comments:
        try:
            comment_box = driver.find_element(By.XPATH, "//div[@aria-label='Write a comment']")
            comment_box.click()
            time.sleep(2)
            comment_box.send_keys(comment)
            time.sleep(1)
            comment_box.send_keys(Keys.ENTER)

            success_count += 1
            print(f"✅ Comment Posted: {comment}")

            sleep_time = random.randint(interval_min, interval_max)
            print(f"⏳ Waiting {sleep_time} seconds before next comment...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"⚠️ Error: {e}")

    driver.quit()
    return render_template_string(HTML_FORM, message=f"✅ {success_count} Comments Successfully Posted!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
