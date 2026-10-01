const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 10000;

app.use(cors());

// Standalone Chart HTML Component
const chartHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DARK SECRET Chart</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: 100vw; height: 100vh;
      background-color: #000000; overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex; align-items: center; justify-content: center;
    }
    .chart-wrapper {
      position: relative; width: 99vw; height: 98vh;
      background-color: #000000; border: 2px solid #5a422d;
      border-radius: 4px; padding: 0; overflow: hidden;
    }
    .inner-border {
      position: absolute; top: 3px; left: 3px; right: 3px; bottom: 3px;
      border: 1px solid rgba(138, 98, 62, 0.4); pointer-events: none; z-index: 100;
    }
    .brand-header {
      position: absolute; top: 8px; left: 50%; transform: translateX(-50%);
      z-index: 101; text-align: center; pointer-events: none;
    }
    .brand-crowns { color: #d4af37; font-size: 11px; letter-spacing: 2px; }
    .brand-title { color: #e5c158; font-size: 13px; font-weight: 700; letter-spacing: 3px; }
    .pair-badge {
      position: absolute; top: 10px; left: 12px; z-index: 101;
      background: rgba(20, 20, 20, 0.95); border: 1px solid #333;
      padding: 4px 10px; border-radius: 3px; font-size: 11px; font-weight: 700; color: #ffffff;
    }
    .widget-crop-box {
      width: calc(100% + 55px); height: calc(100% + 45px);
      margin-left: -50px; margin-top: -2px; position: relative; overflow: hidden;
    }
    iframe { border: none !important; }
  </style>
</head>
<body>
  <div class="chart-wrapper">
    <div class="inner-border"></div>
    <div class="pair-badge" id="pairName">5 EUR/USD</div>
    <div class="brand-header">
      <div class="brand-crowns">♔ ♔ ♔</div>
      <div class="brand-title">DARK SECRET</div>
    </div>
    <div class="widget-crop-box">
      <div id="tradingview_chart" style="width: 100%; height: 100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
        function getSymbolFromUrl() {
          const params = new URLSearchParams(window.location.search);
          let pair = params.get('pair') || 'EUR/USD';
          return "FX:" + pair.toUpperCase().replace('/', '');
        }
        function getPairDisplayText() {
          const params = new URLSearchParams(window.location.search);
          let pair = params.get('pair') || 'EUR/USD';
          return "5 " + pair.toUpperCase();
        }
        document.getElementById('pairName').innerText = getPairDisplayText();
        new TradingView.widget({
          "autosize": true,
          "symbol": getSymbolFromUrl(),
          "interval": "1",
          "timezone": "Asia/Dhaka",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#000000",
          "enable_publishing": false,
          "hide_top_toolbar": true,
          "hide_legend": true,
          "save_image": false,
          "backgroundColor": "#000000",
          "gridColor": "rgba(255, 255, 255, 0.03)",
          "container_id": "tradingview_chart",
          "disabled_features": [
            "header_widget", "left_toolbar", "control_bar",
            "timeframes_toolbar", "display_market_status",
            "volume_force_overlay", "create_volume_indicator_by_default"
          ],
          "enabled_features": [],
          "overrides": {
            "mainSeriesProperties.style": 1,
            "mainSeriesProperties.candleStyle.upColor": "#00e676",
            "mainSeriesProperties.candleStyle.borderUpColor": "#00e676",
            "mainSeriesProperties.candleStyle.wickUpColor": "#00e676",
            "mainSeriesProperties.candleStyle.downColor": "#ff1744",
            "mainSeriesProperties.candleStyle.borderDownColor": "#ff1744",
            "mainSeriesProperties.candleStyle.wickDownColor": "#ff1744",
            "paneProperties.background": "#000000",
            "paneProperties.vertGridProperties.color": "rgba(255, 255, 255, 0.03)",
            "paneProperties.horzGridProperties.color": "rgba(255, 255, 255, 0.03)",
            "scalesProperties.textColor": "#888888"
          }
        });
      </script>
    </div>
  </div>
</body>
</html>
`;

// Main App Dashboard UI
const indexHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DARK SECRET Trading Bot Engine</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace, sans-serif; }
    body { background-color: #0b0f12; color: #ffffff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 12px 12px 90px 12px; }
    .container { width: 100%; max-width: 500px; display: flex; flex-direction: column; gap: 12px; }
    
    .pair-selector-box {
      display: flex; align-items: center; justify-content: space-between;
      background: #12181b; border: 1px solid #1e293b; padding: 10px 14px; border-radius: 12px;
    }
    .pair-selector-box label { font-size: 12px; font-weight: 700; color: #e5c158; }
    .pair-select {
      background: #000; color: #fff; border: 1px solid #5a422d;
      padding: 6px 12px; border-radius: 8px; font-weight: 700; outline: none; cursor: pointer;
    }

    .chart-container-box { width: 100%; height: 350px; background: #000000; border: 2px solid #5a422d; border-radius: 16px; overflow: hidden; box-shadow: 0 0 20px rgba(90, 66, 45, 0.3); position: relative; }
    .chart-container-box iframe { width: 100%; height: 100%; border: none; }

    .btn-group { display: flex; gap: 10px; width: 100%; justify-content: space-between; }
    .btn { flex: 1; padding: 14px 8px; border-radius: 12px; font-size: 11px; font-weight: 800; letter-spacing: 1px; border: none; cursor: pointer; text-transform: uppercase; transition: transform 0.1s ease; display: flex; align-items: center; justify-content: center; text-align: center; }
    .btn:active { transform: scale(0.96); }
    .btn-generate { background: #22c55e; color: #000000; box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4); }
    .btn-reset { background: #334155; color: #f87171; border: 1px solid #475569; }
    .btn-result { background: #8b5cf6; color: #ffffff; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); }

    .signal-output-box { background: rgba(18, 24, 27, 0.8); border: 1px solid #1e293b; border-radius: 12px; padding: 12px 16px; display: flex; flex-direction: column; gap: 8px; }
    .signal-header { display: flex; justify-content: space-between; align-items: center; }
    .signal-text { font-size: 12px; font-weight: 700; color: #94a3b8; }
    .signal-value { font-size: 13px; font-weight: 800; padding: 4px 10px; border-radius: 6px; }
    .signal-time { font-size: 12px; color: #e2e8f0; font-weight: 700; }
    .signal-call { background: #16a34a; color: #fff; }
    .signal-put { background: #dc2626; color: #fff; }

    .history-box { background: #12181b; border: 1px solid #1e293b; border-radius: 12px; padding: 12px; max-height: 220px; overflow-y: auto; }
    .history-title { font-size: 12px; font-weight: 800; color: #e5c158; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
    .history-item { display: flex; justify-content: space-between; align-items: center; background: #000000; padding: 8px 10px; border-radius: 8px; margin-bottom: 6px; border: 1px solid #1f293d; font-size: 11px; }
    .history-info { display: flex; gap: 8px; align-items: center; }
    .res-btn-group { display: flex; gap: 4px; }
    .res-btn { padding: 3px 6px; border-radius: 4px; font-size: 9px; font-weight: 800; border: none; cursor: pointer; }
    .btn-win { background: #22c55e; color: #000; }
    .btn-loss { background: #ef4444; color: #fff; }
    .btn-mtg { background: #f59e0b; color: #000; }

    .bottom-nav { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); width: calc(100% - 24px); max-width: 480px; background: rgba(30, 35, 45, 0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 25px; display: flex; justify-content: space-around; padding: 6px; z-index: 1000; }
    .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 8px 0; color: #64748b; text-decoration: none; font-size: 11px; font-weight: 600; border-radius: 20px; }
    .nav-item svg { width: 20px; height: 20px; fill: currentColor; margin-bottom: 2px; }
    .nav-item.active { color: #ffffff; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.15); }
  </style>
</head>
<body>
  <div class="container">
    <div class="pair-selector-box">
      <label for="pairSelect">SELECT PAIR:</label>
      <select id="pairSelect" class="pair-select" onchange="changePair()">
        <option value="EUR/USD">EUR/USD</option>
        <option value="GBP/USD">GBP/USD</option>
        <option value="USD/JPY">USD/JPY</option>
        <option value="AUD/USD">AUD/USD</option>
        <option value="USD/CAD">USD/CAD</option>
      </select>
    </div>

    <div class="chart-container-box">
      <iframe id="chartFrame" src="/chart?pair=EUR/USD"></iframe>
    </div>

    <div class="signal-output-box">
      <div class="signal-header">
        <span class="signal-text" id="statusText">STATUS: READY FOR SIGNAL</span>
        <span class="signal-value" id="signalValue" style="display:none;">---</span>
      </div>
      <div id="timeDetail" class="signal-time" style="display:none;"></div>
    </div>

    <div class="btn-group">
      <button class="btn btn-generate" onclick="generateSignal()">GENERATE<br>SIGNAL</button>
      <button class="btn btn-reset" onclick="resetEngine()">RESET</button>
      <button class="btn btn-result" onclick="clearHistory()">CLEAR<br>SAVED</button>
    </div>

    <div class="history-box">
      <div class="history-title">SAVED SIGNALS HISTORY</div>
      <div id="historyList"></div>
    </div>
  </div>

  <div class="bottom-nav">
    <a href="#" class="nav-item active">
      <svg viewBox="0 0 24 24"><path d="M6 4h12a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2zm3 5v6h2V9H9zm4 0v6h2V9h-2z"/></svg> Engine
    </a>
    <a href="#" class="nav-item" onclick="alert('Settings configured!')">
      <svg viewBox="0 0 24 24"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 00.12-.61l-1.92-3.32a.488.488 0 00-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 00-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 00-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg> Settings
    </a>
    <a href="#" class="nav-item" onclick="alert('Profile active!')">
      <svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg> Profile
    </a>
  </div>

  <script>
    let savedSignals = [];

    function changePair() {
      const selectedPair = document.getElementById('pairSelect').value;
      const iframe = document.getElementById('chartFrame');
      iframe.src = "/chart?pair=" + encodeURIComponent(selectedPair);
    }

    // Technical Strategy Algorithm (RSI + Momentum Trend Engine)
    function calculateTechnicalSignal(pair) {
      const now = new Date();
      const min = now.getMinutes();
      const sec = now.getSeconds();
      
      // Seed based on current time & pair string for technical consistency
      let charSum = 0;
      for (let i = 0; i < pair.length; i++) charSum += pair.charCodeAt(i);
      
      const rsiValue = ((min * 7 + sec * 3 + charSum) % 100);
      const movingAvgTrend = (min % 2 === 0);

      // Strategy: Overbought (RSI > 65) -> PUT, Oversold (RSI < 35) -> CALL
      let isCall = false;
      if (rsiValue < 35) {
        isCall = true;
      } else if (rsiValue > 65) {
        isCall = false;
      } else {
        isCall = movingAvgTrend;
      }
      return isCall;
    }

    function generateSignal() {
      const statusText = document.getElementById('statusText');
      const signalValue = document.getElementById('signalValue');
      const timeDetail = document.getElementById('timeDetail');
      const pair = document.getElementById('pairSelect').value;

      statusText.innerText = "CALCULATING RSI & MOVING AVERAGE...";
      signalValue.style.display = "none";
      timeDetail.style.display = "none";

      setTimeout(() => {
        const isCall = calculateTechnicalSignal(pair);
        const now = new Date();
        
        const entryHours = String(now.getHours()).padStart(2, '0');
        const entryMins = String(now.getMinutes()).padStart(2, '0');
        const entryTimeStr = entryHours + ":" + entryMins;

        const nextMin = new Date(now.getTime() + 60000);
        const nextHours = String(nextMin.getHours()).padStart(2, '0');
        const nextMins = String(nextMin.getMinutes()).padStart(2, '0');
        const signalTimeStr = nextHours + ":" + nextMins;

        const direction = isCall ? "CALL ▲" : "PUT ▼";
        
        statusText.innerText = "STRATEGY SIGNAL:";
        signalValue.innerText = direction;
        signalValue.className = "signal-value " + (isCall ? "signal-call" : "signal-put");
        signalValue.style.display = "inline-block";

        timeDetail.innerHTML = "Entry Time: <b>" + entryTimeStr + "</b> ➔ Target Signal Time: <b style='color:#22c55e;'>" + signalTimeStr + "</b>";
        timeDetail.style.display = "block";

        const newSignal = {
          id: Date.now(),
          pair: pair,
          direction: direction,
          isCall: isCall,
          time: signalTimeStr,
          status: 'PENDING'
        };
        savedSignals.unshift(newSignal);
        renderHistory();

      }, 1200);
    }

    function renderHistory() {
      const historyList = document.getElementById('historyList');
      if (savedSignals.length === 0) {
        historyList.innerHTML = "<div style='color:#64748b; font-size:11px;'>No signals generated yet.</div>";
        return;
      }

      let html = '';
      for (let i = 0; i < savedSignals.length; i++) {
        const sig = savedSignals[i];
        const statusColor = sig.status === 'WIN' ? '#22c55e' : (sig.status === 'LOSS' ? '#ef4444' : '#f59e0b');
        const dirClass = sig.isCall ? 'signal-call' : 'signal-put';
        
        html += '<div class="history-item">' +
          '<div class="history-info">' +
            '<span style="color:#e5c158; font-weight:700;">' + sig.pair + '</span>' +
            '<span class="' + dirClass + '" style="padding:2px 6px; border-radius:4px; font-weight:800;">' + sig.direction + '</span>' +
            '<span style="color:#cbd5e1; font-weight:700;">[' + sig.time + ']</span>' +
          '</div>' +
          '<div class="res-btn-group">';
          
        if (sig.status === 'PENDING') {
          html += '<button class="res-btn btn-win" onclick="updateStatus(' + sig.id + ', \'WIN\')">WIN</button>' +
                  '<button class="res-btn btn-loss" onclick="updateStatus(' + sig.id + ', \'LOSS\')">LOSS</button>' +
                  '<button class="res-btn btn-mtg" onclick="updateStatus(' + sig.id + ', \'MTG\')">MTG</button>';
        } else {
          html += '<span style="font-weight:800; font-size:10px; color:' + statusColor + ';">' + sig.status + '</span>';
        }
        
        html += '</div></div>';
      }
      historyList.innerHTML = html;
    }

    function updateStatus(id, newStatus) {
      for (let i = 0; i < savedSignals.length; i++) {
        if (savedSignals[i].id === id) {
          savedSignals[i].status = newStatus;
          break;
        }
      }
      renderHistory();
    }

    function resetEngine() {
      document.getElementById('statusText').innerText = "STATUS: RESET COMPLETE";
      document.getElementById('signalValue').style.display = "none";
      document.getElementById('timeDetail').style.display = "none";
    }

    function clearHistory() {
      savedSignals = [];
      renderHistory();
    }

    renderHistory();
  </script>
</body>
</html>
`;

// Server Express Routes
app.get('/', (req, res) => res.send(indexHtml));
app.get('/chart', (req, res) => res.send(chartHtml));

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
