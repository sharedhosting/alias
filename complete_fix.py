#!/usr/bin/env python3
import re

def complete_fix_sqlite(input_file, output_file):
    """
    完整修复SQLite文件的所有转义问题
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 首先备份原始内容
    original_content = content
    
    # 修复方法：将所有 \r\n 替换为纯文本，而不是转义序列
    # SQLite不能处理复杂的转义序列，所以我们替换为实际的换行
    content = content.replace('\\r\\n', '\\n')
    
    # 然后将 \n 替换为实际的换行符，但这在SQL字符串中是不行的
    # 所以我们需要将 \n 保持为字面量的 \\n (两个字符)
    content = content.replace('\\n', '\\\\n')
    content = content.replace('\\r', '\\\\r')
    
    # 修复截断的行
    content = content.replace(
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\",",
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\\\r\\\\n<div>&nbsp;</div>\\\\r\\\\n<div><span style=\"font-size: small\"><strong>\"),"
    )
    
    # 用更安全的方法处理单引号
    # 只在INSERT语句的值部分处理单引号
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.strip().upper().startswith('INSERT'):
            # 使用更精确的方法处理INSERT语句中的单引号
            # 避免在SQL语法部分（如列名）中转义单引号
            new_line = process_insert_line(line)
        else:
            new_line = line
        new_lines.append(new_line)
    
    content = '\n'.join(new_lines)
    
    # 写入修复后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def process_insert_line(line):
    """
    处理INSERT语句行，只转义值部分的单引号
    """
    # 简单的处理方法：找到VALUES关键字，只在VALUES之后的部分转义单引号
    if 'VALUES' not in line.upper():
        return line
    
    # 找到VALUES的位置
    values_pos = line.upper().find('VALUES')
    before_values = line[:values_pos + 6]  # +6 for 'VALUES'
    after_values = line[values_pos + 6:]
    
    # 在after_values部分转义单引号
    # 使用状态机来识别字符串并转义其中的单引号
    result = ""
    i = 0
    in_string = False
    quote_char = None
    
    while i < len(after_values):
        char = after_values[i]
        
        # 检查是否是转义字符
        if char == '\\' and i + 1 < len(after_values) and after_values[i+1] in ['\\', '"', "'"]:
            result += after_values[i:i+2]
            i += 2
            continue
        
        if char in ["'", '"']:
            if not in_string:
                # 开始一个字符串
                in_string = True
                quote_char = char
                result += char
            elif char == quote_char:
                # 结束当前字符串
                in_string = False
                quote_char = None
                result += char
            else:
                # 这是字符串内部的引号，需要转义（如果是单引号）
                if char == "'":
                    result += "''"  # SQLite转义单引号的方式
                else:
                    result += char
        else:
            result += char
        i += 1
    
    return before_values + result

if __name__ == "__main__":
    complete_fix_sqlite('sqlite.sql', 'sqlite_fixed.sql')