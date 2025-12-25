#!/usr/bin/env python3
"""
MySQL to SQLite 3 转换脚本
适用于 sino.sql 文件
用法: python3 convert_mysql_to_sqlite.py sino.sql sino_sqlite.sql
"""

import re
import sys

def convert_mysql_to_sqlite(input_file, output_file):
    """
    主转换函数
    """
    print(f"正在读取文件: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
        return False
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return False

    print("正在进行语法转换...")

    # 1. 移除MySQL特定的设置和注释块
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'--[^\n]*', '', content)
    content = re.sub(r'SET SQL_MODE[^;]*;', '', content)
    content = re.sub(r"\/\*!40101 SET[^;]*;", '', content)

    # 2. 转换 CREATE TABLE 语句
    # 2.1 移除表名和字段名的反引号，替换为双引号（SQLite标准）
    content = re.sub(r'`([^`]+)`', r'"\1"', content)

    # 2.2 处理 AUTO_INCREMENT -> AUTOINCREMENT 并设置为 INTEGER PRIMARY KEY
    # 匹配模式：字段定义中包含 AUTO_INCREMENT
    def replace_auto_increment(match):
        field_def = match.group(1)  # 捕获字段定义
        field_name = match.group(2) # 捕获字段名
        # 将当前字段定义替换为 INTEGER PRIMARY KEY AUTOINCREMENT
        return f'"{field_name}" INTEGER PRIMARY KEY AUTOINCREMENT'

    # 正则表达式匹配类似 `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT
    content = re.sub(
        r'"(\w+)"\s+(?:tiny|small|medium|big)?int[^)]*\)?\s+(?:unsigned\s+)?NOT NULL\s+AUTO_INCREMENT',
        replace_auto_increment,
        content,
        flags=re.IGNORECASE
    )

    # 2.3 移除所有字段的 UNSIGNED 属性
    content = re.sub(r'\s+UNSIGNED', '', content, flags=re.IGNORECASE)

    # 2.4 转换所有整数类型为 INTEGER
    content = re.sub(r'\b(TINYINT|SMALLINT|MEDIUMINT|INT|BIGINT)\s*(\(\d+\))?', 'INTEGER', content, flags=re.IGNORECASE)

    # 2.5 转换 ENUM 类型为 TEXT
    # 先提取ENUM定义，以便后续可能需要添加CHECK约束（此脚本暂只转换类型）
    content = re.sub(r'\bENUM\([^)]+\)', 'TEXT', content, flags=re.IGNORECASE)

    # 2.6 移除字段和表的 COMMENT
    content = re.sub(r"COMMENT\s+'[^']*'", '', content, flags=re.IGNORECASE)

    # 2.7 移除 ENGINE, DEFAULT CHARSET, AUTO_INCREMENT=xx 等表选项
    content = re.sub(r'\)\s*ENGINE\s*=\s*\w+\s*(DEFAULT\s+CHARSET\s*=\s*\w+\s*)?(AUTO_INCREMENT\s*=\s*\d+\s*)?;', ');', content, flags=re.IGNORECASE)

    # 3. 处理数据 INSERT 语句
    # 3.1 将 INSERT 语句中的反引号也替换为双引号
    # 注意：这里需要小心处理，确保只替换表名和字段名部分
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().upper().startswith('INSERT'):
            # 替换 INSERT INTO `table` (...) 中的反引号
            line = re.sub(r'`([^`]+)`', r'"\1"', line)
        new_lines.append(line)
    content = '\n'.join(new_lines)

    # 3.2 修复可能存在的零日期 '0000-00-00'，转换为 NULL
    content = re.sub(r"'0000-00-00'", "NULL", content)
    content = re.sub(r"'0000-00-00 00:00:00'", "NULL", content)

    # 4. 确保每个语句以分号结束
    # 移除多余的空行和空格
    content = re.sub(r'\n\s*\n', '\n', content)
    content = content.strip()

    print(f"正在写入转换后的文件: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("转换完成！")
        return True
    except Exception as e:
        print(f"写入文件时出错: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("用法: python3 convert_mysql_to_sqlite.py <输入文件.sql> <输出文件.sql>")
        print("示例: python3 convert_mysql_to_sqlite.py sino.sql sino_sqlite.sql")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if convert_mysql_to_sqlite(input_file, output_file):
        print("\n下一步操作:")
        print(f"1. 检查转换后的文件: {output_file}")
        print(f"2. 导入到SQLite数据库: sqlite3 your_database.db < {output_file}")
        print(f"3. 验证数据: sqlite3 your_database.db \".tables\" 和 \"SELECT count(*) FROM 表名;\"")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
