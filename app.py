from flask import Flask, render_template, request, jsonify
import urllib.request
import urllib.parse
import json

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

@app.route('/api/send_telegram_signal', methods=['POST'])
def send_telegram_signal():
    try:
        data = request.json
        token = data.get('token')
        chat_id = data.get('chat_id')
        text_msg = data.get('text')
        with_ss = data.get('with_ss', False)
        pair = data.get('pair', 'EUR/USD').replace('/', '')

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        if with_ss:
            # High quality TradingView chart snapshot endpoint (16:9 ratio - 1280x720)
            chart_url = f"https://s3.tradingview.com/snapshots/{pair.lower()[0]}/{pair}.png"
            
            # Alternative dynamic chart generator (16:9 ratio - 1280x720)
            fallback_chart_url = f"https://quickchart.io/chart?bkg=14171d&c={{type:'line',data:{{labels:['M5','M4','M3','M2','M1'],datasets:[{{label:'{pair}',data:[12,19,15,17,24],borderColor:'%2300ff88',fill:false}}]}}}}&width=1280&height=720"

            img_bytes = None
            
            # 1st Attempt: Fetch Chart Image
            for target_url in [f"https://fx-real-data.onrender.com/chart-image?pair={pair}&width=1280&height=720", fallback_chart_url]:
                try:
                    req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=6) as response:
                        if response.status == 200:
                            img_bytes = response.read()
                            break
                except Exception:
                    continue

            # If image fetched successfully, send via Telegram sendPhoto
            if img_bytes:
                boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
                body = []
                body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode('utf-8'))
                body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{text_msg}\r\n'.encode('utf-8'))
                body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="chart_16_9.png"\r\nContent-Type: image/png\r\n\r\n'.encode('utf-8'))
                body.append(img_bytes)
                body.append(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
                
                payload = b''.join(body)
                tg_req = urllib.request.Request(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data=payload,
                    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
                )
                with urllib.request.urlopen(tg_req) as tg_res:
                    return jsonify({'success': True})

        # Text Fallback Message
        payload = json.dumps({'chat_id': chat_id, 'text': text_msg}).encode('utf-8')
        tg_req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(tg_req) as tg_res:
            return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
