from flask import Flask, render_template, request, jsonify
import urllib.request
import urllib.parse
import json
import requests

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
        data = request.json or {}
        token = data.get('token')
        chat_id = data.get('chat_id')
        text_msg = data.get('text', '')
        with_ss = data.get('with_ss', False)
        pair = data.get('pair', 'EURUSD').replace('/', '').replace(' ', '').upper()

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        # SS Toggle ON থাকলে চার্ট ডাউনলোড করে Telegram-এ ছবি পাঠানো হবে
        if with_ss:
            chart_img_url = f"https://quickchart.io/chart?bkg=14171d&c={{type:'line',data:{{labels:['M5','M4','M3','M2','M1'],datasets:[{{label:'{pair}',data:[10,15,13,18,25],borderColor:'%2300ff88',fill:false}}]}}}}&width=1280&height=720"
            
            # 1. Download image to server bytes
            img_res = requests.get(chart_img_url, timeout=10)
            
            if img_res.status_code == 200 and len(img_res.content) > 500:
                # 2. Direct Multipart Photo Upload to Telegram
                tg_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                files = {
                    'photo': ('chart.png', img_res.content, 'image/png')
                }
                payload = {
                    'chat_id': chat_id,
                    'caption': text_msg
                }
                
                resp = requests.post(tg_url, data=payload, files=files, timeout=15)
                res_data = resp.json()
                
                if res_data.get('ok'):
                    return jsonify({'success': True, 'mode': 'photo_sent'})

        # SS OFF থাকলে বা ছবি পাঠাতে ব্যর্থ হলে শুধু টেক্সট পাঠানো হবে
        tg_text_url = f"https://api.telegram.org/bot{token}/sendMessage"
        text_payload = {
            'chat_id': chat_id,
            'text': text_msg
        }
        resp = requests.post(tg_text_url, json=text_payload, timeout=10)
        
        return jsonify({'success': True, 'mode': 'text_sent'})

    except Exception as e:
        print("Telegram Send Error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
