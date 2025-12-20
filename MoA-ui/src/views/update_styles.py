# 批量更新页面样式脚本
import os
import re

# 目标目录
views_dir = r'e:/source/abu/abu-master/MoA-ui/src/views'

# 正则表达式模式，匹配各种容器类的max-width设置
patterns = [
    # 匹配各种容器类
    r'(\.\w+-container|\.\w+-view)\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    # 匹配特定的容器类
    r'\.resistance-support\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.gap-analysis\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.trend-speed\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.distance-ratio\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.linear-fit\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.golden-section\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.price-channel\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.correlation\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}',
    r'\.change-analysis\s*\{[^}]*max-width\s*:\s*1200px[^}]*\}'
]

# 遍历所有.vue文件
for file_name in os.listdir(views_dir):
    if file_name.endswith('.vue'):
        file_path = os.path.join(views_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 应用所有正则表达式替换
        modified = False
        for pattern in patterns:
            def replace_func(match):
                # 将max-width: 1200px替换为width: 100%，并添加box-sizing: border-box
                matched_text = match.group(0)
                # 替换max-width
                updated_text = re.sub(r'max-width\s*:\s*1200px', 'width: 100%', matched_text)
                # 添加box-sizing
                if 'box-sizing' not in updated_text:
                    # 在margin后添加box-sizing
                    updated_text = re.sub(r'(margin[^}]+)', r'\1  box-sizing: border-box;', updated_text)
                    # 如果没有margin，在{后添加box-sizing
                    if 'margin' not in updated_text:
                        updated_text = updated_text.replace('{', '{\n  box-sizing: border-box;')
                return updated_text
            
            new_content, count = re.subn(pattern, replace_func, content, flags=re.DOTALL)
            if count > 0:
                content = new_content
                modified = True
        
        # 保存修改后的内容
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Updated: {file_name}')

print('All files processed.')
