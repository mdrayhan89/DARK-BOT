from flask import Flask, render_template, request, jsonify
import requests
import json
import traceback

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
        with_ss = data.get('with_ss', True) # Default True to force SS
        
        raw_pair = data.get('pair', 'EUR/USD')
        clean_pair = raw_pair.replace('/', '').replace(' ', '').upper()

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        # SS Enabled থাকলে আপনার নিজস্ব Chart API থেকে ইমেজ ফেচ করা হবে
        if with_ss:
            # 1. Primary endpoint (Apnar Chart API)
            chart_url = f"https://fx-real-data.onrender.com/chart-image?pair={raw_pair}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            img_bytes = None
            try:
                # 15 seconds timeout to allow chart rendering
                img_res = requests.get(chart_url, headers=headers, timeout=15)
                if img_res.status_code == 200 and len(img_res.content) > 1000:
                    img_bytes = img_res.content
            except Exception as err:
                print(f"Error fetching from chart API: {err}")

            # 2. Upload photo with text caption to Telegram API
            if img_bytes:
                tg_photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                files = {
                    'photo': (f'{clean_pair}_chart.png', img_bytes, 'image/png')
                }
                payload = {
                    'chat_id': chat_id,
                    'caption': text_msg
                }
                
                tg_res = requests.post(tg_photo_url, data=payload, files=files, timeout=20)
                res_data = tg_res.json()
                
                if res_data.get('ok'):
                    return jsonify({'success': True, 'mode': 'photo_with_caption_sent'})
                else:
                    print("Telegram API Photo Error:", res_data)

        # Fallback to text if image fetch fails
        tg_text_url = f"https://api.telegram.org/bot{token}/sendMessage"
        text_payload = {
            'chat_id': chat_id,
            'text': text_msg
        }
        requests.post(tg_text_url, json=text_payload, timeout=10)
        
        return jsonify({'success': True, 'mode': 'text_sent_fallback'})

    except Exception as e:
        print("Telegram Send Error:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
