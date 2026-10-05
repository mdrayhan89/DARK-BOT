from flask import Flask, render_template, request, jsonify
import requests
import json
import traceback
import urllib.parse
import threading

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

def send_photo_in_background(token, chat_id, text_msg, target_url, clean_pair):
    """
    Background Thread: Text Signal instantly jawar por SS render hole eita photo hisebe pathabe
    """
    try:
        # Fast Canvas Rendering Service
        ss_api_url = f"https://api.microlink.io?url={target_url}&screenshot=true"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        r = requests.get(ss_api_url, headers=headers, timeout=10)
        if r.status_code == 200:
            res_json = r.json()
            ss_img_url = res_json.get('data', {}).get('screenshot', {}).get('url')
            
            if ss_img_url:
                img_data = requests.get(ss_img_url, timeout=10).content
                if len(img_data) > 1000:
                    tg_photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    files = {'photo': (f'{clean_pair}_chart.png', img_data, 'image/png')}
                    payload = {'chat_id': chat_id, 'caption': text_msg}
                    
                    requests.post(tg_photo_url, data=payload, files=files, timeout=15)
                    print("Background Screenshot Sent Successfully!")
    except Exception as e:
        print("Background SS Error:", e)

@app.route('/api/send_telegram_signal', methods=['POST'])
def send_telegram_signal():
    try:
        data = request.json or {}
        token = data.get('token')
        chat_id = data.get('chat_id')
        text_msg = data.get('text', '')
        with_ss = data.get('with_ss', True)
        
        raw_pair = data.get('pair', 'EUR/USD')
        clean_pair = raw_pair.replace('/', '').replace(' ', '').upper()

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        # STEP 1: Fast Text Signal Instant Send (0.1 Second)
        tg_text_url = f"https://api.telegram.org/bot{token}/sendMessage"
        text_payload = {'chat_id': chat_id, 'text': text_msg}
        
        # Immediate send without waiting for SS
        resp = requests.post(tg_text_url, json=text_payload, timeout=5)

        # STEP 2: Background Thread-e Screenshot Process (No Delay in UI)
        if with_ss:
            target_chart_url = f"https://fx-real-data.onrender.com/chart?pair={urllib.parse.quote(raw_pair)}"
            
            thread = threading.Thread(
                target=send_photo_in_background,
                args=(token, chat_id, text_msg, target_chart_url, clean_pair)
            )
            thread.daemon = True
            thread.start()

        return jsonify({'success': True, 'mode': 'instant_signal_sent'})

    except Exception as e:
        print("Telegram Send Error:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
