# 测试财经API的可用性
import requests

# 要测试的财经API列表
finance_apis = [
    # 百度财经API
    {'name': '百度财经', 'url': 'http://gp.baidu.com/stocks/stockkline', 'params': {'stock_code': 'usAAPL'}},
    # 新浪财经API
    {'name': '新浪财经', 'url': 'https://hq.sinajs.cn/list=gb_USDCNY'},
    # 腾讯财经API
    {'name': '腾讯财经', 'url': 'http://qt.gtimg.cn/q=sh600000'},
    # 网易财经API
    {'name': '网易财经', 'url': 'https://api.money.126.net/data/feed/0000001,1399001', 'params': {'callback': 'callback'}},
    # 东方财富API
    {'name': '东方财富', 'url': 'http://quote.eastmoney.com/stocklist.html'}
]

# 测试每个API
def test_api(api):
    try:
        print(f'测试 {api["name"]}...')
        response = requests.get(api['url'], params=api.get('params', {}), timeout=10)
        if response.status_code == 200:
            print(f'✅ {api["name"]} 可以正常访问')
            return True
        else:
            print(f'❌ {api["name"]} 访问失败，状态码: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ {api["name"]} 访问失败，错误: {str(e)}')
        return False

# 主函数
if __name__ == '__main__':
    print('开始测试财经API可用性...')
    print('-' * 50)
    
    success_count = 0
    for api in finance_apis:
        if test_api(api):
            success_count += 1
        print('-' * 50)
    
    print(f'测试完成，共测试 {len(finance_apis)} 个API，其中 {success_count} 个可以正常访问')
