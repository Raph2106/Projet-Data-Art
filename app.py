from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO, emit
from chaleur import generate_frame
import time
import logging
import threading

logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.basicConfig(
    filename="old_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
app.debug = True

socketio = SocketIO(app)

shared_data = {"x": 1.0}
test_data = {"x": 2.0}
data_lock = threading.Lock()


def get_shared_data():
    with data_lock:
        return shared_data


@app.context_processor
def inject_time():
    return {"time": time.time}


@app.route("/websocket")
def index():
    return render_template("index.html")


@app.route("/post", methods=["POST"])
def update_data():
    test_data["x"] = request.json["x"]
    return {"Données reçues": test_data}


# mettre route /websocket
@app.route("/video_feed")
def video_feed():
    return render_template("video_feed.html")


@app.route("/video_socket")
def video_socket():
    return render_template("video_socket.html")


@app.route("/test")
def testFlask():
    return Response(response="Réponse de Flask. \n")


@app.route("/websocket/video_stream")
def video_stream():
    return Response(
        generate_frame(get_shared_data),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@socketio.on("send_data")
def handle_send_data(data):
    global shared_data
    with data_lock:
        shared_data["x"] = data["x"]
    print("Données reçues:", data)
    emit("data_response", {"status": "Données reçues avec succès"})


@socketio.on("start_video")
def start_video():
    for frame_base64 in generate_frame():
        emit("new_frame", {"image": frame_base64})
        time.sleep(0.04)


if __name__ == "__main__":
    socketio.run(app, host="::1", port=1120)
