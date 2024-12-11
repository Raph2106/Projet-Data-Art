from flask import Flask, Response, request, jsonify, render_template
from chaleur import HeatSimulation3D
import logging
import matplotlib.pyplot as plt
import io
import time

app = Flask(__name__)
data_switch = 0
data_switches = (1, 0)
user_data0 = []
user_data1 = []
frame_data = []
app.debug = True


logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.basicConfig(
    filename="old_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_data():
    global data_switch, frame_data, user_data0, user_data1
    if data_switch == 0:
        user_data1 = []
        data_switch = data_switches[data_switch]
        data = user_data0.copy()
    elif data_switch == 1:
        user_data0 = []
        data_switch = data_switches[data_switch]
        data = user_data1.copy()
    return data


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
    print("Données reçue :", data, "\nSwitch :", data_switch)
    if data_switch == 0:
        print("Traitement pour switch 0: \n user_data0 avant append:", user_data0)
        user_data0.append(data)
        print("user_data0 après append:", user_data0)
    elif data_switch == 1:
        print("Traitement pour switch 1: \n user_data1 avant append:", user_data1)
        user_data1.append(data)
        print("user_data1 après append:", user_data1)
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
