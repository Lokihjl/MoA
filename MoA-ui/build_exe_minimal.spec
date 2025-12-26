# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - 最小排除版本
用于将魔A量化交易系统打包为独立exe文件
只排除明显不需要的模块，避免标准库依赖问题
"""

import os
import sys
from pathlib import Path

# 项目根目录
project_root = Path(os.getcwd())
sys.path.insert(0, str(project_root))

# 需要包含的数据文件和目录
datas = [
    # Flask模板和静态文件
    ('server/static', 'server/static'),
    ('server/config', 'server/config'),
    ('server/blueprints', 'server/blueprints'),
    ('server/models', 'server/models'),
    ('server/utils', 'server/utils'),
    
    # abupy模块中的必要数据文件（使用绝对路径）
    (str(project_root.parent / 'abupy' / 'RomDataBu'), 'abupy/RomDataBu'),
    
    # 前端文件（如果有的话）
    ('src', 'src'),
    ('public', 'public'),
    
    # 其他必要文件
    ('package.json', '.'),
    ('README.md', '.'),
    ('index.html', '.'),
]

# 需要隐藏导入的模块
hiddenimports = [
    # Flask相关
    'flask',
    'flask_sqlalchemy',
    'flask_cors',
    
    # 数据库相关
    'sqlalchemy',
    'sqlite3',
    
    # 量化交易相关
    'abupy',
    'abupy.CoreBu.ABuEnv',
    'abupy.CoreBu.ABu',
    'abupy.CoreBu.ABuBase',
    'abupy.CoreBu.ABuPdHelper',
    'abupy.IndicatorBu.ABuNDMa',
    'abupy.TradeBu.ABuCapital',
    'abupy.TradeBu.ABuOrder',
    'abupy.UtilBu.ABuRegUtil',
    'abupy.UtilBu.ABuStatsUtil',
    
    # 机器学习相关
    'sklearn',
    'numpy',
    'pandas',
    
    # 图表相关
    'matplotlib',
    
    # 网络请求
    'requests',
    'urllib',
    
    # 其他工具
    'json',
    'datetime',
    'pathlib',
    'logging',
    'threading',
    'multiprocessing',
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
]

# 注意：不排除任何核心标准库模块
# 保留所有标准库模块以避免依赖问题

# 打包分析
a = Analysis(
    ['server\\app.py'],  # 主脚本
    pathex=[str(project_root)],
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