from flask import Flask, Response, Request, jsonify, render_template

app = Flask(__name__)
user_data = {}


@app.route("/old")
def old():
    return render_template("old_index.html")


@app.route("/data", methods=["POST"])
def receive_data():
    data = Request.json
    user_data["last_received"] = data
    print(f"Données reçues : {data}")

    return jsonify({"status": "success", "received": data})


if __name__ == "__main__":
    app.run(host="::1", port=1120)
