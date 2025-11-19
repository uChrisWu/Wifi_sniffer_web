import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 保存最近一条数据
latest_data = {
    "instant": 0,
    "smoothed": 0.0,
    "time": None,
    "ip": None,
}

@app.route("/", methods=["GET"])
def index():
    # 展示当前最新的数据
    return render_template("index.html", data=latest_data)

@app.route("/upload", methods=["POST"])
def upload():
    global latest_data

    # 解析 JSON
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "msg": "invalid json"}), 400

    # 记录时间 & 发送方 IP
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    sender_ip = request.remote_addr

    # 从 ESP32 上传的数据中取 instant / smoothed
    instant = data.get("instant")
    smoothed = data.get("smoothed")

    # 更新全局状态
    latest_data = {
        "instant": instant,
        "smoothed": smoothed,
        "time": now,
        "ip": sender_ip,
    }

    # 控制台打印一下方便调试
    print(f"[{now}] from {sender_ip} -> {data}")

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Render 会通过 PORT 环境变量告诉你要监听哪个端口
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
