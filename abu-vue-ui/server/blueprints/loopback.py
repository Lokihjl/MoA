# 回测相关蓝图
from flask import request, jsonify
import json
from . import moA_bp
from models import LoopBackRecord, db

# =================== 魔A回测相关接口 ===================

# 运行策略回测
@moA_bp.route('/loopback', methods=['POST', 'OPTIONS'])
def run_loopback():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        # 获取回测参数
        params = request.get_json()
        print('收到回测请求:', params)
        
        # 模拟回测结果（实际项目中应调用魔A量化框架的回测函数）
        mock_result = {
            'winRate': 0.65,
            'totalProfit': 0.45,
            'annualProfit': 0.225,
            'sharpeRatio': 1.8,
            'maxDrawdown': -0.08,
            'tradesCount': 24
        }
        
        # 将回测记录保存到数据库
        record = LoopBackRecord(
            params=json.dumps(params),
            result=json.dumps(mock_result)
        )
        db.session.add(record)
        db.session.commit()
        
        # 返回回测结果
        return jsonify(mock_result), 200
    except Exception as e:
        print('回测失败:', str(e))
        return jsonify({'error': f'回测失败: {str(e)}'}), 500

# 获取回测记录列表
@moA_bp.route('/loopback/records', methods=['GET'])
def get_loopback_records():
    try:
        # 查询所有回测记录
        records = LoopBackRecord.query.all()
        
        # 格式化返回结果
        result = []
        for record in records:
            result.append({
                'id': record.id,
                'params': json.loads(record.params),
                'result': json.loads(record.result),
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify(result), 200
    except Exception as e:
        print('获取回测记录失败:', str(e))
        return jsonify({'error': f'获取回测记录失败: {str(e)}'}), 500

# 获取单个回测记录
@moA_bp.route('/loopback/records/<int:record_id>', methods=['GET'])
def get_loopback_record(record_id):
    try:
        # 查询单个回测记录
        record = LoopBackRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '回测记录不存在'}), 404
        
        # 格式化返回结果
        result = {
            'id': record.id,
            'params': json.loads(record.params),
            'result': json.loads(record.result),
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取回测记录失败:', str(e))
        return jsonify({'error': f'获取回测记录失败: {str(e)}'}), 500

# 删除回测记录
@moA_bp.route('/loopback/records/<int:record_id>', methods=['DELETE'])
def delete_loopback_record(record_id):
    try:
        # 查询并删除回测记录
        record = LoopBackRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '回测记录不存在'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': '回测记录删除成功'}), 200
    except Exception as e:
        print('删除回测记录失败:', str(e))
        return jsonify({'error': f'删除回测记录失败: {str(e)}'}), 500
