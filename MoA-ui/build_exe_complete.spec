# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - 完整版本
用于将魔A量化交易系统打包为独立exe文件
确保所有依赖模块正确包含
"""

import os
import sys
from pathlib import Path

# 项目根目录和父目录
project_root = Path(os.getcwd())
parent_dir = project_root.parent

# 添加路径到Python路径中，确保能正确找到所有模块
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(parent_dir))

# 需要包含的数据文件和目录
datas = [
    # Flask模板和静态文件
    ('server/static', 'server/static'),
    ('server/config', 'server/config'),
    ('server/blueprints', 'server/blueprints'),
    ('server/models', 'server/models'),
    ('server/utils', 'server/utils'),
    
    # abupy整个模块目录（重要！）
    (str(parent_dir / 'abupy'), 'abupy'),
    
    # 前端文件（如果有的话）
    ('src', 'src'),
    ('public', 'public'),
    
    # 其他必要文件
    ('package.json', '.'),
    ('README.md', '.'),
    ('index.html', '.'),
]

# 需要隐藏导入的模块 - 使用更完整的方式
hiddenimports = [
    # Flask相关
    'flask',
    'flask_sqlalchemy',
    'flask_cors',
    'werkzeug',
    'jinja2',
    'markupsafe',
    'click',
    'itsdangerous',
    
    # 数据库相关
    'sqlalchemy',
    'sqlite3',
    'pysqlite3',
    
    # 量化交易相关 - 完整的abupy模块
    'abupy',
    'abupy.CoreBu',
    'abupy.CoreBu.ABuEnv',
    'abupy.CoreBu.ABu',
    'abupy.CoreBu.ABuBase',
    'abupy.CoreBu.ABuPdHelper',
    'abupy.CoreBu.ABuStore',
    'abupy.CoreBu.ABuFixes',
    'abupy.IndicatorBu',
    'abupy.IndicatorBu.ABuNDMa',
    'abupy.TradeBu',
    'abupy.TradeBu.ABuCapital',
    'abupy.TradeBu.ABuOrder',
    'abupy.UtilBu',
    'abupy.UtilBu.ABuRegUtil',
    'abupy.UtilBu.ABuStatsUtil',
    'abupy.UtilBu.ABuDTUtil',
    'abupy.UtilBu.ABuDateUtil',
    'abupy.UtilBu.ABuFileUtil',
    'abupy.UtilBu.ABuKLUtil',
    'abupy.UtilBu.ABuStrUtil',
    'abupy.UtilBu.ABuOsUtil',
    'abupy.UtilBu.ABuPlatform',
    'abupy.UtilBu.ABuProgress',
    'abupy.MarketBu',
    'abupy.MarketBu.ABuMarket',
    'abupy.MarketBu.ABuSymbol',
    'abupy.MarketBu.ABuNetWork',
    'abupy.TLineBu',
    'abupy.TLineBu.ABuTL',
    'abupy.TLineBu.ABuTLine',
    'abupy.AlphaBu',
    'abupy.AlphaBu.ABuAlpha',
    'abupy.AlphaBu.ABuPickBase',
    'abupy.UmpBu',
    'abupy.UmpBu.ABuUmp',
    'abupy.UmpBu.ABuUmpBase',
    
    # 机器学习相关
    'sklearn',
    'numpy',
    'pandas',
    'scipy',
    
    # 图表相关
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends',
    
    # 网络请求
    'requests',
    'urllib',
    'urllib3',
    
    # 其他工具
    'json',
    'datetime',
    'pathlib',
    'logging',
    'threading',
    'multiprocessing',
    'concurrent.futures',
    'multiprocessing.managers',
    'multiprocessing.shared_memory',
    'multiprocessing.synchronize',
    'multiprocessing.queues',
    'multiprocessing.pool',
    'multiprocessing.dummy',
    'multiprocessing.heap',
    'multiprocessing.reduction',
    'multiprocessing.process',
    'multiprocessing.context',
    'multiprocessing.util',
    'multiprocessing.forkserver',
    'multiprocessing.spawn',
]

# 最小排除列表 - 只排除明显不需要的大型GUI和开发工具
excludes = [
    # 开发工具
    'pytest',
    'unittest',
    'doctest',
    'setuptools',
    'pip',
    
    # 大型GUI库（除非确实需要）
    'tkinter',
    'PyQt4',
    'PyQt5',
    'PyQt6',
    'PySide',
    'PySide2',
    
    # 其他不常用的大包
    'IPython',
    'jupyter',
    'notebook',
    'sphinx',
    'numpydoc',
]

# 打包分析
a = Analysis(
    ['server\\app.py'],  # 主脚本
    pathex=[str(project_root), str(parent_dir)],  # 添加abupy的路径
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 收集Python文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='魔A量化交易系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口，调试时有用
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以设置exe图标
    version_file=None,
)