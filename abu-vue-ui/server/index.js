import express from 'express';
import cors from 'cors';

const app = express();
const PORT = 3001;

// 启用CORS
app.use(cors());
// 解析JSON请求体
app.use(express.json());

// 模拟回测API
app.post('/api/loopback', (req, res) => {
  console.log('收到回测请求:', req.body);
  
  // 模拟回测结果
  const mockResult = {
    winRate: 0.65,
    totalProfit: 0.45,
    annualProfit: 0.225,
    sharpeRatio: 1.8,
    maxDrawdown: -0.08,
    tradesCount: 24
  };
  
  // 模拟异步处理
  setTimeout(() => {
    res.json(mockResult);
  }, 1000);
});

// 模拟股票信息API
app.get('/api/stock/:symbol', (req, res) => {
  const { symbol } = req.params;
  
  const mockStockInfo = {
    symbol: symbol,
    name: `${symbol} Company`,
    price: 150 + Math.random() * 50,
    change: (Math.random() - 0.5) * 10,
    changePercent: (Math.random() - 0.5) * 5,
    volume: Math.floor(Math.random() * 10000000),
    marketCap: Math.floor(Math.random() * 100000000000)
  };
  
  res.json(mockStockInfo);
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
});
