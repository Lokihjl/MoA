# -*- encoding:utf-8 -*-
"""
    因子生命周期管理系统
    实现因子的注册、测试、部署、监控和退役全生命周期管理
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
import pandas as pd
import datetime
import pickle
import os
import json
from collections import defaultdict
from ..FactorBuyBu.ABuFactorBuyBase import AbuFactorBuyBase
from ..FactorSellBu.ABuFactorSellBase import AbuFactorSellBase
from ..UtilBu.ABuFileUtil import dump_pickle, load_pickle
from ..FactorSellBu.ABuFactorSellNDay import AbuFactorSellNDay
from ..FactorBuyBu.ABuFactorBuyBreak import AbuFactorBuyBreak
from abupy.UtilBu import ABuProgress

__author__ = '量化策略师'


class AbuFactorRegistry(object):
    """因子注册表"""
    
    def __init__(self, registry_path='./factor_registry.json'):
        """
        初始化因子注册表
        :param registry_path: 注册表文件路径
        """
        self.registry_path = registry_path
        self.registry = self.load_registry()
    
    def load_registry(self):
        """
        加载因子注册表
        :return: 因子注册表
        """
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'buy_factors': {},
            'sell_factors': {},
            'version': '1.0'
        }
    
    def save_registry(self):
        """
        保存因子注册表
        """
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def register_factor(self, factor_class, factor_type='buy', description='',
                       version='1.0', author='', tags=None):
        """
        注册因子
        :param factor_class: 因子类
        :param factor_type: 因子类型（buy/sell）
        :param description: 因子描述
        :param version: 因子版本
        :param author: 因子作者
        :param tags: 因子标签
        :return: 注册结果
        """
        factor_name = factor_class.__name__
        registry_key = 'buy_factors' if factor_type == 'buy' else 'sell_factors'
        
        if factor_name in self.registry[registry_key]:
            print(f"因子 {factor_name} 已存在于注册表中")
            return False
        
        # 检查因子是否继承自正确的基类
        if factor_type == 'buy' and not issubclass(factor_class, AbuFactorBuyBase):
            print(f"因子 {factor_name} 不是有效的买入因子类")
            return False
        
        if factor_type == 'sell' and not issubclass(factor_class, AbuFactorSellBase):
            print(f"因子 {factor_name} 不是有效的卖出因子类")
            return False
        
        # 注册因子
        self.registry[registry_key][factor_name] = {
            'class_name': factor_name,
            'type': factor_type,
            'description': description,
            'version': version,
            'author': author,
            'tags': tags or [],
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_updated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'registered',  # registered, testing, deployed, monitoring, deprecated
            'performance_metrics': {}
        }
        
        self.save_registry()
        print(f"因子 {factor_name} 注册成功")
        return True
    
    def update_factor(self, factor_name, factor_type='buy', **kwargs):
        """
        更新因子信息
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :param kwargs: 要更新的字段
        :return: 更新结果
        """
        registry_key = 'buy_factors' if factor_type == 'buy' else 'sell_factors'
        
        if factor_name not in self.registry[registry_key]:
            print(f"因子 {factor_name} 不存在于注册表中")
            return False
        
        # 更新字段
        for key, value in kwargs.items():
            if key in ['status', 'description', 'version', 'tags', 'performance_metrics']:
                self.registry[registry_key][factor_name][key] = value
        
        # 更新时间
        self.registry[registry_key][factor_name]['last_updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.save_registry()
        print(f"因子 {factor_name} 更新成功")
        return True
    
    def get_factor_info(self, factor_name, factor_type='buy'):
        """
        获取因子信息
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :return: 因子信息
        """
        registry_key = 'buy_factors' if factor_type == 'buy' else 'sell_factors'
        
        if factor_name not in self.registry[registry_key]:
            print(f"因子 {factor_name} 不存在于注册表中")
            return None
        
        return self.registry[registry_key][factor_name]
    
    def list_factors(self, factor_type=None, status=None, tags=None):
        """
        列出因子
        :param factor_type: 因子类型（可选）
        :param status: 因子状态（可选）
        :param tags: 因子标签（可选）
        :return: 因子列表
        """
        factors = []
        
        if factor_type is None:
            # 获取所有因子
            for f in self.registry['buy_factors'].values():
                factors.append(f)
            for f in self.registry['sell_factors'].values():
                factors.append(f)
        else:
            # 获取指定类型的因子
            registry_key = 'buy_factors' if factor_type == 'buy' else 'sell_factors'
            factors = list(self.registry[registry_key].values())
        
        # 按状态过滤
        if status is not None:
            factors = [f for f in factors if f['status'] == status]
        
        # 按标签过滤
        if tags is not None:
            factors = [f for f in factors if set(tags).issubset(set(f['tags']))]
        
        return factors
    
    def deprecated_factor(self, factor_name, factor_type='buy', reason=''):
        """
        标记因子为已废弃
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :param reason: 废弃原因
        :return: 操作结果
        """
        return self.update_factor(factor_name, factor_type, 
                                 status='deprecated', 
                                 deprecated_reason=reason)


class AbuFactorEvaluator(object):
    """因子评估器"""
    
    def __init__(self, registry=None):
        """
        初始化因子评估器
        :param registry: 因子注册表
        """
        self.registry = registry or AbuFactorRegistry()
    
    def evaluate_factor(self, factor_class, kl_pd, capital, benchmark=None, n_folds=3):
        """
        评估因子性能
        :param factor_class: 因子类
        :param kl_pd: K线数据
        :param capital: 初始资金
        :param benchmark: 基准数据
        :param n_folds: 交叉验证折数
        :return: 评估结果
        """
        from abupy import AbuCapital, AbuKLManager, AbuBenchmark
        from abupy import ABuPickTimeExecute
        
        factor_name = factor_class.__name__
        
        # 检查因子类型
        if issubclass(factor_class, AbuFactorBuyBase):
            factor_type = 'buy'
            # 使用默认的卖出因子
            sell_factors = [{'sell_factor': AbuFactorSellNDay, 'sell_factor_args': {'n_day': 20}}]
        elif issubclass(factor_class, AbuFactorSellBase):
            factor_type = 'sell'
            # 使用默认的买入因子
            buy_factors = [{'buy_factor': AbuFactorBuyBreak}]
        else:
            print(f"无效的因子类: {factor_name}")
            return None
        
        results = []
        
        # 进行交叉验证
        for fold in range(n_folds):
            print(f"正在进行第 {fold+1}/{n_folds} 次交叉验证...")
            
            # 划分数据
            split_point = int(len(kl_pd) * (fold + 1) / (n_folds + 1))
            train_kl = kl_pd.iloc[:split_point]
            test_kl = kl_pd.iloc[split_point:split_point + int(len(kl_pd) / (n_folds + 1))]
            
            if len(test_kl) < 100:  # 确保有足够的数据
                continue
            
            # 创建回测环境
            capital = AbuCapital(capital)
            benchmark = benchmark or AbuBenchmark()
            kl_pd_manager = AbuKLManager(test_kl)
            
            # 执行回测
            if factor_type == 'buy':
                buy_factors = [{'buy_factor': factor_class}]
                execute = ABuPickTimeExecute()
                result = execute.fit_pick_time(kl_pd_manager, benchmark, capital, 
                                             buy_factors, sell_factors)
            else:
                sell_factors = [{'sell_factor': factor_class}]
                execute = ABuPickTimeExecute()
                result = execute.fit_pick_time(kl_pd_manager, benchmark, capital, 
                                             buy_factors, sell_factors)
            
            results.append(result)
        
        # 计算平均指标
        metrics = self._calculate_metrics(results)
        
        # 更新注册表
        self.registry.update_factor(factor_name, factor_type, 
                                  status='tested', 
                                  performance_metrics=metrics)
        
        return metrics
    
    def _calculate_metrics(self, results):
        """
        计算因子性能指标
        :param results: 回测结果列表
        :return: 性能指标
        """
        if not results:
            return {}
        
        metrics = {
            'avg_return': 0,
            'avg_max_drawdown': 0,
            'avg_sharpe_ratio': 0,
            'avg_win_rate': 0,
            'avg_profit_factor': 0,
            'avg_trades_count': 0
        }
        
        for result in results:
            if hasattr(result, 'capital') and hasattr(result.capital, 'capital_pd'):
                capital_pd = result.capital.capital_pd
                
                if not capital_pd.empty:
                    # 计算收益率
                    total_return = (capital_pd['capital_blance'].iloc[-1] / capital_pd['capital_blance'].iloc[0]) - 1
                    metrics['avg_return'] += total_return
                    
                    # 计算最大回撤
                    drawdown = self._calculate_max_drawdown(capital_pd['capital_blance'])
                    metrics['avg_max_drawdown'] += drawdown
                    
                    # 计算夏普比率
                    sharpe = self._calculate_sharpe_ratio(capital_pd['capital_blance'].pct_change())
                    metrics['avg_sharpe_ratio'] += sharpe
            
            if hasattr(result, 'orders_pd') and not result.orders_pd.empty:
                # 计算胜率
                win_count = len(result.orders_pd[result.orders_pd['profit'] > 0])
                total_count = len(result.orders_pd)
                win_rate = win_count / total_count if total_count > 0 else 0
                metrics['avg_win_rate'] += win_rate
                
                # 计算盈利因子
                profit_factor = self._calculate_profit_factor(result.orders_pd['profit'])
                metrics['avg_profit_factor'] += profit_factor
                
                # 计算交易次数
                metrics['avg_trades_count'] += total_count
        
        # 取平均值
        n_valid_results = len([r for r in results if hasattr(r, 'capital') and hasattr(r.capital, 'capital_pd')])
        if n_valid_results > 0:
            metrics['avg_return'] /= n_valid_results
            metrics['avg_max_drawdown'] /= n_valid_results
            metrics['avg_sharpe_ratio'] /= n_valid_results
        
        n_valid_orders = len([r for r in results if hasattr(r, 'orders_pd') and not r.orders_pd.empty])
        if n_valid_orders > 0:
            metrics['avg_win_rate'] /= n_valid_orders
            metrics['avg_profit_factor'] /= n_valid_orders
            metrics['avg_trades_count'] /= n_valid_orders
        
        return metrics
    
    def _calculate_max_drawdown(self, equity):
        """
        计算最大回撤
        :param equity: 权益曲线
        :return: 最大回撤
        """
        if equity.empty:
            return 0
        
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.03):
        """
        计算夏普比率
        :param returns: 收益率序列
        :param risk_free_rate: 无风险利率
        :return: 夏普比率
        """
        if returns.empty:
            return 0
        
        excess_returns = returns - risk_free_rate / 252  # 假设252个交易日
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
        
        return sharpe
    
    def _calculate_profit_factor(self, profits):
        """
        计算盈利因子
        :param profits: 盈利序列
        :return: 盈利因子
        """
        if profits.empty:
            return 0
        
        total_profit = profits[profits > 0].sum()
        total_loss = abs(profits[profits < 0].sum())
        
        if total_loss == 0:
            return np.inf
        
        return total_profit / total_loss
    
    def compare_factors(self, factor_classes, kl_pd, capital, benchmark=None):
        """
        比较多个因子的性能
        :param factor_classes: 因子类列表
        :param kl_pd: K线数据
        :param capital: 初始资金
        :param benchmark: 基准数据
        :return: 比较结果
        """
        comparison_results = []
        
        for factor_class in factor_classes:
            print(f"正在评估因子: {factor_class.__name__}")
            metrics = self.evaluate_factor(factor_class, kl_pd, capital, benchmark)
            
            if metrics:
                comparison_results.append({
                    'factor_name': factor_class.__name__,
                    'metrics': metrics
                })
        
        # 按夏普比率排序
        comparison_results.sort(key=lambda x: x['metrics'].get('avg_sharpe_ratio', 0), reverse=True)
        
        return comparison_results


class AbuFactorMonitor(object):
    """因子监控器"""
    
    def __init__(self, registry=None):
        """
        初始化因子监控器
        :param registry: 因子注册表
        """
        self.registry = registry or AbuFactorRegistry()
        self.monitoring_data = defaultdict(list)
    
    def monitor_factor(self, factor_name, factor_type, recent_returns, window=20):
        """
        监控因子表现
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :param recent_returns: 最近的收益率序列
        :param window: 监控窗口
        :return: 监控结果
        """
        factor_info = self.registry.get_factor_info(factor_name, factor_type)
        if not factor_info:
            return None
        
        # 保存监控数据
        self.monitoring_data[(factor_name, factor_type)].extend(recent_returns[-window:])
        
        # 只保留最近的window条数据
        if len(self.monitoring_data[(factor_name, factor_type)]) > window:
            self.monitoring_data[(factor_name, factor_type)] = self.monitoring_data[(factor_name, factor_type)][-window:]
        
        # 计算监控指标
        current_returns = self.monitoring_data[(factor_name, factor_type)]
        
        monitoring_results = {
            'factor_name': factor_name,
            'factor_type': factor_type,
            'current_return': np.sum(current_returns),
            'current_sharpe': self._calculate_sharpe_ratio(current_returns),
            'current_max_drawdown': self._calculate_max_drawdown(current_returns),
            'current_win_rate': len([r for r in current_returns if r > 0]) / len(current_returns) if current_returns else 0,
            'alert_messages': []
        }
        
        # 检查是否需要发出警报
        if factor_info['performance_metrics']:
            # 比较当前表现与历史表现
            historical_sharpe = factor_info['performance_metrics'].get('avg_sharpe_ratio', 0)
            if monitoring_results['current_sharpe'] < historical_sharpe * 0.5:
                monitoring_results['alert_messages'].append('夏普比率下降超过50%')
            
            historical_max_drawdown = factor_info['performance_metrics'].get('avg_max_drawdown', 0)
            if monitoring_results['current_max_drawdown'] < historical_max_drawdown * 1.5:  # 注意：回撤是负数
                monitoring_results['alert_messages'].append('最大回撤扩大超过50%')
            
            historical_win_rate = factor_info['performance_metrics'].get('avg_win_rate', 0)
            if monitoring_results['current_win_rate'] < historical_win_rate * 0.5:
                monitoring_results['alert_messages'].append('胜率下降超过50%')
        
        # 更新注册表中的监控信息
        self.registry.update_factor(factor_name, factor_type, 
                                  last_monitored_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  current_performance=monitoring_results)
        
        return monitoring_results
    
    def generate_monitoring_report(self):
        """
        生成监控报告
        :return: 监控报告
        """
        report = {
            'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'factors': [],
            'alerts': []
        }
        
        # 获取所有已部署的因子
        deployed_factors = self.registry.list_factors(status='deployed')
        
        for factor in deployed_factors:
            factor_name = factor['class_name']
            factor_type = factor['type']
            
            if (factor_name, factor_type) in self.monitoring_data:
                # 获取当前监控数据
                monitoring_results = factor.get('current_performance', {})
                
                report['factors'].append({
                    'factor_name': factor_name,
                    'factor_type': factor_type,
                    'status': factor['status'],
                    'version': factor['version'],
                    'current_sharpe': monitoring_results.get('current_sharpe', 0),
                    'historical_sharpe': factor['performance_metrics'].get('avg_sharpe_ratio', 0),
                    'current_max_drawdown': monitoring_results.get('current_max_drawdown', 0),
                    'historical_max_drawdown': factor['performance_metrics'].get('avg_max_drawdown', 0),
                    'alerts': monitoring_results.get('alert_messages', [])
                })
                
                # 收集警报
                for alert in monitoring_results.get('alert_messages', []):
                    report['alerts'].append({
                        'factor_name': factor_name,
                        'factor_type': factor_type,
                        'alert_message': alert,
                        'timestamp': factor.get('last_monitored_at', '')
                    })
        
        return report
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.03):
        """
        计算夏普比率
        :param returns: 收益率序列
        :param risk_free_rate: 无风险利率
        :return: 夏普比率
        """
        if not returns:
            return 0
        
        excess_returns = returns - risk_free_rate / 252  # 假设252个交易日
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
        
        return sharpe
    
    def _calculate_max_drawdown(self, returns):
        """
        计算最大回撤
        :param returns: 收益率序列
        :return: 最大回撤
        """
        if not returns:
            return 0
        
        equity = np.cumprod(1 + np.array(returns))
        peak = equity[0]
        max_drawdown = 0
        
        for value in equity[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        
        return -max_drawdown  # 返回负数表示回撤


class AbuFactorVersionManager(object):
    """因子版本管理器"""
    
    def __init__(self, version_dir='./factor_versions'):
        """
        初始化因子版本管理器
        :param version_dir: 版本存储目录
        """
        self.version_dir = version_dir
        os.makedirs(version_dir, exist_ok=True)
    
    def save_factor_version(self, factor_class, version='1.0', description=''):
        """
        保存因子版本
        :param factor_class: 因子类
        :param version: 版本号
        :param description: 版本描述
        :return: 保存结果
        """
        factor_name = factor_class.__name__
        version_file = os.path.join(self.version_dir, f"{factor_name}_v{version}.pkl")
        
        # 保存因子类
        with open(version_file, 'wb') as f:
            pickle.dump(factor_class, f)
        
        # 保存版本信息
        version_info = {
            'factor_name': factor_name,
            'version': version,
            'description': description,
            'saved_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        info_file = os.path.join(self.version_dir, f"{factor_name}_versions.json")
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                versions = json.load(f)
        else:
            versions = []
        
        versions.append(version_info)
        
        with open(info_file, 'w') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
        
        print(f"因子 {factor_name} 版本 {version} 保存成功")
        return True
    
    def load_factor_version(self, factor_name, version='latest'):
        """
        加载因子版本
        :param factor_name: 因子名称
        :param version: 版本号或'latest'
        :return: 因子类
        """
        info_file = os.path.join(self.version_dir, f"{factor_name}_versions.json")
        
        if not os.path.exists(info_file):
            print(f"因子 {factor_name} 没有版本信息")
            return None
        
        with open(info_file, 'r') as f:
            versions = json.load(f)
        
        if not versions:
            print(f"因子 {factor_name} 没有保存的版本")
            return None
        
        # 查找指定版本
        if version == 'latest':
            # 按版本号排序
            versions.sort(key=lambda x: [int(v) for v in x['version'].split('.')], reverse=True)
            target_version = versions[0]
        else:
            target_version = None
            for v in versions:
                if v['version'] == version:
                    target_version = v
                    break
            
            if not target_version:
                print(f"因子 {factor_name} 版本 {version} 不存在")
                return None
        
        # 加载因子类
        version_file = os.path.join(self.version_dir, f"{factor_name}_v{target_version['version']}.pkl")
        
        if not os.path.exists(version_file):
            print(f"因子 {factor_name} 版本 {target_version['version']} 文件不存在")
            return None
        
        with open(version_file, 'rb') as f:
            factor_class = pickle.load(f)
        
        print(f"加载因子 {factor_name} 版本 {target_version['version']} 成功")
        return factor_class
    
    def list_factor_versions(self, factor_name):
        """
        列出因子的所有版本
        :param factor_name: 因子名称
        :return: 版本列表
        """
        info_file = os.path.join(self.version_dir, f"{factor_name}_versions.json")
        
        if not os.path.exists(info_file):
            print(f"因子 {factor_name} 没有版本信息")
            return []
        
        with open(info_file, 'r') as f:
            versions = json.load(f)
        
        return versions


class AbuFactorLifecycleManager(object):
    """因子生命周期管理器"""
    
    def __init__(self, registry_path='./factor_registry.json', version_dir='./factor_versions'):
        """
        初始化因子生命周期管理器
        :param registry_path: 注册表路径
        :param version_dir: 版本存储目录
        """
        self.registry = AbuFactorRegistry(registry_path)
        self.evaluator = AbuFactorEvaluator(self.registry)
        self.monitor = AbuFactorMonitor(self.registry)
        self.version_manager = AbuFactorVersionManager(version_dir)
    
    def register_new_factor(self, factor_class, factor_type='buy', description='',
                           version='1.0', author='', tags=None):
        """
        注册新因子
        :param factor_class: 因子类
        :param factor_type: 因子类型
        :param description: 因子描述
        :param version: 因子版本
        :param author: 因子作者
        :param tags: 因子标签
        :return: 注册结果
        """
        # 注册因子
        success = self.registry.register_factor(factor_class, factor_type, description,
                                              version, author, tags)
        
        if success:
            # 保存因子版本
            self.version_manager.save_factor_version(factor_class, version, description)
        
        return success
    
    def test_factor(self, factor_class, kl_pd, capital, benchmark=None):
        """
        测试因子
        :param factor_class: 因子类
        :param kl_pd: K线数据
        :param capital: 初始资金
        :param benchmark: 基准数据
        :return: 测试结果
        """
        factor_name = factor_class.__name__
        
        # 检查因子是否已注册
        factor_info = self.registry.get_factor_info(factor_name, 
                                                   'buy' if issubclass(factor_class, AbuFactorBuyBase) else 'sell')
        
        if not factor_info:
            print(f"因子 {factor_name} 尚未注册")
            return None
        
        # 评估因子
        metrics = self.evaluator.evaluate_factor(factor_class, kl_pd, capital, benchmark)
        
        if metrics:
            # 更新因子状态为已测试
            self.registry.update_factor(factor_name, factor_info['type'], status='tested')
        
        return metrics
    
    def deploy_factor(self, factor_name, factor_type='buy'):
        """
        部署因子
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :return: 部署结果
        """
        factor_info = self.registry.get_factor_info(factor_name, factor_type)
        
        if not factor_info:
            print(f"因子 {factor_name} 不存在")
            return False
        
        if factor_info['status'] != 'tested':
            print(f"因子 {factor_name} 尚未通过测试")
            return False
        
        # 更新因子状态为已部署
        success = self.registry.update_factor(factor_name, factor_type, status='deployed')
        
        if success:
            print(f"因子 {factor_name} 部署成功")
        
        return success
    
    def monitor_factor_performance(self, factor_name, factor_type, recent_returns):
        """
        监控因子性能
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :param recent_returns: 最近的收益率序列
        :return: 监控结果
        """
        return self.monitor.monitor_factor(factor_name, factor_type, recent_returns)
    
    def update_factor_version(self, factor_class, new_version, description=''):
        """
        更新因子版本
        :param factor_class: 新的因子类
        :param new_version: 新版本号
        :param description: 版本描述
        :return: 更新结果
        """
        factor_name = factor_class.__name__
        
        # 检查因子是否已注册
        factor_info = self.registry.get_factor_info(factor_name, 
                                                   'buy' if issubclass(factor_class, AbuFactorBuyBase) else 'sell')
        
        if not factor_info:
            print(f"因子 {factor_name} 尚未注册")
            return False
        
        # 保存新版本
        self.version_manager.save_factor_version(factor_class, new_version, description)
        
        # 更新注册表
        self.registry.update_factor(factor_name, factor_info['type'],
                                  version=new_version,
                                  status='registered')  # 新版本需要重新测试
        
        print(f"因子 {factor_name} 版本更新到 {new_version} 成功")
        return True
    
    def deprecated_factor(self, factor_name, factor_type='buy', reason=''):
        """
        标记因子为已废弃
        :param factor_name: 因子名称
        :param factor_type: 因子类型
        :param reason: 废弃原因
        :return: 操作结果
        """
        return self.registry.deprecated_factor(factor_name, factor_type, reason)
    
    def generate_lifecycle_report(self):
        """
        生成因子生命周期报告
        :return: 生命周期报告
        """
        report = {
            'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_factors': 0,
                'registered_factors': 0,
                'testing_factors': 0,
                'deployed_factors': 0,
                'monitoring_factors': 0,
                'deprecated_factors': 0
            },
            'factors': []
        }
        
        # 获取所有因子
        all_factors = self.registry.list_factors()
        
        # 统计摘要
        report['summary']['total_factors'] = len(all_factors)
        
        for factor in all_factors:
            report['summary'][f"{factor['status']}_factors"] += 1
            
            # 收集因子详细信息
            factor_details = {
                'name': factor['class_name'],
                'type': factor['type'],
                'status': factor['status'],
                'version': factor['version'],
                'author': factor['author'],
                'created_at': factor['created_at'],
                'last_updated_at': factor['last_updated_at'],
                'tags': factor['tags'],
                'performance': factor.get('performance_metrics', {}),
                'current_performance': factor.get('current_performance', {})
            }
            
            report['factors'].append(factor_details)
        
        return report


def demo_factor_lifecycle():
    """
    演示因子生命周期管理
    """
    from abupy import ABuSymbolPd
    from abupy.FactorBuyBu.ABuFactorBuyBreak import AbuFactorBuyBreak
    from abupy.FactorSellBu.ABuFactorSellNDay import AbuFactorSellNDay
    
    # 创建生命周期管理器
    lifecycle_manager = AbuFactorLifecycleManager()
    
    # 获取测试数据
    kl_pd = ABuSymbolPd.make_kl_df('600519', n_folds=2)
    capital = 1000000
    
    print("=== 演示因子生命周期管理 ===")
    
    # 1. 注册新因子
    print("\n1. 注册买入因子 AbuFactorBuyBreak...")
    lifecycle_manager.register_new_factor(AbuFactorBuyBreak, 'buy', 
                                         description='突破买入因子',
                                         version='1.0',
                                         author='ABu',
                                         tags=['突破', '趋势', '买入'])
    
    # 2. 注册卖出因子
    print("\n2. 注册卖出因子 AbuFactorSellNDay...")
    lifecycle_manager.register_new_factor(AbuFactorSellNDay, 'sell',
                                         description='持有N天后卖出因子',
                                         version='1.0',
                                         author='ABu',
                                         tags=['持有期限', '卖出'])
    
    # 3. 测试因子
    print("\n3. 测试买入因子 AbuFactorBuyBreak...")
    test_results = lifecycle_manager.test_factor(AbuFactorBuyBreak, kl_pd, capital)
    print(f"测试结果: {test_results}")
    
    # 4. 部署因子
    print("\n4. 部署买入因子 AbuFactorBuyBreak...")
    lifecycle_manager.deploy_factor('AbuFactorBuyBreak', 'buy')
    
    # 5. 监控因子性能（模拟数据）
    print("\n5. 监控因子性能...")
    # 模拟最近20天的收益率
    recent_returns = np.random.normal(0.001, 0.02, 20)
    monitoring_results = lifecycle_manager.monitor_factor_performance('AbuFactorBuyBreak', 'buy', recent_returns)
    print(f"监控结果: {monitoring_results}")
    
    # 6. 生成生命周期报告
    print("\n6. 生成生命周期报告...")
    report = lifecycle_manager.generate_lifecycle_report()
    print(f"报告摘要: {report['summary']}")
    
    # 7. 生成监控报告
    print("\n7. 生成监控报告...")
    monitoring_report = lifecycle_manager.monitor.generate_monitoring_report()
    print(f"监控报告警报数: {len(monitoring_report['alerts'])}")
    
    # 8. 列出因子版本
    print("\n8. 列出因子版本...")
    versions = lifecycle_manager.version_manager.list_factor_versions('AbuFactorBuyBreak')
    for v in versions:
        print(f"版本 {v['version']}: {v['description']} (保存于 {v['saved_at']})")


if __name__ == '__main__':
    demo_factor_lifecycle()