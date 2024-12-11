from flask import Flask, Response, request, jsonify, render_template
from chaleur import HeatSimulation3D
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
    sim = HeatSimulation3D(150, 150, diffusion_rate=0.15)
    fig, ax = plt.subplots(figsize=(10, 8))

    sim.add_heat_source(15, 15, temperature=1.0, radius=4)
    sim.add_heat_source(10, 10, temperature=0.8, radius=3)
    sim.add_heat_source(20, 20, temperature=0.6, radius=3)

    while True:
        t0 = time.time()
        data = get_data()
        for d in data:
            print(
                f"x: {type(float(d['x']))}, y: {type(float(d['y']))}, z: {type(d['z'])}"
            )

            sim.add_heat_source(
                round(float(d["x"]) * 10),
                round(float(d["y"]) * 10),
                temperature=round(float(d["z"]) / 10),
                radius=round(float(d["z"]) / 4),
            )
        sim.update()
        sim.visualize_2d(ax)

        print("Données arrivant dans generate_frame :", data)

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
