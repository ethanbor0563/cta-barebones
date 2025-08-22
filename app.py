#!/usr/bin/env python3
import os
import time
import requests
from flask import Flask, jsonify, send_from_directory

# --- robust static folder path (works regardless of working directory) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# create Flask app pointing to absolute static folder
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')

# small CTA proxy /placeholder (keep your real implementation here)
@app.route('/api/trains')
def api_trains():
    # placeholder response so /api/trains returns 200 while you debug
    return jsonify({'ok': True, 'arrivals': []})

# serve index.html from the absolute static folder
@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

# serve other static files (css/js) if requested
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(STATIC_DIR, path)

if __name__ == '__main__':
    # debug=False in general; set True temporarily for extra logging if needed
    app.run(host='0.0.0.0', port=5000, threaded=True)
