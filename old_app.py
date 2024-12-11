from flask import Flask, Response, request, jsonify, render_template
from chaleur import HeatSimulation3D, HeatSimulation2D
import logging
import matplotlib.pyplot as plt
import io
import time
import redis
import json

app = Flask(__name__)
app.debug = True
r = redis.StrictRedis(host="localhost", port=6379, db=0)

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.basicConfig(
    filename="old_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_data():
    keys = r.keys("user_data_*")
    all_data = []

    for key in keys:
        while True:
            data = r.lpop(key)
            if not data:
                break
            all_data.append(json.loads(data))

    return all_data


def generate_frame():

    plt.ioff()
    data = {}
    sim = HeatSimulation2D(150, 150, diffusion_rate=0.15)
    fig, ax = plt.subplots(figsize=(10, 8))

    while True:
        t0 = time.time()
        data = get_data()
        for d in data:
            sim.add_heat_source2(
                round(float(d["x"])),
                round(float(d["y"])),
                temperature=round(abs(float(d["z"]))),
                radius=round(float(d["z"])),
            )
        sim.update()
        sim.visualize_2d(ax)

        buf = io.BytesIO()
        plt.savefig(buf, format="jpeg", bbox_inches="tight")
        buf.seek(0)

        frame = buf.read()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

        buf.close()
        t1 = time.time()
        if t1 - t0 < 0.04:
            time.sleep(0.04 - (t1 - t0))


@app.route("/old")
def old():
    return render_template("old_index.html")


@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    # user_data.put(data)
    unique_key = f"user_data_{int(time.time() * 1000)}"
    json_data = json.dumps(data)
    r.rpush(unique_key, json_data)
    print(f"Données reçues : {data}")

    return jsonify({"status": "success", "received": data})


@app.route("/video_stream")
def video_stream():
    return Response(
        generate_frame(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    app.run(host="::1", port=1120)
