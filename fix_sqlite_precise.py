#!/usr/bin/env python3

def fix_sqlite_sql(input_file, output_file):
    """
    精确修复SQLite SQL文件中的特定错误
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复第一个问题：在第380行附近的反斜杠转义问题
    # 将 \r\n 转换为正确的转义序列
    # 在SQLite中，反斜杠需要被转义为 \\
    content = content.replace('\\r\\n', '\\\\r\\\\n')
    
    # 修复第二个问题：第515行的截断问题
    content = content.replace(
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\r\\n<div>&nbsp;</div>\\r\\n<div><span style=\"font-size: small\"><strong>\",",
        "(4, 0, 'Company Intro', 'font-weight:bold;', '<div>&nbsp;</div>\\\\r\\\\n<div>&nbsp;</div>\\\\r\\\\n<div><span style=\"font-size: small\"><strong>\"),"
    )
    
    # 修复其他地方的 \r\n 序列
    import re
    # 修复所有独立的 \r 和 \n 转义序列
    content = re.sub(r'(?<!\\)\\r(?=\\|")', r'\\\\r', content)
    content = re.sub(r'(?<!\\)\\n(?=\\|")', r'\\\\n', content)
    content = re.sub(r'(?<!\\)\\t(?=\\|")', r'\\\\t', content)
    
    # 在SQLite中，单引号用两个单引号转义
    # 但我们需要小心只转义内容中的单引号，而不是SQL语法中的
    lines = content.split('\n')
    new_content = []
    
    for line in lines:
        # 检查是否是INSERT语句的行
        if 'INSERT INTO' in line and ('VALUES' in line or line.count("'") >= 2):
            # 转义内容中的单引号，但不转义SQL语法中的单引号
            # 使用状态机来跟踪是否在字符串中
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
            
            new_content.append(new_line)
        else:
            new_content.append(line)
    
    content = '\n'.join(new_content)
    
    # 保存修复后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed SQL file saved to {output_file}")

if __name__ == "__main__":
    fix_sqlite_sql('sqlite.sql', 'sqlite_fixed.sql')