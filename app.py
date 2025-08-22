from flask import Flask, jsonify, send_from_directory
import requests
from datetime import datetime

API_KEY = "e8be9f1ba2074ab09d59b389c591311c"
MAPID = "40540"

app = Flask(__name__, static_folder="static", static_url_path='')

ROUTE_COLORS = {
    "Red": "#FF0000",
    "Blue": "#0000FF",
    "Brn": "#A52A2A",
    "G": "#00FF00",
    "Org": "#FFA500",
    "Pink": "#FF69B4",
    "P": "#800080",
    "Y": "#FFFF00",
    "Purple": "#800080",
}


def fetch_arrivals():
    try:
        url = f"http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key={API_KEY}&mapid={MAPID}&max=5&outputType=JSON"
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("ctatt", {}).get("eta", [])
    except Exception as e:
        print("CTA API error:", e)
        return []


@app.route("/api/trains")
def api_trains():
    arrivals = fetch_arrivals()
    trains = []
    for entry in arrivals:
        arr_time_str = entry.get("arrT")
        if not arr_time_str:
            continue
        eta = datetime.strptime(arr_time_str, "%Y-%m-%dT%H:%M:%S")
        trains.append({
            "train_id": entry.get("rn"),
            "route": entry.get("rt"),
            "dest": entry.get("destNm"),
            "eta_iso": eta.isoformat()
        })
    # Sort by ETA
    trains.sort(key=lambda t: t["eta_iso"])
    return jsonify(trains)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
