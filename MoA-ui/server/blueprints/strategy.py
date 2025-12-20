# 策略相关蓝图
from flask import request, jsonify
from . import moA_bp

# =================== 魔A策略相关接口 ===================

# 获取可用策略列表
@moA_bp.route('/strategies', methods=['GET'])
def get_strategies():
    try:
        # 模拟可用策略列表（实际项目中应调用魔A量化框架的策略列表函数）
        mock_strategies = [
            {'id': 'breakout', 'name': '突破策略', 'description': '基于价格突破的策略'},
            {'id': 'double_ma', 'name': '双均线策略', 'description': '基于双均线交叉的策略'},
            {'id': 'trend_follow', 'name': '趋势跟踪策略', 'description': '基于趋势跟踪的策略'},
            {'id': 'mean_reversion', 'name': '均值回归策略', 'description': '基于均值回归的策略'}
        ]
        
        return jsonify(mock_strategies), 200
    except Exception as e:
        print('获取策略列表失败:', str(e))
        return jsonify({'error': f'获取策略列表失败: {str(e)}'}), 500

# 获取策略详情
@moA_bp.route('/strategies/<strategy_id>', methods=['GET'])
def get_strategy_detail(strategy_id):
    try:
        # 模拟策略详情（实际项目中应调用魔A量化框架的策略详情函数）
        mock_strategy_detail = {
            'id': strategy_id,
            'name': f'{strategy_id}策略',
            'description': f'基于{strategy_id}的量化策略',
            'parameters': [
                {'name': 'xd', 'type': 'integer', 'default': 42, 'description': '突破天数'},
                {'name': 'stop_loss', 'type': 'float', 'default': 0.05, 'description': '止损比例'},
                {'name': 'take_profit', 'type': 'float', 'default': 0.2, 'description': '止盈比例'}
            ]
        }
        
        return jsonify(mock_strategy_detail), 200
    except Exception as e:
        print('获取策略详情失败:', str(e))
        return jsonify({'error': f'获取策略详情失败: {str(e)}'}), 500
