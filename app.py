from flask import Flask, render_template

app = Flask(__name__)

# Apnar sob binary pairs list
PAIRS = [
    "EUR/USD", "USD/JPY", "CAD/JPY", "AUD/CAD", "GBP/USD", 
    "EUR/JPY", "AUD/JPY", "AUD/USD", "EUR/GBP", "AUD/CHF", 
    "EUR/CAD", "GBP/CAD"
]

@app.route('/')
def index():
    return render_template('index.html', pairs=PAIRS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
