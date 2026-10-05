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
        pair = data.get('pair', 'EUR/USD').replace('/', '').replace(' ', '').upper()

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        # SS Toggle ON থাকলে সরাসরি Photo URL দিয়ে Telegram-এ পাঠানো হবে
        if with_ss:
            # Live Candlestick Generator Image URL
            chart_img_url = f"https://api.chart-img.com/v2/tradingview/advanced-chart?symbol=FX:{pair}&interval=1m&theme=dark&width=1280&height=720"
            
            photo_payload = json.dumps({
                'chat_id': chat_id,
                'photo': chart_img_url,
                'caption': text_msg
            }).encode('utf-8')

            try:
                tg_req = urllib.request.Request(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data=photo_payload,
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(tg_req, timeout=10) as tg_res:
                    res_data = json.loads(tg_res.read().decode())
                    if res_data.get('ok'):
                        return jsonify({'success': True, 'mode': 'photo_url'})
            except Exception as photo_err:
                print("Photo Send Failed, falling back to text:", str(photo_err))

        # SS OFF থাকলে বা ছবি পাঠাতে ব্যর্থ হলে শুধু টেক্সট পাঠাবে
        payload = json.dumps({'chat_id': chat_id, 'text': text_msg}).encode('utf-8')
        tg_req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(tg_req, timeout=10) as tg_res:
            return jsonify({'success': True, 'mode': 'text_only'})

    except Exception as e:
        print("Telegram Send Error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
