import os
from datetime import datetime
from collections import deque
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 保存最近一条数据（用于首页大数字）
latest_data = {
    "instant": 0,
    "smoothed": 0.0,
    "time": None,
    "ip": None,
}

# 历史记录：保存最近 N 条（例如 720 条，如果 ESP32 每 5 秒上传一次 ≈ 1 小时）
HISTORY_MAX_POINTS = 720
history = deque(maxlen=HISTORY_MAX_POINTS)


@app.route("/", methods=["GET"])
def index():
    # 首页渲染模板，模板里会用到 latest_data
    return render_template("index.html", data=latest_data)


@app.route("/upload", methods=["POST"])
def upload():
    global latest_data, history

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"status": "error", "msg": "invalid json"}), 400

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    sender_ip = request.remote_addr

    instant = data.get("instant")
    smoothed = data.get("smoothed")

    # 更新当前最新值
    latest_data = {
        "instant": instant,
        "smoothed": smoothed,
        "time": now,
        "ip": sender_ip,
    }

    # 追加到历史记录
    history.append({
        "time": now,
        "instant": instant,
        "smoothed": smoothed,
    })

    print(f"[{now}] from {sender_ip} -> {data}")

    return jsonify({"status": "ok"}), 200


@app.route("/data", methods=["GET"])
def get_data():
    """
    前端用来获取历史数据的接口，返回：
    {
      "points": [
        {"time": "...", "instant": 3, "smoothed": 2.5},
        ...
      ]
    }
    """
    return jsonify({
        "points": list(history)
    })


if __name__ == "__main__":
    # Render 会通过 PORT 环境变量指定端口
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
