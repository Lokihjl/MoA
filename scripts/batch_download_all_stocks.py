# coding=utf-8
"""
批量下载所有A股股票数据到SQLite数据库
"""

from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN
from abupy.MarketBu.ABuSymbolPd import make_kl_df
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketDataFetchMode
import time

def batch_download_all_stocks():
    """
    批量下载所有A股股票数据
    """
    print("=== 开始批量下载所有A股股票数据 ===")
    
    # 确保使用SQLite作为数据源
    print(f"当前数据缓存类型: {ABuEnv.g_data_cache_type}")
    
    # 设置数据获取模式为网络获取（如果本地没有数据）
    ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
    
    # 获取所有A股股票代码
    print("正在获取所有A股股票代码...")
    abu_symbol_cn = AbuSymbolCN()
    all_symbols = abu_symbol_cn.all_symbol(index=True)  # 包含指数
    
    print(f"共获取到 {len(all_symbols)} 个A股股票代码")
    print(f"前10个股票代码: {all_symbols[:10]}")
    
    # 分批次下载，每批次100个股票，避免内存占用过高
    batch_size = 100
    total_batches = (len(all_symbols) + batch_size - 1) // batch_size
    
    print(f"将分 {total_batches} 批次下载，每批次 {batch_size} 个股票")
    
    start_time = time.time()
    
    for batch_idx in range(total_batches):
        batch_start = batch_idx * batch_size
        batch_end = min((batch_idx + 1) * batch_size, len(all_symbols))
        batch_symbols = all_symbols[batch_start:batch_end]
        
        print(f"\n--- 正在下载第 {batch_idx + 1}/{total_batches} 批次，股票范围: {batch_start + 1}-{batch_end}/{len(all_symbols)} ---")
        print(f"当前批次股票代码: {batch_symbols[:5]}...{batch_symbols[-5:]}")
        
        batch_start_time = time.time()
        
        try:
            # 使用并行方式下载数据，自动保存到SQLite
            panel = make_kl_df(
                batch_symbols,
                n_folds=2,  # 下载最近2年的数据
                parallel=True,  # 启用并行下载
                parallel_save=True,  # 并行后统一保存
                show_progress=True  # 显示进度条
            )
            
            batch_end_time = time.time()
            batch_duration = batch_end_time - batch_start_time
            
            print(f"第 {batch_idx + 1} 批次下载完成，耗时: {batch_duration:.2f} 秒")
            
        except Exception as e:
            print(f"第 {batch_idx + 1} 批次下载失败: {e}")
            continue
    
    total_duration = time.time() - start_time
    print(f"\n=== 所有A股股票数据下载完成 ===")
    print(f"总耗时: {total_duration:.2f} 秒")
    print(f"共下载 {len(all_symbols)} 个股票数据")
    print(f"数据已保存到SQLite数据库: {ABuEnv.g_project_rom_data_dir}")

if __name__ == "__main__":
    batch_download_all_stocks()
