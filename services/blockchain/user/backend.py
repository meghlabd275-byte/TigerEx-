#!/usr/bin/env python3
"""Blockchain Service - Full Backend"""
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)
blocks, transactions, validators = {}, {}, {}

@app.route('/api/admin/health')
def admin_health(): return jsonify({"status": "ok"})
@app.route('/api/admin/stats')
def admin_stats(): return jsonify({"blocks": len(blocks), "txs": len(transactions), "validators": len(validators)})
@app.route('/api/user/health')
def user_health(): return jsonify({"status": "ok"})
@app.route('/api/user/send', methods=['POST'])
def send_tx():
    data = request.get_json()
    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
    transactions[tx_id] = {"tx_id": tx_id, "from": data.get('from'), "to": data.get('to'), "value": data.get('value'), "status": "pending"}
    return jsonify({"status": "pending", "tx_id": tx_id})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6500)