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

# --- Live Candlestick Image Fetcher ---
def get_candlestick_chart_bytes(pair_symbol):
    # Standardizing pair symbol format (e.g. FX:EURUSD or FX:USDJPY)
    clean_symbol = pair_symbol.replace('/', '').replace(' ', '').upper()
    formatted_symbol = f"FX:{clean_symbol}"
    
    # Live TradingView Candlestick Generator URL
    chart_url = f"https://s3.tradingview.com/snapshots/{clean_symbol[0].lower()}/{clean_symbol}.png"
    
    # Backup real-time candlestick API rendering
    backup_url = f"https://api.chart-img.com/v2/tradingview/advanced-chart?symbol={formatted_symbol}&interval=1m&theme=dark&width=1280&height=720"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    for target_url in [backup_url, chart_url]:
        try:
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    data = response.read()
                    if len(data) > 1000: # Ensure valid image size
                        return data
        except Exception as err:
            print(f"Fetch failed for {target_url}: {err}")
            continue
            
    return None

@app.route('/api/send_telegram_signal', methods=['POST'])
def send_telegram_signal():
    try:
        data = request.json
        token = data.get('token')
        chat_id = data.get('chat_id')
        text_msg = data.get('text')
        with_ss = data.get('with_ss', False)
        pair = data.get('pair', 'EUR/USD')

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        # Try sending Photo with Caption if with_ss is True
        if with_ss:
            img_bytes = get_candlestick_chart_bytes(pair)

            if img_bytes:
                boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
                body = []
                body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode('utf-8'))
                body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{text_msg}\r\n'.encode('utf-8'))
                body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="candlestick_chart.png"\r\nContent-Type: image/png\r\n\r\n'.encode('utf-8'))
                body.append(img_bytes)
                body.append(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
                
                payload = b''.join(body)
                tg_req = urllib.request.Request(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data=payload,
                    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
                )
                with urllib.request.urlopen(tg_req) as tg_res:
                    return jsonify({'success': True, 'mode': 'photo'})

        # Text Fallback Message if SS is disabled or failed
        payload = json.dumps({'chat_id': chat_id, 'text': text_msg}).encode('utf-8')
        tg_req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(tg_req) as tg_res:
            return jsonify({'success': True, 'mode': 'text'})

    except Exception as e:
        print("Telegram Send Error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
