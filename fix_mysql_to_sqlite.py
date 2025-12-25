#!/usr/bin/env python3
"""
将MySQL dump文件转换为SQLite兼容的SQL文件
"""

import re

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
        r'SET @OLD.*?=.*?;',
        r'CREATE DATABASE.*?;',
        r'USE .*?;',
        r'/\*![^*]*40101 SET[^*]*\*/;',
        r'/\*![^*]*40014 SET[^*]*\*/;',
        r'/\*![^*]*40000 ALTER[^*]*\*/;',
        r'LOCK TABLES.*?;',
        r'UNLOCK TABLES.*?;',
        r'--.*?\n',
        r'/\*!.*?\*/;',
        r'/\*[^!].*?\*/',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # 替换反引号为双引号
    content = content.replace('`', '"')
    
    # 转换数据类型
    replacements = [
        # 处理各种整数类型
        (r'\bTINYINT\(\d+\)\s+UNSIGNED\b', 'INTEGER'),
        (r'\bSMALLINT\(\d+\)\s+UNSIGNED\b', 'INTEGER'),
        (r'\bMEDIUMINT\(\d+\)\s+UNSIGNED\b', 'INTEGER'),
        (r'\bINT\(\d+\)\s+UNSIGNED\b', 'INTEGER'),
        (r'\bINTEGER\(\d+\)\s+UNSIGNED\b', 'INTEGER'),
        (r'\bBIGINT\(\d+\)\s+UNSIGNED\b', 'INTEGER'),
        (r'\bTINYINT\(\d+\)\b', 'INTEGER'),
        (r'\bSMALLINT\(\d+\)\b', 'INTEGER'),
        (r'\bMEDIUMINT\(\d+\)\b', 'INTEGER'),
        (r'\bINT\(\d+\)\b', 'INTEGER'),
        (r'\bINTEGER\(\d+\)\b', 'INTEGER'),
        (r'\bBIGINT\(\d+\)\b', 'INTEGER'),
        (r'\bTINYINT\b', 'INTEGER'),
        (r'\bSMALLINT\b', 'INTEGER'),
        (r'\bMEDIUMINT\b', 'INTEGER'),
        (r'\bINT\b', 'INTEGER'),
        (r'\bINTEGER\b', 'INTEGER'),
        (r'\bBIGINT\b', 'INTEGER'),
        
        # 处理浮点数类型
        (r'\bFLOAT\(\d+,\s*\d+\)\b', 'REAL'),
        (r'\bDOUBLE\(\d+,\s*\d+\)\b', 'REAL'),
        (r'\bDECIMAL\(\d+,\s*\d+\)\b', 'REAL'),
        (r'\bDECIMAL\b', 'REAL'),
        (r'\bFLOAT\b', 'REAL'),
        (r'\bDOUBLE\b', 'REAL'),
        
        # 处理字符串类型
        (r'\bVARCHAR\((\d+)\)\b', 'TEXT'),
        (r'\bCHAR\((\d+)\)\b', 'TEXT'),
        (r'\bTINYTEXT\b', 'TEXT'),
        (r'\bMEDIUMTEXT\b', 'TEXT'),
        (r'\bLONGTEXT\b', 'TEXT'),
        (r'\blongtext\b', 'TEXT'),
        
        # 处理二进制类型
        (r'\bTINYBLOB\b', 'BLOB'),
        (r'\bMEDIUMBLOB\b', 'BLOB'),
        (r'\bLONGBLOB\b', 'BLOB'),
        (r'\bBLOB\b', 'BLOB'),
        (r'\bVARBINARY\((\d+)\)\b', 'BLOB'),
        
        # 处理日期时间类型
        (r'\bDATETIME\b', 'TEXT'),
        (r'\bTIMESTAMP\b', 'TEXT'),
        (r'\bTIME\b', 'TEXT'),
        (r'\bYEAR\b', 'INTEGER'),
        
        # 处理枚举类型
        (r'\bENUM\([^)]+\)\b', 'TEXT'),
        (r'\benum\([^)]+\)\b', 'TEXT'),
        (r'\bSET\([^)]+\)\b', 'TEXT'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # 处理 AUTO_INCREMENT
    content = re.sub(r'\s+AUTO_INCREMENT\s*=\s*\d+', '', content)
    content = re.sub(r'\s+AUTO_INCREMENT\b', '', content)
    content = re.sub(r'(\s+INTEGER|\s+INT|\s+TEXT)\s+NOT\s+NULL\s+INTEGER PRIMARY KEY AUTOINCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL', content, flags=re.IGNORECASE)
    content = re.sub(r'(\s+INTEGER|\s+INT|\s+TEXT)\s+INTEGER PRIMARY KEY AUTOINCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    content = re.sub(r'(\s+INTEGER|\s+INT)\s+PRIMARY KEY\s+AUTOINCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    content = re.sub(r'(\s+INTEGER|\s+INT)\s+AUTO_INCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    
    # 移除字段注释
    content = re.sub(r"COMMENT\s+'[^']*'", '', content)
    
    # 移除表选项
    content = re.sub(r'ENGINE\s*=\s*\w+', '', content)
    content = re.sub(r'DEFAULT CHARSET\s*=\s*\w+', '', content)
    content = re.sub(r'CHARSET\s*=\s*\w+', '', content)
    content = re.sub(r'COLLATE\s*=\s*\w+', '', content)
    content = re.sub(r'AUTO_INCREMENT\s*=\s*\d+', '', content)
    
    # 处理零日期
    content = re.sub(r"'0000-00-00'", 'NULL', content)
    content = re.sub(r"'0000-00-00 00:00:00'", 'NULL', content)
    
    # 移除 UNSIGNED
    content = re.sub(r'\s+UNSIGNED\b', '', content, flags=re.IGNORECASE)
    
    # 移除 KEY 定义（索引）
    content = re.sub(r',\s*\n?\s*KEY\s+"?[\w_]+"?\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    content = re.sub(r',\s*\n?\s*UNIQUE KEY\s+"?[\w_]+"?\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    content = re.sub(r',\s*\n?\s*PRIMARY KEY\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'KEY\s+"?[\w_]+"?\s*\([^)]+\),?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'UNIQUE KEY\s+"?[\w_]+"?\s*\([^)]+\),?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'PRIMARY KEY\s*\([^)]+\),?', '', content, flags=re.IGNORECASE)
    
    # 移除可能的额外逗号
    content = re.sub(r',(\s*[)]\s*(?:,|;))', r'\1', content)
    content = re.sub(r',(\s*[)]\s*CREATE)', r'\1', content)
    
    # 确保每行CREATE TABLE语句格式正确
    content = re.sub(r'CREATE TABLE(\s+)IF(\s+)NOT(\s+)EXISTS', 'CREATE TABLE IF NOT EXISTS', content)
    content = re.sub(r'CREATE TABLE(\s+)IF(\s+)NOT(\s+)EXISTS(\s+)(\w+)', r'CREATE TABLE IF NOT EXISTS \5', content)
    
    # 修复可能的语法问题
    content = re.sub(r'\(\s*,', '(', content)
    
    # 清理多余的空白行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # 确保每个语句以分号结束
    content = re.sub(r'(\s*\n)(CREATE TABLE|INSERT INTO|DROP TABLE|ALTER TABLE)', r';\n\2', content)
    
    # 为每个CREATE TABLE语句添加IF NOT EXISTS
    content = re.sub(r'CREATE TABLE(\s+)("?\w+"?)', r'CREATE TABLE IF NOT EXISTS \2', content)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    
    print(f"转换完成: {input_file} -> {output_file}")
    print(f"文件大小: {len(content)} 字符")

if __name__ == '__main__':
    convert_mysql_to_sqlite_sql('/workspace/sino.sql', '/workspace/sqlite.sql')