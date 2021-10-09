from flask import Flask, jsonify
import requests
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = True


@app.route("/")
def first_page():
    return "This is for Dota Api"


@app.route("/dota_status")
def dota_status():
    for i in range(5):
        try:
            with open(f"ApiFile/dota_status_{i}.json", "rb") as f:
                return jsonify(json.load(f))
        except:
            pass
    return "No file"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

