import json
import os
import random
import string
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, 'leads.json')

app = Flask(__name__)


def read_leads():
    try:
        with open(LEADS_FILE, encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def write_leads(leads):
    with open(LEADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
        f.write('\n')


def normalize_phone(value):
    return ''.join(c for c in str(value or '') if c.isdigit())


def is_valid_ua_phone(value):
    digits = normalize_phone(value)
    if len(digits) == 12 and digits.startswith('380'):
        return True
    if len(digits) == 10 and digits.startswith('0'):
        return True
    if len(digits) == 9:
        return True
    return False


def make_lead_id():
    ts = format(int(datetime.now(timezone.utc).timestamp() * 1000), 'x')
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return ts + suffix


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/src_img/<path:filename>')
def src_img(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'src_img'), filename)


@app.post('/api/leads')
def create_lead():
    data = request.get_json(silent=True) or {}
    phone = (data.get('phone') or '').strip()
    name = (data.get('name') or '').strip()
    source = (data.get('source') or 'unknown').strip()

    if not is_valid_ua_phone(phone):
        return jsonify(ok=False, error='invalid_phone'), 400

    lead = {
        'id': make_lead_id(),
        'phone': phone,
        'digits': normalize_phone(phone),
        'name': name or None,
        'source': source,
        'page': data.get('page'),
        'submittedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
    }

    leads = read_leads()
    leads.append(lead)
    write_leads(leads)

    return jsonify(ok=True, lead=lead)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
