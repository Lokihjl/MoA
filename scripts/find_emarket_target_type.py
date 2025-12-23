# 查找EMarketTargetType的完整定义
import sys
sys.path.append('.')
from abupy.CoreBu.ABuEnv import EMarketTargetType

# 打印所有枚举值
print("EMarketTargetType枚举值:")
for enum_name in dir(EMarketTargetType):
    if not enum_name.startswith('_'):
        enum_value = getattr(EMarketTargetType, enum_name)
        print(f"{enum_name} = {enum_value.value}")
