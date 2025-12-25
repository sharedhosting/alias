#!/usr/bin/env python3
"""
最终修复版：将MySQL dump文件转换为SQLite兼容的SQL文件
"""

import re

def convert_mysql_to_sqlite_sql(input_file, output_file):
    """将MySQL dump文件转换为SQLite兼容的SQL文件"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 移除MySQL特定的设置和注释
    # 处理MySQL条件注释 /*![数字] ... */
    content = re.sub(r'/\*![0-9]+\s[^*]*(?:\*(?!/)[^*]*)*\*/', '', content)
    # 处理单行注释
    content = re.sub(r'--.*?\n', '\n', content)
    # 处理SET语句
    content = re.sub(r'SET [^;]*;', '', content)
    # 处理数据库相关语句
    content = re.sub(r'(CREATE DATABASE|USE)[^;]*;', '', content)
    # 处理LOCK/UNLOCK语句
    content = re.sub(r'(LOCK TABLES|UNLOCK TABLES)[^;]*;', '', content)
    
    # 2. 替换反引号为双引号
    content = content.replace('`', '"')
    
    # 3. 转换数据类型 - 修正顺序，先处理复杂的再处理简单的
    # 整数类型
    content = re.sub(r'\bTINYINT\(\d+\)\s+UNSIGNED\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bSMALLINT\(\d+\)\s+UNSIGNED\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bMEDIUMINT\(\d+\)\s+UNSIGNED\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bINT\(\d+\)\s+UNSIGNED\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bINTEGER\(\d+\)\s+UNSIGNED\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bBIGINT\(\d+\)\s+UNSIGNED\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bTINYINT\(\d+\)\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bSMALLINT\(\d+\)\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bMEDIUMINT\(\d+\)\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bINT\(\d+\)\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bINTEGER\(\d+\)\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bBIGINT\(\d+\)\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bTINYINT\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bSMALLINT\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bMEDIUMINT\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bINT\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bINTEGER\b', 'INTEGER', content, flags=re.IGNORECASE)
    content = re.sub(r'\bBIGINT\b', 'INTEGER', content, flags=re.IGNORECASE)
    
    # 浮点数类型
    content = re.sub(r'\bFLOAT\(\d+,\s*\d+\)\b', 'REAL', content, flags=re.IGNORECASE)
    content = re.sub(r'\bDOUBLE\(\d+,\s*\d+\)\b', 'REAL', content, flags=re.IGNORECASE)
    content = re.sub(r'\bDECIMAL\(\d+,\s*\d+\)\b', 'REAL', content, flags=re.IGNORECASE)
    content = re.sub(r'\bDECIMAL\b', 'REAL', content, flags=re.IGNORECASE)
    content = re.sub(r'\bFLOAT\b', 'REAL', content, flags=re.IGNORECASE)
    content = re.sub(r'\bDOUBLE\b', 'REAL', content, flags=re.IGNORECASE)
    
    # 字符串类型
    content = re.sub(r'\bVARCHAR\((\d+)\)\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bCHAR\((\d+)\)\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bTINYTEXT\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bMEDIUMTEXT\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bLONGTEXT\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\blongtext\b', 'TEXT', content, flags=re.IGNORECASE)
    
    # 二进制类型
    content = re.sub(r'\bTINYBLOB\b', 'BLOB', content, flags=re.IGNORECASE)
    content = re.sub(r'\bMEDIUMBLOB\b', 'BLOB', content, flags=re.IGNORECASE)
    content = re.sub(r'\bLONGBLOB\b', 'BLOB', content, flags=re.IGNORECASE)
    content = re.sub(r'\bBLOB\b', 'BLOB', content, flags=re.IGNORECASE)
    content = re.sub(r'\bVARBINARY\((\d+)\)\b', 'BLOB', content, flags=re.IGNORECASE)
    
    # 日期时间类型
    content = re.sub(r'\bDATETIME\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bTIMESTAMP\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bTIME\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bYEAR\b', 'INTEGER', content, flags=re.IGNORECASE)
    
    # 枚举和集合类型 - 需要处理单引号中的内容
    content = re.sub(r'\bENUM\s*\([^)]+\)\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\benum\s*\([^)]+\)\b', 'TEXT', content, flags=re.IGNORECASE)
    content = re.sub(r'\bSET\s*\([^)]+\)\b', 'TEXT', content, flags=re.IGNORECASE)
    
    # 4. 处理 AUTO_INCREMENT
    content = re.sub(r'\s+AUTO_INCREMENT\s*=\s*\d+', '', content)
    content = re.sub(r'\s+AUTO_INCREMENT\b', '', content)
    # 修复自增主键
    content = re.sub(r'(\s+INTEGER|\s+TEXT)\s+NOT\s+NULL\s+INTEGER PRIMARY KEY AUTOINCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL', content, flags=re.IGNORECASE)
    content = re.sub(r'(\s+INTEGER|\s+TEXT)\s+INTEGER PRIMARY KEY AUTOINCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    content = re.sub(r'(\s+INTEGER)\s+PRIMARY KEY\s+AUTOINCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    content = re.sub(r'(\s+INTEGER)\s+AUTO_INCREMENT', r' INTEGER PRIMARY KEY AUTOINCREMENT', content, flags=re.IGNORECASE)
    
    # 5. 移除字段注释
    content = re.sub(r"COMMENT\s+'[^']*'", '', content)
    
    # 6. 移除表选项
    content = re.sub(r'ENGINE\s*=\s*\w+', '', content)
    content = re.sub(r'DEFAULT CHARSET\s*=\s*\w+', '', content)
    content = re.sub(r'CHARSET\s*=\s*\w+', '', content)
    content = re.sub(r'COLLATE\s*=\s*\w+', '', content)
    content = re.sub(r'AUTO_INCREMENT\s*=\s*\d+', '', content)
    
    # 7. 处理零日期
    content = re.sub(r"'0000-00-00'", 'NULL', content)
    content = re.sub(r"'0000-00-00 00:00:00'", 'NULL', content)
    
    # 8. 移除 UNSIGNED
    content = re.sub(r'\s+UNSIGNED\b', '', content, flags=re.IGNORECASE)
    
    # 9. 移除 KEY 定义（索引）
    content = re.sub(r',\s*\n?\s*KEY\s+"?[\w_]+"?\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    content = re.sub(r',\s*\n?\s*UNIQUE KEY\s+"?[\w_]+"?\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    content = re.sub(r',\s*\n?\s*PRIMARY KEY\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'KEY\s+"?[\w_]+"?\s*\([^)]+\),?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'UNIQUE KEY\s+"?[\w_]+"?\s*\([^)]+\),?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'PRIMARY KEY\s*\([^)]+\),?', '', content, flags=re.IGNORECASE)
    
    # 10. 移除可能的额外逗号
    content = re.sub(r',(\s*[)]\s*(?:,|;))', r'\1', content)
    content = re.sub(r',(\s*[)]\s*CREATE)', r'\1', content)
    
    # 11. 修复重复的IF NOT EXISTS
    content = re.sub(r'CREATE TABLE IF NOT EXISTS IF NOT EXISTS', 'CREATE TABLE IF NOT EXISTS', content)
    
    # 12. 修复可能的语法问题
    content = re.sub(r'\(\s*,', '(', content)
    
    # 13. 清理多余的空白行和重复分号
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = re.sub(r';\s*;', ';', content)
    
    # 14. 移除开头的分号
    content = re.sub(r'^\s*;', '', content)
    content = re.sub(r'^\s*\n', '', content)
    
    # 15. 确保每个语句以分号结束
    content = re.sub(r'(\s*\n)(CREATE TABLE|INSERT INTO|DROP TABLE|ALTER TABLE)', r';\n\2', content)
    
    # 16. 最后清理
    content = content.strip()
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"转换完成: {input_file} -> {output_file}")
    print(f"文件大小: {len(content)} 字符")

if __name__ == '__main__':
    convert_mysql_to_sqlite_sql('/workspace/sino.sql', '/workspace/sqlite.sql')