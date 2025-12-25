#!/usr/bin/env python3
"""
将MySQL dump文件转换为SQLite兼容的SQL文件
"""

import re
import sys

def convert_mysql_to_sqlite_sql(input_file, output_file):
    """将MySQL dump文件转换为SQLite兼容的SQL文件"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除MySQL特定的设置和注释
    patterns_to_remove = [
        r'SET SQL_MODE=.*?;',
        r'SET @OLD_CHARACTER_SET_CLIENT.*?;',
        r'SET @OLD_COLLATION_CONNECTION.*?;',
        r'SET NAMES.*?;',
        r'CREATE DATABASE.*?;',
        r'USE .*?;',
        r'/\*![^*]*40101 SET[^*]*\*/;',
        r'/\*![^*]*40014 SET[^*]*\*/;',
        r'/\*![^*]*40000 ALTER[^*]*\*/;',
        r'LOCK TABLES.*?;',
        r'UNLOCK TABLES.*?;',
        r'--.*',
        r'/\*!.*?\*/;',  # MySQL条件注释
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # 替换反引号为双引号
    content = content.replace('`', '"')
    
    # 转换数据类型
    replacements = [
        # 处理各种整数类型
        (r'\bTINYINT\(\d+\)\s+UNSIGNED', 'INTEGER'),
        (r'\bSMALLINT\(\d+\)\s+UNSIGNED', 'INTEGER'),
        (r'\bMEDIUMINT\(\d+\)\s+UNSIGNED', 'INTEGER'),
        (r'\bINT\(\d+\)\s+UNSIGNED', 'INTEGER'),
        (r'\bINTEGER\(\d+\)\s+UNSIGNED', 'INTEGER'),
        (r'\bBIGINT\(\d+\)\s+UNSIGNED', 'INTEGER'),
        (r'\bTINYINT\(\d+\)', 'INTEGER'),
        (r'\bSMALLINT\(\d+\)', 'INTEGER'),
        (r'\bMEDIUMINT\(\d+\)', 'INTEGER'),
        (r'\bINT\(\d+\)', 'INTEGER'),
        (r'\bINTEGER\(\d+\)', 'INTEGER'),
        (r'\bBIGINT\(\d+\)', 'INTEGER'),
        
        # 处理浮点数类型
        (r'\bFLOAT\(\d+,\s*\d+\)', 'REAL'),
        (r'\bDOUBLE\(\d+,\s*\d+\)', 'REAL'),
        (r'\bDECIMAL\(\d+,\s*\d+\)', 'REAL'),
        (r'\bDECIMAL', 'REAL'),
        
        # 处理字符串类型
        (r'\bVARCHAR\((\d+)\)', 'TEXT'),
        (r'\bCHAR\((\d+)\)', 'TEXT'),
        (r'\bTINYTEXT', 'TEXT'),
        (r'\bMEDIUMTEXT', 'TEXT'),
        (r'\bLONGTEXT', 'TEXT'),
        
        # 处理二进制类型
        (r'\bTINYBLOB', 'BLOB'),
        (r'\bMEDIUMBLOB', 'BLOB'),
        (r'\bLONGBLOB', 'BLOB'),
        (r'\bBLOB', 'BLOB'),
        (r'\bVARBINARY\((\d+)\)', 'BLOB'),
        
        # 处理日期时间类型
        (r'\bDATETIME', 'TEXT'),
        (r'\bTIMESTAMP', 'TEXT'),
        (r'\bTIME', 'TEXT'),
        (r'\bYEAR', 'INTEGER'),
        
        # 处理枚举类型
        (r'\bENUM\([^)]+\)', 'TEXT'),
        (r'\bSET\([^)]+\)', 'TEXT'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # 处理 AUTO_INCREMENT
    content = re.sub(r'AUTO_INCREMENT\s*=\s*\d+', '', content)
    content = re.sub(r'(\s+INTEGER|\s+INT)\s+AUTO_INCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    
    # 移除字段注释
    content = re.sub(r"COMMENT\s+'[^']*'", '', content)
    
    # 移除表选项
    content = re.sub(r'ENGINE\s*=\s*\w+', '', content)
    content = re.sub(r'DEFAULT CHARSET\s*=\s*\w+', '', content)
    content = re.sub(r'CHARSET\s*=\s*\w+', '', content)
    content = re.sub(r'COLLATE\s*=\s*\w+', '', content)
    
    # 处理零日期
    content = re.sub(r"'0000-00-00'", 'NULL', content)
    content = re.sub(r"'0000-00-00 00:00:00'", 'NULL', content)
    
    # 移除 UNSIGNED
    content = re.sub(r'\s+UNSIGNED', '', content, flags=re.IGNORECASE)
    
    # 移除可能的额外逗号
    content = re.sub(r',(\s*[)]\s*[,;])', r'\1', content)
    
    # 清理多余的空白行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # 确保每个语句以分号结束
    content = re.sub(r'(\s*\n)(CREATE TABLE|INSERT INTO|DROP TABLE|ALTER TABLE)', r';\n\2', content)
    
    # 为每个CREATE TABLE语句添加IF NOT EXISTS
    content = re.sub(r'CREATE TABLE(\s+)(\w+)', r'CREATE TABLE IF NOT EXISTS\1\2', content)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    
    print(f"转换完成: {input_file} -> {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 convert_to_sqlite_sql.py <input.sql> <output.sql>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    convert_mysql_to_sqlite_sql(input_file, output_file)