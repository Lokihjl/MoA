# 蓝图初始化
from flask import Blueprint

# 创建魔A功能的主Blueprint
moA_bp = Blueprint('moA', __name__, url_prefix='/api/moA')

# 导入所有蓝图模块
from . import loopback
from . import stock
from . import strategy
from . import data
from . import alpha_strategy
from . import gap
from . import trend_speed
from . import golden_section
from . import price_change
