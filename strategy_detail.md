# 策略详细实现说明

## 一、选股方式

该策略实际上是**择时策略**，而非传统意义上的选股策略。它的选股逻辑是：

1. **股票池选择**：在给定的股票池中（如示例中的8只美股：usNOAH, usSFUN, usBIDU, usAAPL, usGOOG, usTSLA, usWUBA, usVIPS）进行操作
2. **无明确选股逻辑**：不对股票进行基本面或技术面的筛选，而是对股票池中的所有股票应用相同的择时策略
3. **择时替代选股**：通过择时因子来决定何时买入和卖出，而非选择特定的股票

## 二、买入操作实现

### 1. 买入因子：AbuFactorBuyBreak

该策略使用42日和60日突破因子作为买入信号，具体实现逻辑：

```python
# 当股票收盘价达到过去xd天的最高价格时，触发买入信号
def fit_day(self, today):
    # 忽略统计周期内前xd天的数据
    if self.today_ind < self.xd - 1:
        return None
    
    # 今天的收盘价格达到xd天内最高价格则符合买入条件
    if today.close == self.kl_pd.close[self.today_ind - self.xd + 1:self.today_ind + 1].max():
        # 跳过相应天数的交易，避免频繁交易
        self.skip_days = self.xd
        # 生成买入订单，次日执行买入
        return self.buy_tomorrow()
    return None
```

### 2. 买入信号触发条件

- 当股票收盘价达到过去42日的最高价格时，触发买入信号
- 当股票收盘价达到过去60日的最高价格时，触发买入信号
- 两个因子并行生效，只要满足其中一个条件就会触发买入

### 3. 买入执行流程

1. 当日收盘后，检查是否满足突破条件
2. 如果满足条件，生成买入订单
3. 次日开盘时执行买入操作
4. 买入后跳过相应天数的交易（42日或60日），避免频繁交易

## 三、卖出操作实现

### 1. 卖出因子：AbuFactorCloseAtrNStop

该策略只使用盈利保护止盈因子作为卖出信号，具体实现逻辑：

```python
def fit_day(self, today, orders):
    for order in orders:
        # 计算买入后的最大收益价格
        max_close = self.kl_pd.iloc[start_ind:end_ind, :].close.max()
        
        # 止盈条件：
        # 1. 有一定盈利：最大收益价格 - 买入价格 > 今日ATR21
        # 2. 盈利回吐：最大收益价格 - 今日收盘价 > 今日ATR21 * close_atr_n
        if (max_close - order.buy_price) * order.expect_direction > today['atr21'] \
                and (max_close - today.close) * order.expect_direction > today['atr21'] * self.close_atr_n:
            # 生成卖出订单，次日执行卖出
            self.sell_tomorrow(order)
```

### 2. 卖出信号触发条件

该因子是一个**利润保护止盈因子**，当满足以下两个条件时触发卖出信号：

1. **有一定盈利**：买入后股票曾达到一定的盈利水平
   ```
   最大收益价格 - 买入价格 > 今日ATR21
   ```

2. **盈利开始回吐**：当前价格较最高点回落超过一定幅度
   ```
   最大收益价格 - 今日收盘价 > 今日ATR21 * close_atr_n
   ```
   其中，`close_atr_n` 默认值为1.5

### 3. 卖出执行流程

1. 对每个持仓订单，计算从买入日到今日的最大收益价格
2. 检查是否满足盈利保护止盈条件
3. 如果满足条件，生成卖出订单
4. 次日开盘时执行卖出操作

## 四、策略特点

### 1. 无明确止损机制

该策略没有设置明确的止损因子，而是依靠盈利保护止盈来控制风险。这种设计的特点是：
- 允许股票在小幅亏损时继续持有，等待反弹
- 当盈利回吐超过一定幅度时才卖出，保护已有利润
- 可能导致个别股票长期亏损持有

### 2. 多因子并行

买入端使用两个突破因子并行：
- 42日突破因子：捕捉中期趋势
- 60日突破因子：捕捉长期趋势

这种设计可以：
- 增加买入机会
- 捕捉不同时间周期的趋势
- 提高策略的适应性

### 3. 自适应调整

卖出因子使用ATR（平均真实波幅）作为调整依据：
- ATR会根据市场波动自动调整
- 市场波动大时，止盈阈值自动扩大
- 市场波动小时，止盈阈值自动缩小

这种设计可以：
- 适应不同市场环境
- 避免在波动大时过早止盈
- 避免在波动小时过晚止盈

## 五、策略实现代码示例

```python
from abupy import AbuFactorBuyBreak, AbuFactorCloseAtrNStop
from abupy import abu

# 设置初始资金
read_cash = 1000000

# 择时股票池
choice_symbols = ['usNOAH', 'usSFUN', 'usBIDU', 'usAAPL', 'usGOOG',
                  'usTSLA', 'usWUBA', 'usVIPS']

# 买入因子：42日和60日突破因子
buy_factors = [{'xd': 42, 'class': AbuFactorBuyBreak},
               {'xd': 60, 'class': AbuFactorBuyBreak}]

# 卖出因子：盈利保护止盈因子
# 注意：这里只使用了一个卖出因子，没有止损因子
sell_factors = [
    {'class': AbuFactorCloseAtrNStop, 'close_atr_n': 1.5}
]

# 执行回测
abu_result_tuple, kl_pd_manager = abu.run_loop_back(read_cash,
                                                   buy_factors,
                                                   sell_factors,
                                                   stock_pickers=None,
                                                   choice_symbols=choice_symbols,
                                                   n_folds=2)
```

## 六、风险提示

1. **没有明确止损**：可能导致个别股票长期亏损持有，影响整体收益
2. **过度依赖历史数据**：策略基于历史数据回测，未来市场环境变化可能导致策略失效
3. **参数敏感性**：策略表现对参数（如42日、60日、close_atr_n等）较为敏感
4. **股票池限制**：策略表现受股票池质量影响较大

## 七、优化建议

1. **添加止损机制**：可以考虑添加止损因子，如AbuFactorAtrNStop，控制单个股票的最大亏损
2. **动态调整参数**：根据市场环境动态调整突破周期和止盈参数
3. **结合选股策略**：可以考虑添加选股因子，筛选优质股票后再应用择时策略
4. **多策略组合**：可以考虑结合多种策略，分散风险

## 总结

该策略是一个**趋势跟踪策略**，通过突破因子捕捉上升趋势，通过盈利保护止盈因子保护已有利润。它的特点是：
- 收益率较高，年化收益可达24.88%
- 胜率较高，可达82.35%
- 没有明确的止损机制
- 依赖历史数据和参数设置

投资者在使用该策略时，应注意控制风险，适当优化参数，并结合自身的风险偏好进行调整。