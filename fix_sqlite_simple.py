#!/usr/bin/env python3
import re

def fix_sqlite_sql(input_file, output_file):
    """
    修复SQLite SQL文件中的转义字符和语法错误
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复第515行的截断问题 - 这是主要问题
    content = content.replace(
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\",",
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\"),"
    )
    
    # 现在修复引号问题：在SQLite中，单引号需要用两个单引号转义
    # 但要小心，只处理实际的字符串内容，而不是SQL语法中的引号
    
    # 使用更简单直接的方法：找到INSERT语句中的VALUES部分，并正确转义其中的单引号
    lines = content.split('\n')
    new_lines = []
    in_insert_values = False
    
    for line in lines:
        original_line = line
        
        # 检查是否是INSERT语句的开始
        if 'INSERT INTO' in line and 'VALUES' in line:
            # 这一行包含INSERT和VALUES，转义其中的单引号
            # 但保留 'VALUES' 这样的SQL关键字
            new_line = ""
            i = 0
            in_string = False
            quote_char = None
            
            while i < len(line):
                char = line[i]
                
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
                        # 这是字符串内部的引号，需要转义
                        if char == "'":
                            new_line += "''"  # SQLite转义单引号的方式
                        else:
                            new_line += char
                else:
                    new_line += char
                i += 1
            
            line = new_line
        elif in_insert_values and ');' not in line.lower() and ');' not in line:
            # 如果在INSERT VALUES中间的行，同样处理单引号
            new_line = ""
            i = 0
            in_string = False
            quote_char = None
            
            while i < len(line):
                char = line[i]
                
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
                        # 这是字符串内部的引号，需要转义
                        if char == "'":
                            new_line += "''"  # SQLite转义单引号的方式
                        else:
                            new_line += char
                else:
                    new_line += char
                i += 1
            
            line = new_line
        elif ');' in line or ');\n' in line or line.strip().endswith(';'):
            # 如果是INSERT语句的结尾，重置标志
            in_insert_values = False
            line = original_line
        else:
            line = original_line
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # 保存修复后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed SQL file saved to {output_file}")

if __name__ == "__main__":
    fix_sqlite_sql('sqlite.sql', 'sqlite_fixed.sql')