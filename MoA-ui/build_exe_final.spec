# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - 最终完整版本
确保所有文件和静态资源被正确打包
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

# 完整的静态文件和数据文件列表
datas = [
    # 使用绝对路径确保文件被正确包含
    (str(project_root / 'server' / 'static'), 'server/static'),
    (str(project_root / 'server' / 'config'), 'server/config'),
    (str(project_root / 'server' / 'blueprints'), 'server/blueprints'),
    (str(project_root / 'server' / 'models'), 'server/models'),
    (str(project_root / 'server' / 'utils'), 'server/utils'),
    
    # abupy整个模块目录
    (str(parent_dir / 'abupy'), 'abupy'),
    
    # 额外的必要文件
    (str(project_root / 'package.json'), '.'),
    (str(project_root / 'README.md'), '.'),
    (str(project_root / 'index.html'), '.'),
]

# 需要隐藏导入的模块
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
    'abupy.MarketBu.ABuSQLiteCache',
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
    'sklearn.utils',
    'sklearn.base',
    'sklearn.ensemble',
    'sklearn.tree',
    'sklearn.model_selection',
    
    # 图表相关
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends',
    'matplotlib.backends.backend_agg',
    
    # 网络请求
    'requests',
    'urllib',
    'urllib3',
    
    # IPython相关（被abupy依赖）
    'IPython',
    'IPython.display',
    'IPython.core',
    'IPython.utils',
    
    # 其他工具
    'json',
    'datetime',
    'pathlib',
    'logging',
    'threading',
    'multiprocessing',
    'concurrent.futures',
    'unittest',
    'tokenize',
    'zipfile',
    'email',
    'calendar',
    'difflib',
    'quopri',
]

# 排除列表（只排除大型非必要包）
excludes = [
    # 开发工具包
    'jupyter',
    'notebook',
    'sphinx',
    'numpydoc',
    'pytest',
    'setuptools',
    'pip',
    
    # 大型GUI库
    'tkinter',
    'PyQt4',
    'PyQt5',
    'PyQt6',
    'PySide',
    'PySide2',
]

# 打包分析
a = Analysis(
    [str(project_root / 'server' / 'app.py')],  # 主脚本
    pathex=[str(project_root), str(parent_dir)],  # 路径
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
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)