from flask import Flask, render_template, request, jsonify
import requests
import json
import traceback
import urllib.parse
import concurrent.futures

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

def fetch_chart_image_fast(target_url, clean_pair):
    """
    খুব দ্রুত (১-২ সেকেন্ডে) স্ক্রিনশট রিটার্ন করার জন্য ফাস্ট সার্ভিসসমূহ
    """
    fast_ss_urls = [
        f"https://screenshot.abstractapi.com/v1/?api_key=sample&url={target_url}&width=1000&height=600",
        f"https://api.microlink.io?url={target_url}&screenshot=true&meta=false&embed=screenshot.url",
        f"https://shot.screenshotapi.net/screenshot?url={target_url}&width=1000&height=600&output=image"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # microlink instant screenshot extractor
    try:
        micro_url = f"https://api.microlink.io?url={target_url}&screenshot=true"
        r = requests.get(micro_url, headers=headers, timeout=3.5)
        if r.status_code == 200:
            res_json = r.json()
            ss_img_url = res_json.get('data', {}).get('screenshot', {}).get('url')
            if ss_img_url:
                img_data = requests.get(ss_img_url, timeout=3).content
                if len(img_data) > 1000:
                    return img_data
    except Exception as e:
        print("Microlink SS Error:", e)

    # Backup Fast Direct Fetch
    for ss_endpoint in fast_ss_urls:
        try:
            res = requests.get(ss_endpoint, headers=headers, timeout=3)
            if res.status_code == 200 and len(res.content) > 2000:
                return res.content
        except Exception:
            continue

    return None

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

        target_chart_url = f"https://fx-real-data.onrender.com/chart?pair={urllib.parse.quote(raw_pair)}"
        
        img_bytes = None

        if with_ss:
            # Parallel Threading দিয়ে ১-২ সেকেন্ডে SS ফেচ করা হবে
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(fetch_chart_image_fast, target_chart_url, clean_pair)
                try:
                    img_bytes = future.result(timeout=4.0) # ৪ সেকেন্ডের বেশি ওয়েট করবে না
                except concurrent.futures.TimeoutError:
                    print("SS Fetching Timed out! Sending fast signal.")

        # ১. SS পাওয়া গেলে ফটো সহ টেলিগ্রামে সিগন্যাল যাবে
        if img_bytes:
            tg_photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
            files = {
                'photo': (f'{clean_pair}_chart.png', img_bytes, 'image/png')
            }
            payload = {
                'chat_id': chat_id,
                'caption': text_msg
            }
            
            tg_res = requests.post(tg_photo_url, data=payload, files=files, timeout=5)
            res_data = tg_res.json()
            
            if res_data.get('ok'):
                return jsonify({'success': True, 'mode': 'photo_sent_instantly'})

        # ২. SS দ্রুত না আসলে ১ সেকেন্ডে টেক্সট সিগন্যাল সেন্ড হবে (No Delay)
        tg_text_url = f"https://api.telegram.org/bot{token}/sendMessage"
        text_payload = {'chat_id': chat_id, 'text': text_msg}
        requests.post(tg_text_url, json=text_payload, timeout=5)
        
        return jsonify({'success': True, 'mode': 'fast_text_sent'})

    except Exception as e:
        print("Telegram Send Error:")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
