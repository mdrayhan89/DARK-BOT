from flask import Flask, render_template, request, jsonify, send_file
import urllib.request
import urllib.parse
import json
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

# Telegram-এ Signal এবং Screenshot পাঠানোর জন্য Secure Backend Endpoint
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

        if with_ss:
            # 16:9 High Resolution Chart Snapshot URL
            chart_url = f"https://fx-real-data.onrender.com/chart-image?pair={urllib.parse.quote(pair)}&width=1280&height=720"
            try:
                # Screenshot Fetch
                req = urllib.request.Request(chart_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=8) as response:
                    img_bytes = response.read()

                # Telegram SendPhoto API multipart construct
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
            except Exception as e:
                # Fallback to Text Message if Screenshot Fetch fails
                pass

        # Text Message Only
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
