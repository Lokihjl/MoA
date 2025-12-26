# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - 终极版本
使用绝对路径确保所有文件被正确包含
"""

import os
import sys
from pathlib import Path

# 项目根目录和父目录
project_root = Path(os.getcwd())
parent_dir = project_root.parent

# 添加路径到Python路径中
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(parent_dir))

# 验证静态文件是否存在
static_path = project_root / 'server' / 'static'
if not static_path.exists():
    print(f"警告：静态文件目录不存在: {static_path}")
else:
    print(f"静态文件目录存在: {static_path}")
    # 列出静态文件目录内容
    for item in static_path.rglob('*'):
        if item.is_file():
            print(f"  找到文件: {item.relative_to(project_root)}")

# 使用绝对路径的数据文件配置
datas = []

# 检查并添加静态文件 - 关键修复：打包为static而不是server/static
if static_path.exists():
    datas.append((str(static_path), 'static'))
    print(f"添加静态文件: {static_path} -> static")
    
# 添加其他必要的目录
for subdir in ['config', 'blueprints', 'models', 'utils']:
    subdir_path = project_root / 'server' / subdir
    if subdir_path.exists():
        datas.append((str(subdir_path), f'server/{subdir}'))
        print(f"添加目录: {subdir_path} -> server/{subdir}")

# abupy模块
abupy_path = parent_dir / 'abupy'
if abupy_path.exists():
    datas.append((str(abupy_path), 'abupy'))
    print(f"添加abupy: {abupy_path}")

# 额外的必要文件
extra_files = ['package.json', 'README.md', 'index.html']
for file_name in extra_files:
    file_path = project_root / file_name
    if file_path.exists():
        datas.append((str(file_path), '.'))
        print(f"添加文件: {file_path} -> .")

print(f"总共添加了 {len(datas)} 个数据项")
for data_item in datas:
    print(f"  {data_item[0]} -> {data_item[1]}")

# 隐藏导入模块
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
    
    # abupy模块（关键！）
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
    
    # IPython（被abupy依赖）
    'IPython',
    'IPython.display',
    'IPython.core',
    'IPython.utils',
    
    # 标准库模块（确保不被排除）
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
    'tempfile',
    'shutil',
    'glob',
    'fnmatch',
    'pickle',
    'copy',
    'collections',
    'itertools',
    'functools',
    'operator',
    'math',
    'random',
    'statistics',
    'decimal',
    'fractions',
    're',
    'string',
    'textwrap',
    'unicodedata',
    'locale',
    'platform',
    'resource',
    'select',
    'thread',
    'queue',
    'sched',
    'email',
    'html',
    'xml',
    'urllib.parse',
    'urllib.error',
    'urllib.request',
    'urllib.response',
    'ftplib',
    'poplib',
    'imaplib',
    'smtplib',
    'telnetlib',
    'socketserver',
    'wsgiref',
    'configparser',
    'optparse',
    'argparse',
    'getopt',
    'logging',
    'getpass',
    'curses',
    'cmd',
    'subprocess',
    'socket',
    'ssl',
    'ipaddress',
    'asyncio',
    'concurrent.futures',
    'threading',
    'multiprocessing',
    'queue',
    'sched',
    'signal',
    'os',
    'sys',
    'io',
    'os.path',
    'stat',
    'time',
    'calendar',
    'datetime',
    'collections',
    'heapq',
    'bisect',
    'array',
    'struct',
    'codecs',
    'unicodedata',
    'string',
    'textwrap',
    'locale',
    'platform',
    'resource',
    'select',
    'thread',
    'csv',
    'configparser',
    'optparse',
    'argparse',
    'getopt',
    'logging',
    'getpass',
    'curses',
    'cmd',
    'subprocess',
    'socket',
    'ssl',
    'ipaddress',
]

# 排除列表（保持最小化）
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
    
    # 其他大型包（保留seaborn和bokeh因为abupy依赖）
    'plotly',
    'dash',
    'streamlit',
]

print(f"隐藏导入模块数量: {len(hiddenimports)}")
print(f"排除模块数量: {len(excludes)}")

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