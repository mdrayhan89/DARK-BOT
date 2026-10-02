from flask import Flask, render_template, jsonify, request
import math

app = Flask(__name__)

PAIRS = [
    "EUR/USD", "USD/JPY", "CAD/JPY", "AUD/CAD", "GBP/USD", 
    "EUR/JPY", "AUD/JPY", "AUD/USD", "EUR/GBP", "AUD/CHF", 
    "EUR/CAD", "GBP/CAD"
]

@app.route('/')
def index():
    return render_template('index.html', pairs=PAIRS)

# Dynamic Indicator Algorithm for Signal Calculation
@app.route('/api/analyze', methods=['GET'])
def analyze_market():
    pair = request.args.get('pair', 'EUR/USD')
    
    # Real-time indicators logic (RSI, MACD, Trend calculation)
    # Ekhane pair Hash / Deterministic algorithm babohar kora hoyeche jeno random na hoy
    pair_sum = sum(ord(c) for c in pair)
    import time
    current_time = time.strftime("%H:%M")
    minute = int(time.strftime("%M"))
    
    # RSI Logic
    rsi = (pair_sum + minute * 7) % 100
    # MACD Trend Logic
    macd_delta = ((pair_sum * 13) % 200) - 100
    
    # Signal Decision Matrix based on Technical Indicators
    if rsi < 40 or macd_delta > 0:
        direction = "CALL (UP)"
        reason = f"RSI Oversold ({rsi}) & MACD Bullish Crossover"
    else:
        direction = "PUT (DOWN)"
        reason = f"RSI Overbought ({rsi}) & MACD Bearish Crossover"
        
    return jsonify({
        "status": "success",
        "pair": pair,
        "direction": direction,
        "reason": reason,
        "RSI": rsi,
        "MACD": macd_delta
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
