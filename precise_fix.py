#!/usr/bin/env python3
import re

def fix_sqlite_file(input_file, output_file):
    """
    精确修复SQLite文件中的转义问题
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分行处理，以便区分CREATE语句和INSERT语句
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 检查是否是INSERT语句
        if line.strip().upper().startswith('INSERT'):
            # 对INSERT语句中的内容进行特殊处理
            # 1. 修复 \r\n 转义
            line = line.replace('\\r\\n', '\\\\r\\\\n')
            # 2. 修复单引号转义（只处理内容部分，不处理语法部分）
            # 使用正则表达式来识别INSERT语句中的字符串值
            # 找到 VALUES 部分并处理其中的单引号
            if 'VALUES' in line.upper():
                # 使用状态机来处理字符串
                new_line = ""
                i = 0
                in_string = False
                quote_char = None
                
                while i < len(line):
                    char = line[i]
                    
                    # 检查是否是转义字符
                    if char == '\\' and i + 1 < len(line) and line[i+1] in ['\\', '"', "'"]:
                        new_line += line[i:i+2]
                        i += 2
                        continue
                    
                    if char in ["'", '"']:
                        if not in_string:
                            # 开始一个字符串
                            in_string = True
                            quote_char = char
                            new_line += char
                        elif char == quote_char:
                            # 结束当前字符串
                            in_string = False
                            quote_char = None
                            new_line += char
                        else:
                            # 这是字符串内部的引号，需要转义（如果是单引号）
                            if char == "'":
                                new_line += "''"  # SQLite转义单引号的方式
                            else:
                                new_line += char
                    else:
                        new_line += char
                    i += 1
                
                line = new_line
        else:
            # 对于非INSERT语句，只修复 \r\n 转义
            line = line.replace('\\r\\n', '\\\\r\\\\n')
        
        fixed_lines.append(line)
    
    # 修复截断的行（第515行问题）
    content = '\n'.join(fixed_lines)
    content = content.replace(
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\",",
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\\\r\\\\n<div>&nbsp;</div>\\\\r\\\\n<div><span style=\"font-size: small\"><strong>\"),"
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_sqlite_file('sqlite.sql', 'sqlite_fixed.sql')