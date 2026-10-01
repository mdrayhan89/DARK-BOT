const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 10000;

const publicDir = path.join(__dirname, 'public');

app.use(cors());
app.use(express.static(publicDir));

// Serve Main UI
app.get('/', (req, res) => {
  const indexPath = path.join(publicDir, 'index.html');
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).send('index.html not found! Please check public folder in GitHub repo.');
  }
});

// Serve Chart Standalone
app.get('/chart', (req, res) => {
  const chartPath = path.join(publicDir, 'chart.html');
  if (fs.existsSync(chartPath)) {
    res.sendFile(chartPath);
  } else {
    res.status(404).send('chart.html not found! Please check public folder in GitHub repo.');
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
