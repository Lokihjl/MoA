#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试回测功能是否生成真实的交易记录
"""

import requests
import json

def test_backtest():
    """测试回测API是否生成真实交易记录"""
    url = "http://localhost:3001/api/moA/loopback"
    
    # 测试参数 - 使用A股股票sh601118（中国国航）
    params = {
        "initialCash": 1000000,
        "nFolds": 2,
        "symbols": ["sh601118"]
    }
    
    try:
        print("正在调用回测API...")
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        result = response.json()
        print("回测结果:")
        print(f"胜率: {result.get('winRate', 0):.2%}")
        print(f"总收益: {result.get('totalProfit', 0):.2%}")
        print(f"年化收益: {result.get('annualProfit', 0):.2%}")
        print(f"夏普比率: {result.get('sharpeRatio', 0):.2f}")
        print(f"最大回撤: {result.get('maxDrawdown', 0):.2%}")
        print(f"交易次数: {result.get('tradesCount', 0)}")
        print(f"数据源: {result.get('dataSource', '未知')}")
        
        # 检查交易记录
        trade_records = result.get('tradeRecords', [])
        print(f"\n交易记录数量: {len(trade_records)}")
        
        if trade_records:
            print("\n交易记录详情:")
            print("ID | 股票代码 | 买入日期 | 卖出日期 | 买入价格 | 卖出价格 | 数量 | 盈利 | 持有天数 | 盈利率")
            print("---|---------|---------|---------|---------|---------|------|------|---------|--------")
            for record in trade_records[:5]:  # 只显示前5条
                print(f"{record['id']:2d} | {record['symbol']} | {record['buy_date']} | {record['sell_date']} | {record['buy_price']:.2f} | {record['sell_price']:.2f} | {record['quantity']} | {record['profit']:.2f} | {record['hold_days']} | {record['profit_rate']:.2f}%")
            
            if len(trade_records) > 5:
                print(f"... 还有 {len(trade_records) - 5} 条记录")
            
            # 验证价格是否在真实范围内（sh601118的价格应该在5-6元左右）
            prices = []
            for record in trade_records:
                prices.append(record['buy_price'])
                prices.append(record['sell_price'])
            
            avg_price = sum(prices) / len(prices) if prices else 0
            print(f"\n平均交易价格: {avg_price:.2f} 元")
            
            if 4 <= avg_price <= 7:
                print("✅ 价格验证通过: 交易价格在真实范围内")
            else:
                print(f"❌ 价格验证失败: 交易价格 {avg_price:.2f} 元不在预期范围内 (4-7元)")
        else:
            print("❌ 没有生成交易记录")
            
        return result
        
    except requests.RequestException as e:
        print(f"❌ 回测API调用失败: {e}")
        return None

if __name__ == "__main__":
    test_backtest()