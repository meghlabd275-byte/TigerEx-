from flask import Flask, jsonify, request
app = Flask(__name__)
@app.route('/api/admin/health') 
def health(): return jsonify({"status": "ok", "service": "custom-exchange"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6400)
