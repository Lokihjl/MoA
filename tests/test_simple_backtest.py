# -*- encoding:utf-8 -*-
"""
测试ABu回测功能的简单脚本
"""

from __future__ import print_function

# 导入日志模块
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_backtest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ABuBacktestTest')

# 导入ABu相关模块
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketSourceType
from abupy.MarketBu import ABuSymbolPd
from abupy.FactorBuyBu import AbuFactorBuyBreak
from abupy.FactorSellBu import AbuFactorAtrNStop
from abupy import AbuCapital, AbuKLManager, AbuMetricsBase
from abupy.TradeBu.ABuBenchmark import AbuBenchmark

# 设置数据源为腾讯财经
logger.info("正在配置数据源...")
ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
logger.info(f"数据源已设置为: {ABuEnv.g_market_source}")

def test_backtest():
    """执行回测测试"""
    try:
        # 获取股票数据
        logger.info("获取股票数据...")
        symbol = "sh000003"  # 使用数据库中实际存在的股票代码
        kl_pd = ABuSymbolPd.make_kl_df(symbol, start="2024-06-26", end="2025-12-23")  # 使用数据库中实际存在的时间范围
    
        if kl_pd is None or kl_pd.empty:
            logger.error("获取股票数据失败")
            return
    
        logger.info(f"股票数据形状: {kl_pd.shape}")
        logger.info(f"股票数据列名: {kl_pd.columns.tolist()}")
        logger.debug(f"前5行数据:\n{kl_pd.head()}")
    
        # 预处理数据，添加必要的列和属性
        logger.info("\n预处理数据...")
        # 为kl_pd设置name属性
        kl_pd.name = symbol
    
        # 添加date_week列（星期几，0=星期一，4=星期五）
        kl_pd['date_week'] = kl_pd.index.weekday
    
        # 添加date_month列（月份）
        kl_pd['date_month'] = kl_pd.index.month
    
        logger.info(f"预处理后数据形状: {kl_pd.shape}")
        logger.info(f"预处理后数据列名: {kl_pd.columns.tolist()}")
        logger.info(f"是否包含date_week列: {'date_week' in kl_pd.columns}")
        logger.info(f"是否包含date_month列: {'date_month' in kl_pd.columns}")
        logger.info(f"kl_pd.name: {kl_pd.name}")
    
        # 创建基准对象
        try:
            benchmark = AbuBenchmark(benchmark=symbol, benchmark_kl_pd=kl_pd)
            logger.info(f"创建基准对象成功: {benchmark.benchmark}")
        except Exception as e:
            logger.error(f"创建基准对象失败: {e}")
            traceback.print_exc()
            return
    
        # 创建资金对象
        try:
            capital = AbuCapital(1000000, benchmark=benchmark)  # 100万元初始资金，增加资金量以满足最小交易单位要求
            logger.info(f"创建资金对象成功，初始资金: {capital.read_cash}")
        except Exception as e:
            logger.error(f"创建资金对象失败: {e}")
            traceback.print_exc()
            return
    
        # 创建因子列表
        # 创建一个简单的自定义买入因子
        from abupy.FactorBuyBu.ABuFactorBuyBase import AbuFactorBuyBase, BuyCallMixin
    
        import numpy as np
    
        class AbuFactorBuySimple(AbuFactorBuyBase, BuyCallMixin):
            """简单的测试买入因子，在满足条件时买入"""
        
            def _init_self(self, **kwargs):
                self.factor_name = 'SimpleBuyFactor'
                self.buy_allowed = True  # 允许买入
                self.skip_days = 0  # 确保skip_days为0，不跳过任何交易日
                self.trade_count = 0  # 新增：统计交易次数
                logger.debug(f"\nAbuFactorBuySimple初始化完成，buy_allowed={self.buy_allowed}")
        
            def fit_day(self, today):
                logger.debug(f"\n进入fit_day，today.key: {today.key}")
            
                # 设置today_ind（防止它没有被设置）
                if not hasattr(self, 'today_ind') or self.today_ind is None:
                    self.today_ind = int(today.key)
            
                # 确保我们不会超出范围
                if self.today_ind >= len(self.kl_pd) - 1:
                    logger.debug(f"  超出范围，self.today_ind: {self.today_ind}, kl_pd长度: {len(self.kl_pd)}")
                    return None
            
                logger.debug(f"  buy_allowed: {self.buy_allowed}")
                # 非常简单的条件：每天都尝试买入
                logger.debug(f"  产生买入信号！")
                logger.debug(f"  today.key: {today.key}")
                logger.debug(f"  self.today_ind: {self.today_ind}")
                logger.debug(f"  today.close: {today.close}")
                    
                # 尝试直接创建订单
                try:
                    # 获取第二天的数据
                    next_day = self.kl_pd.iloc[self.today_ind + 1]
                    logger.debug(f"  第二天数据: {next_day}")
                
                    # 检查滑点类
                    logger.debug(f"  滑点类: {self.slippage_class}")
                
                    # 检查资金
                    logger.debug(f"  当前资金: {self.capital.read_cash}")
                
                    # 检查kl_pd.name
                    logger.debug(f"  kl_pd.name: {self.kl_pd.name}")
                
                    # 直接测试fit_buy_order的各个步骤
                    from abupy.TradeBu.ABuOrder import AbuOrder
                    order = AbuOrder()
                
                    # 测试滑点类
                    slippage_class = self.slippage_class
                    factor_name = self.factor_name
                    fact = slippage_class(next_day, factor_name)
                    bp = fact.fit()
                    logger.debug(f"  滑点类返回的买入价格: {bp}")
                
                    if bp < np.inf:
                        # 测试仓位管理类
                        position_class = self.position_class
                        position = position_class(next_day, factor_name, self.kl_pd.name, bp, self.capital.read_cash, **self.position_kwargs)
                        bc = position.fit_position(self)
                        logger.debug(f"  仓位管理类返回的买入数量: {bc}")
                    
                        if not np.isnan(bc):
                            import math
                            # A股向下取整数到最小交易单位个数
                            buy_cnt = int(math.floor(bc))
                            # A股最小100一手
                            min_cnt = 100
                            # 向最小的手量看齐
                            buy_cnt -= buy_cnt % min_cnt
                            logger.debug(f"  调整后的买入数量: {buy_cnt}")
                            logger.debug(f"  最小交易单位: {min_cnt}")
                        
                            if buy_cnt >= min_cnt:
                                logger.debug("  买入数量满足最小交易单位要求！")
                                # 手动设置order属性
                                order.buy_symbol = self.kl_pd.name
                                order.buy_date = int(next_day.date)
                                order.buy_factor = self.factor_name
                                order.buy_factor_class = self.__class__.__name__
                                order.buy_price = bp
                                order.buy_cnt = buy_cnt
                                order.buy_pos = position.__class__.__name__
                                order.buy_type_str = self.buy_type_str
                                order.expect_direction = self.expect_direction
                                order.sell_date = None
                                order.sell_type = 'keep'
                                order.keep_days = 0
                                order.sell_price = None
                                order.sell_type_extra = ''
                                order.ml_features = None
                                order.order_deal = True
                                self.trade_count += 1  # 新增：交易次数加1
                                logger.debug(f"  手动设置订单完成！")
                                logger.debug(f"  order.buy_symbol: {order.buy_symbol}")
                                logger.debug(f"  order.buy_price: {order.buy_price}")
                                logger.debug(f"  order.buy_cnt: {order.buy_cnt}")
                                logger.debug(f"  order.order_deal: {order.order_deal}")
                                logger.debug(f"  当前交易次数: {self.trade_count}")
                            else:
                                logger.debug("  买入数量不满足最小交易单位要求！")
                        else:
                            logger.debug("  仓位管理类返回NaN！")
                    else:
                        logger.debug("  滑点类返回正无穷，不买入！")
                    return order
                except Exception as e:
                    logger.error(f"  创建订单时出错: {e}")
                    traceback.print_exc()
                return None
    
        # 使用自定义的简单买入因子
        buy_factors = [{'class': AbuFactorBuySimple}]
    
        # 创建卖出因子
        sell_factors = [{'stop_loss_n': 1.0, 'class': AbuFactorAtrNStop}]
    
        # 执行回测
        logger.info("\n执行回测...")
        logger.info(f"股票代码: {symbol}")
        logger.info(f"基准对象: {benchmark.benchmark}")
        logger.info(f"买入因子: {buy_factors}")
        logger.info(f"卖出因子: {sell_factors}")
        logger.info(f"金融数据行数: {len(kl_pd)}")
        logger.info(f"金融数据时间范围: {kl_pd.index[0]} 到 {kl_pd.index[-1]}")
    
        # 导入需要的模块
        from abupy.AlphaBu.ABuPickTimeExecute import _do_pick_time_work, EFitError
        from abupy.AlphaBu.ABuPickTimeWorker import AbuPickTimeWorker
        from abupy.TradeBu.ABuTradeProxy import trade_summary
    
        # 直接使用AbuPickTimeWorker进行回测，以获取更详细的调试信息
        try:
            pick_timer_worker = AbuPickTimeWorker(
                cap=capital,
                kl_pd=kl_pd,
                benchmark=benchmark,
                buy_factors=buy_factors,
                sell_factors=sell_factors
            )
        
            logger.info("\n初始化AbuPickTimeWorker成功")
            logger.info(f"资金: {pick_timer_worker.capital}")
            logger.info(f"买入因子数量: {len(pick_timer_worker.buy_factors)}")
            logger.info(f"卖出因子数量: {len(pick_timer_worker.sell_factors)}")
        
            # 手动执行回测
            logger.info("\n手动执行回测...")
            pick_timer_worker.fit()
        
            logger.info(f"\n回测完成")
            logger.info(f"产生的订单数量: {len(pick_timer_worker.orders)}")
            logger.info(f"总交易次数: {len(pick_timer_worker.orders)}")
        except Exception as e:
            logger.error(f"执行回测失败: {e}")
            traceback.print_exc()
            return
    
        if pick_timer_worker.orders:
            logger.info(f"\n回测结果:")
            logger.info(f"总交易次数: {len(pick_timer_worker.orders)}")
            logger.info(f"订单详情:")
            for i, order in enumerate(pick_timer_worker.orders[:5]):  # 只打印前5个订单
                try:
                    logger.info(f"订单 {i+1}:")
                    logger.info(f"  股票代码: {order.buy_symbol}")
                    logger.info(f"  买入日期: {order.buy_date}")
                    logger.info(f"  买入价格: {order.buy_price}")
                    logger.info(f"  买入数量: {order.buy_cnt}")
                    logger.info(f"  订单状态: {'成交' if order.order_deal else '未成交'}")
                    logger.info(f"  卖出日期: {order.sell_date}")
                    logger.info(f"  卖出类型: {order.sell_type}")
                except Exception as e:
                    logger.error(f"打印订单详情时出错: {e}")
                    traceback.print_exc()
        else:
            logger.info("\n没有产生任何订单")
        
            # 检查buy_factors
            logger.info(f"\n检查buy_factors:")
            try:
                for i, bf in enumerate(pick_timer_worker.buy_factors):
                    logger.info(f"买入因子 {i+1}:")
                    logger.info(f"  类型: {bf.__class__.__name__}")
                    logger.info(f"  名称: {bf.factor_name}")
                    logger.info(f"  锁定状态: {bf.lock_factor}")
                    logger.debug(f"  因子属性: {dir(bf)}")
                
                # 手动测试买入因子
                logger.info(f"\n手动测试买入因子...")
                factor = pick_timer_worker.buy_factors[0]
                logger.info(f"测试因子: {factor.__class__.__name__}")
            
                # 遍历前10天的数据进行测试，减1确保有下一天的数据
                for i in range(min(10, len(kl_pd) - 1)):
                    try:
                        today = kl_pd.iloc[i]
                        logger.info(f"\n测试第 {i+1} 天: {today.name}")
                        logger.info(f"  日期: {today.name}")
                        logger.info(f"  收盘价: {today.close}")
                    
                        # 重置today_ind为当前日期索引，确保不超出范围
                        factor.today_ind = i
                    
                        # 重置buy_allowed为True，确保可以买入
                        factor.buy_allowed = True
                        logger.info(f"  重置buy_allowed为: {factor.buy_allowed}")
                    
                        # 测试fit_day方法
                        result = factor.fit_day(today)
                        logger.info(f"  fit_day结果: {result}")
                    
                        # 如果result不是None，说明产生了买入信号
                        if result is not None:
                            logger.info(f"  ✓ 产生了买入信号！")
                        else:
                            logger.info(f"  ✗ 没有产生买入信号")
                    except Exception as e:
                        logger.error(f"手动测试第{i+1}天出错: {e}")
                        traceback.print_exc()
            except Exception as e:
                logger.error(f"检查buy_factors时出错: {e}")
                traceback.print_exc()
    
        logger.info("测试完成")
    
    except Exception as e:
        logger.error(f"test_backtest函数出错: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        test_backtest()
    except Exception as e:
        logger.critical(f"主程序执行失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭日志
        logging.shutdown()