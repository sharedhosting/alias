#!/usr/bin/env python3
import re

def fix_sqlite_sql(input_file, output_file):
    """
    修复SQLite SQL文件中的转义字符和语法错误
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复反斜杠转义问题
    # 将未转义的反斜杠进行转义
    content = re.sub(r'(?<!\\)\\(?!["\'\\nrtbfav]|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[0-7]{1,3}|N\{[a-zA-Z\s]+\})', r'\\\\', content)
    
    # 修复第515行的截断问题
    # 找到有问题的行并修复它
    content = content.replace(
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\",",
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\"),"
    )
    
    # 修复其他可能的转义问题
    # 避免将有效的转义序列（如\\r\\n）重复转义
    # 但修复未正确转义的反斜杠
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 修复引号转义问题
        # 将单引号转为两个单引号（SQLite的转义方式）
        if "INSERT INTO" in line and ("VALUES" in line or line.count("'") > 2):
            # 避免转义已转义的引号，只转义独立的单引号
            # 使用更精确的正则表达式来转义单引号
            fixed_line = line
            # 找到不在字符串中间的单引号并转义
            i = 0
            new_line = ""
            in_string = False
            quote_char = None
            
            while i < len(fixed_line):
                char = fixed_line[i]
                
                if char in ["'", '"'] and (i == 0 or fixed_line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                        new_line += char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                        new_line += char
                    else:
                        new_line += char
                else:
                    new_line += char
                
                i += 1
            
            # 现在处理字符串中的单引号转义
            # SQLite中，单引号用两个单引号转义
            fixed_line = re.sub(r"(?<!')'(?=.*')", "''", line)
            # 但要避免转义已经转义的引号
            fixed_line = re.sub(r"''(?=')", "'", fixed_line)
            
            # 如果原始方法更好，就使用原始方法
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # 使用原来的修复方法，但更加精确
    content = '\n'.join(fixed_lines)
    
    # 专门修复引号问题：将内容中的单引号转义为两个单引号
    # 这个正则表达式会查找INSERT语句中的单引号并转义
    insert_pattern = r'(INSERT INTO [^;]*VALUES\s*\([^)]*)\''([^)]*\'\s*\d+\s*\)\s*;?'
    
    # 更简单的方式：直接将所有的INSERT语句中的单引号转义
    # 分割内容，处理每个INSERT部分
    parts = content.split('INSERT INTO')
    
    processed_parts = [parts[0]]  # 第一部分不需要处理
    
    for part in parts[1:]:
        # 将单引号转义为两个单引号（SQLite的转义方式）
        # 但要小心不要转义已经是转义的单引号
        processed_part = re.sub(r"(?<!')'(?=.*?')", "''", part)
        processed_parts.append(processed_part)
    
    content = 'INSERT INTO' + 'INSERT INTO'.join(processed_parts[1:])
    
    # 特别处理有问题的行
    content = content.replace(
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\",",
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\"),"
    )
    
    # 保存修复后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed SQL file saved to {output_file}")

if __name__ == "__main__":
    fix_sqlite_sql('sqlite.sql', 'sqlite_fixed.sql')