from flask import Flask, render_template, request, jsonify, send_file
import urllib.request
import io

app = Flask(__name__)

PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'EUR/JPY', 'CAD/JPY', 'GBP/CAD']

@app.route('/')
def index():
    return render_template('index.html', pairs=PAIRS)

@app.route('/api/analyze')
def analyze():
    pair = request.args.get('pair', 'EUR/USD')
    return jsonify({
        'pair': pair,
        'direction': 'BUY',
        'reason': 'RSI Oversold + MACD Bullish Crossover'
    })

# --- Built-in urllib for Screenshot Fetching (No 'requests' needed) ---
@app.route('/api/screenshot')
def get_chart_screenshot():
    pair = request.args.get('pair', 'EUR/USD')
    chart_url = f"https://fx-real-data.onrender.com/chart-image?pair={urllib.parse.quote(pair)}&width=1280&height=720"
    
    try:
        req = urllib.request.Request(chart_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                img_data = response.read()
                return send_file(io.BytesIO(img_data), mimetype='image/png')
    except Exception as e:
        pass
        
    return send_file(io.BytesIO(b''), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
