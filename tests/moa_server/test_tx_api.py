# 直接测试腾讯财经API
import requests

def test_tx_stock_api(symbol):
    """
    测试腾讯财经股票行情API
    :param symbol: 股票代码，如'sh600000'表示上海证券交易所的浦发银行
    :return: 解析后的股票数据字典，或None表示失败
    """
    # 腾讯财经股票行情API
    url = f'http://qt.gtimg.cn/q={symbol}'
    print(f'测试直接调用腾讯财经API: {url}')
    
    try:
        # 设置较短的超时时间，避免用户等待过长
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # 检查HTTP状态码
        
        print(f'✅ 调用成功，状态码: {response.status_code}')
        print(f'返回原始数据: {response.text}')
        
        # 解析腾讯财经返回的数据
        data = response.text
        if data.startswith('v_'):
            # 腾讯财经API返回格式：v_sh600000="0~11.58~11.63~11.57~...";
            # 解析数据
            parts = data.split('=')
            if len(parts) == 2:
                stock_data = parts[1].strip('";\r\n')
                stock_fields = stock_data.split('~')
                
                # 定义字段映射
                field_names = [
                    'market_type', 'stock_name', 'stock_code', 'current_price', 'today_open', 'yesterday_close',
                    'volume', 'outer_volume', 'inner_volume', 'buy1_price', 'buy1_volume', 'buy2_price', 'buy2_volume',
                    'buy3_price', 'buy3_volume', 'buy4_price', 'buy4_volume', 'buy5_price', 'buy5_volume',
                    'sell1_price', 'sell1_volume', 'sell2_price', 'sell2_volume', 'sell3_price', 'sell3_volume',
                    'sell4_price', 'sell4_volume', 'sell5_price', 'sell5_volume', 'reserved1', 'trade_time',
                    'price_change', 'change_percent', 'up_limit_price', 'down_limit_price', 'trade_info',
                    'total_volume', 'total_amount', 'turnover_rate', 'pe_ratio', 'reserved2', 'today_high',
                    'today_low', 'reserved3', 'total_market_cap', 'circulating_market_cap', 'reserved4', 'reserved5',
                    'high_52w', 'low_52w', 'reserved6', 'reserved7', 'reserved8', 'reserved9', 'reserved10',
                    'reserved11', 'reserved12', 'reserved13', 'reserved14', 'reserved15', 'reserved16',
                    'reserved17', 'reserved18', 'reserved19', 'reserved20', 'reserved21', 'reserved22',
                    'reserved23', 'reserved24', 'reserved25', 'reserved26', 'reserved27', 'reserved28',
                    'reserved29', 'reserved30', 'reserved31', 'reserved32', 'reserved33', 'reserved34',
                    'reserved35', 'reserved36', 'reserved37', 'reserved38', 'reserved39', 'reserved40'
                ]
                
                # 构建股票数据字典
                stock_info = {}
                for i, field_name in enumerate(field_names):
                    if i < len(stock_fields):
                        stock_info[field_name] = stock_fields[i]
                    else:
                        stock_info[field_name] = ''
                
                print('\n解析后的股票数据:')
                for key, value in stock_info.items():
                    print(f'{key}: {value}')
                
                return stock_info
            else:
                print('❌ 数据格式错误，无法解析')
        else:
            print(f'❌ 数据格式异常: {data}')
    except requests.exceptions.ConnectTimeout:
        print(f'❌ 连接腾讯财经API超时，请检查网络连接')
    except requests.exceptions.ConnectionError:
        print(f'❌ 无法连接到腾讯财经API服务器，请检查网络或API地址是否正确')
    except requests.exceptions.HTTPError as e:
        print(f'❌ 腾讯财经API返回错误状态码: {e}')
    except Exception as e:
        print(f'❌ 调用腾讯财经API异常: {str(e)}')
    return None

# 测试函数
if __name__ == '__main__':
    # 测试浦发银行股票
    test_tx_stock_api('sh600000')
