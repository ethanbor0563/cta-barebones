#!/usr/bin/env python3
# app.py -- very lightweight CTA proxy for the frontend
import os
import time
import requests
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

# CONFIG: set these in environment on the Pi (or edit here temporarily)
CTA_KEY = os.environ.get('CTA_KEY', 'YOUR_CTA_KEY_HERE')
STOP_ID = os.environ.get('CTA_STOPID', 'YOUR_STOP_ID_HERE')
CTA_MAX = int(os.environ.get('CTA_MAX', '8'))

# small in-memory cache to avoid repeated calls
_cache = {'ts': 0, 'data': None}
CACHE_SECONDS = 5

def fetch_cta():
    global _cache
    if time.time() - _cache['ts'] < CACHE_SECONDS and _cache['data'] is not None:
        return _cache['data']
    url = 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx'
    params = {
        'key': CTA_KEY,
        'stpid': STOP_ID,
        'max': CTA_MAX,
        'outputType': 'JSON'
    }
    try:
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        data = {'error': str(e)}
    _cache = {'ts': time.time(), 'data': data}
    return data

def normalize_cta(cta_json):
    """Return list of simplified arrival dicts: { line, direction, eta }.
    We try to produce an ISO-like eta string parseable by Date.parse."""
    out = []
    if not isinstance(cta_json, dict):
        return out
    ctatt = cta_json.get('ctatt') or {}
    etas = ctatt.get('eta') or []
    # sometimes a single object
    if isinstance(etas, dict):
        etas = [etas]
    for item in etas:
        line = item.get('rt') or item.get('route') or item.get('rtnm') or ''
        direction = item.get('trDr') or item.get('dest') or ''
        arr = item.get('arrT') or item.get('prdt') or item.get('prdt') or None
        iso = None
        if arr:
            s = str(arr).strip()
            # CTA often returns "YYYYMMDD HH:MM:SS" or "YYYY-MM-DD HH:MM:SS"
            # Try to transform to "YYYY-MM-DDTHH:MM:SS"
            try:
                if len(s) >= 17 and s[4:6].isdigit() and s[6:8].isdigit() and ' ' in s:
                    # if format like 20140503 11:12:34
                    datepart, timepart = s.split(' ', 1)
                    if len(datepart) == 8 and datepart.isdigit():
                        y = datepart[0:4]; m = datepart[4:6]; d = datepart[6:8]
                        iso = f"{y}-{m}-{d}T{timepart}"
                    else:
                        iso = s.replace(' ', 'T')
                else:
                    iso = s.replace(' ', 'T')
            except Exception:
                iso = s
        out.append({'line': line, 'direction': direction, 'eta': iso, 'raw': item})
    return out

@app.route('/api/trains')
def api_trains():
    cta = fetch_cta()
    if 'error' in cta:
        return jsonify({'ok': False, 'error': cta['error']}), 500
    arrivals = normalize_cta(cta)
    return jsonify({'ok': True, 'fetched_at': int(time.time()), 'arrivals': arrivals})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # dev mode
    app.run(host='0.0.0.0', port=5000, threaded=True)
