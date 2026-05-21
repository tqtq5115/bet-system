from flask import Flask, jsonify, request
from flask_cors import CORS
import threading, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)

data = {
    "numbers": [],
    "users": [{"id": "A101", "bal": 1000}],
    "bets": [],
    "odds_rules": [{"start": 0, "end": 289, "odds": 0.95}]
}

def crawler():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    while True:
        try:
            driver.get("https://www.taiwanlottery.com/lotto/result/bingo_bingo")
            time.sleep(3)
            nums = driver.execute_script("return Array.from(document.querySelectorAll('.ball_tx')).map(e=>parseInt(e.innerText)).filter(n=>!isNaN(n)).slice(0,20)")
            if nums: data["numbers"] = sorted(nums)
        except: pass
        time.sleep(30)

@app.route('/api/state', methods=['GET', 'POST'])
def state():
    if request.method == 'POST':
        data.update(request.json)
        return jsonify({"status": "success"})
    return jsonify(data)

@app.route('/api/register', methods=['POST'])
def register():
    new_user = request.json
    if any(u["id"] == new_user["id"] for u in data["users"]):
        return jsonify({"status": "error", "message": "帳號已存在"}), 400
    data["users"].append({"id": new_user["id"], "bal": 1000})
    return jsonify({"status": "success"})

@app.route('/api/bet', methods=['POST'])
def place_bet():
    bet = request.json
    amount = int(bet.get("amount", 0))
    if amount % 100 != 0 or amount <= 0:
        return jsonify({"status": "error", "message": "需為100倍數"}), 400
    bet["ip"] = request.remote_addr
    for user in data["users"]:
        if user["id"] == bet["user"]:
            if user["bal"] >= amount:
                user["bal"] -= amount
                data["bets"].insert(0, bet)
                return jsonify({"status": "success", "new_bal": user["bal"]})
            else:
                return jsonify({"status": "error", "message": "餘額不足"}), 400
    return jsonify({"status": "error", "message": "無此用戶"}), 404

if __name__ == '__main__':
    threading.Thread(target=crawler, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)