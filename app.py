from flask import Flask, render_template, request, jsonify
import requests
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
        with_ss = data.get('with_ss', True)
        
        raw_pair = data.get('pair', 'EUR/USD')
        clean_pair = raw_pair.replace('/', '').replace(' ', '').upper()

        if not token or not chat_id:
            return jsonify({'success': False, 'error': 'Missing Token or Chat ID'}), 400

        img_bytes = None

        if with_ss:
            # Apnar Sothik Chart Endpoint URL
            correct_chart_url = f"https://fx-real-data.onrender.com/chart?pair={raw_pair}"
            
            # Webshot / Screenshot rendering API or direct fetch
            # Note: Chart url jodi HTML hoy, tobon Screenshot API call kora lagbe
            screenshot_api_url = f"https://api.screenshotmachine.com?key=FREE_OR_YOUR_KEY&url={correct_chart_url}&dimension=1024x768"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            try:
                print(f"Fetching chart from: {correct_chart_url}")
                res = requests.get(correct_chart_url, headers=headers, timeout=12)
                
                # Check if returned response is direct image
                if res.status_code == 200 and 'image' in res.headers.get('Content-Type', ''):
                    img_bytes = res.content
                else:
                    # If /chart returns HTML page instead of raw image bytes
                    print("URL returned HTML, using Screenshot fallback...")
                    # Screenshot machine or html2image endpoint
                    ss_res = requests.get(screenshot_api_url, timeout=15)
                    if ss_res.status_code == 200:
                        img_bytes = ss_res.content

            except Exception as fetch_err:
                print(f"Fetch Error: {fetch_err}")

        # Telegram-e photo soh signal pathano
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
                return jsonify({'success': True, 'mode': 'photo_sent'})

        # Image capture na hole fallback text send
        tg_text_url = f"https://api.telegram.org/bot{token}/sendMessage"
        text_payload = {'chat_id': chat_id, 'text': text_msg}
        requests.post(tg_text_url, json=text_payload, timeout=10)
        
        return jsonify({'success': True, 'mode': 'text_sent_fallback'})

    except Exception as e:
        print("Telegram Send Error:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
