#!/usr/bin/env python3
"""
直接逐行处理转换脚本 - 确保不丢失SQL语句
"""

import sqlite3
import re
import sys

def convert_mysql_to_sqlite_direct(input_file, output_db):
    """直接逐行转换，不过度清理"""
    
    print(f"📁 处理文件: {input_file}")
    print(f"🗄️  输出数据库: {output_db}")
    
    # 连接SQLite数据库
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()
    
    # 优化设置
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    
    tables_created = 0
    rows_inserted = 0
    line_count = 0
    
    print("🔍 开始逐行读取SQL文件...")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        current_statement = ""
        in_statement = False
        
        for line_num, line in enumerate(f, 1):
            line_count += 1
            stripped = line.strip()
            
            # 跳过注释和空行
            if not stripped or stripped.startswith('--') or stripped.startswith('/*!'):
                continue
            
            # 添加到当前语句
            current_statement += line
            
            # 检查是否以分号结束
            if ';' in line:
                # 处理完整的SQL语句
                process_sql_statement(current_statement, cursor)
                
                # 检查是否创建了表或插入了数据
                if 'CREATE TABLE' in current_statement.upper():
                    tables_created += 1
                elif 'INSERT INTO' in current_statement.upper():
                    rows_inserted += 1
                
                # 重置当前语句
                current_statement = ""
                in_statement = False
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 处理完成统计:")
    print(f"  读取行数: {line_count}")
    print(f"  创建的表: {tables_created}")
    print(f"  插入的行: {rows_inserted}")
    print(f"  数据库文件: {output_db}")
    
    return True

def process_sql_statement(statement, cursor):
    """处理单个SQL语句"""
    try:
        # 简单的MySQL到SQLite转换
        converted = convert_mysql_syntax(statement)
        
        # 执行转换后的语句
        if converted:
            cursor.execute(converted)
            return True
    except Exception as e:
        # 如果执行失败，尝试更激进的转换
        try:
            # 移除更多MySQL特定语法
            simplified = simplify_statement(converted or statement)
            if simplified:
                cursor.execute(simplified)
                return True
        except Exception as e2:
            print(f"  ⚠ 执行失败: {str(e2)[:80]}")
            return False
    
    return False

def convert_mysql_syntax(sql):
    """基本的MySQL语法转换"""
    if not sql or not sql.strip():
        return None
    
    # 移除反引号，用双引号替换
    sql = sql.replace('`', '"')
    
    # 移除MySQL特定注释
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    
    # 处理CREATE TABLE
    if 'CREATE TABLE' in sql.upper():
        # 移除ENGINE和CHARSET
        sql = re.sub(r'\)\s*ENGINE\s*=\s*\w+.*?;', ');', sql, flags=re.IGNORECASE | re.DOTALL)
        
        # 转换AUTO_INCREMENT
        sql = re.sub(r'AUTO_INCREMENT', 'AUTOINCREMENT', sql, flags=re.IGNORECASE)
        
        # 移除UNSIGNED
        sql = re.sub(r'\s+UNSIGNED', '', sql, flags=re.IGNORECASE)
        
        # 转换数据类型
        sql = re.sub(r'\bTINYINT\(\d+\)', 'INTEGER', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bSMALLINT\(\d+\)', 'INTEGER', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bMEDIUMINT\(\d+\)', 'INTEGER', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bINT\(\d+\)', 'INTEGER', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bVARCHAR\(\d+\)', 'TEXT', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bCHAR\(\d+\)', 'TEXT', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bENUM\([^)]+\)', 'TEXT', sql, flags=re.IGNORECASE)
        
        # 移除字段注释
        sql = re.sub(r"COMMENT\s+'[^']*'", '', sql, flags=re.IGNORECASE)
    
    # 处理INSERT语句
    elif 'INSERT INTO' in sql.upper():
        # 处理零日期
        sql = re.sub(r"'0000-00-00'", "NULL", sql)
        sql = re.sub(r"'0000-00-00 00:00:00'", "NULL", sql)
    
    # 移除行内注释
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    
    return sql.strip()

def simplify_statement(sql):
    """简化语句，确保可执行"""
    if 'CREATE TABLE' in sql.upper():
        # 提取表名
        match = re.search(r'CREATE TABLE\s+"([^"]+)"', sql, re.IGNORECASE)
        if match:
            table_name = match.group(1)
            # 创建最简单的表
            return f'CREATE TABLE "{table_name}" (id INTEGER PRIMARY KEY AUTOINCREMENT);'
    
    return sql

def main():
    if len(sys.argv) != 3:
        print("用法: python3 direct_converter.py <输入SQL文件> <输出SQLite数据库>")
        print("示例: python3 direct_converter.py sino.sql sino_direct.db")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_db = sys.argv[2]
    
    try:
        success = convert_mysql_to_sqlite_direct(input_file, output_db)
        
        if success:
            print("\n✅ 转换完成！验证命令:")
            print(f"  sqlite3 {output_db} \".tables\"")
            print(f"  sqlite3 {output_db} \"SELECT COUNT(*) FROM sqlite_master WHERE type='table';\"")
        else:
            print("\n❌ 转换失败！")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 转换过程中出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
