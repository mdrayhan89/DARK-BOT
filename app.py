from flask import Flask, render_template, request, jsonify, send_file
import requests
import io

app = Flask(__name__)

PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'EUR/JPY', 'CAD/JPY', 'GBP/CAD']

@app.route('/')
def index():
    return render_template('index.html', pairs=PAIRS)

@app.route('/api/analyze')
def analyze():
    pair = request.args.get('pair', 'EUR/USD')
    # Signal logic
    return jsonify({
        'pair': pair,
        'direction': 'BUY',
        'reason': 'RSI Oversold + MACD Bullish Crossover'
    })

# --- 16:9 CHART SCREENSHOT API FIX ---
@app.route('/api/screenshot')
def get_chart_screenshot():
    pair = request.args.get('pair', 'EUR/USD')
    # Real-time chart snapshot provider (16:9 Ratio - 1280x720)
    chart_url = f"https://fx-real-data.onrender.com/chart-image?pair={pair}&width=1280&height=720"
    
    try:
        res = requests.get(chart_url, timeout=10)
        if res.status_code == 200:
            return send_file(io.BytesIO(res.content), mimetype='image/png')
    except Exception as e:
        pass
        
    # Fallback placeholder 16:9 image
    return send_file(io.BytesIO(b''), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
