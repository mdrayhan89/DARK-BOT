from flask import Flask, render_template, request, jsonify
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

        # SS Toggle ON থাকলে সরাসরি আপনার Chart API থেকে স্ক্রিনশট টেনে নেওয়া হবে
        if with_ss:
            # Apnar Nijer Chart Image API Endpoint
            my_chart_api_url = f"https://fx-real-data.onrender.com/chart-image?pair={pair}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            try:
                # Fetching image from your API
                img_res = requests.get(my_chart_api_url, headers=headers, timeout=12)
                
                if img_res.status_code == 200 and len(img_res.content) > 500:
                    tg_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    files = {
                        'photo': (f'{pair}_chart.png', img_res.content, 'image/png')
                    }
                    payload = {
                        'chat_id': chat_id,
                        'caption': text_msg
                    }
                    
                    resp = requests.post(tg_url, data=payload, files=files, timeout=15)
                    res_data = resp.json()
                    
                    if res_data.get('ok'):
                        return jsonify({'success': True, 'mode': 'photo_sent'})
                else:
                    print(f"Chart API Failed with status: {img_res.status_code}")
            except Exception as ss_err:
                print("Failed to fetch image from personal API:", str(ss_err))

        # SS OFF থাকলে বা আপনার API ইমেজ রেন্ডার করতে ব্যর্থ হলে শুধু টেক্সট মেসেজ যাবে
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
