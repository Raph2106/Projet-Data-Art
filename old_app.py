from flask import Flask, request, jsonify, render_template
import logging

app = Flask(__name__)
user_data = {}
app.debug = True


logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.basicConfig(
    filename="old_app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

shared_data = {"x": 1.0}
test_data = {"x": 2.0}


@app.route("/old")
def old():
    return render_template("old_index.html")


@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    user_data["last_received"] = data
    print(f"Données reçues : {data}")

    return jsonify({"status": "success", "received": data})


if __name__ == "__main__":
    app.run(host="::1", port=1120)
