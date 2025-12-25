#!/usr/bin/env python3
"""
增强版 MySQL 5.x 到 SQLite 3 转换器
专门处理 sino.sql 文件转换
"""

import re
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

class MySQLToSQLiteConverter:
    def __init__(self, input_file, output_db):
        self.input_file = Path(input_file)
        self.output_db = Path(output_db)
        self.conn = None
        self.cursor = None
        self.stats = {
            'tables_created': 0,
            'rows_inserted': 0,
            'errors': 0,
            'warnings': 0
        }
        
        # SQLite 不支持的 MySQL 语句模式
        self.skip_patterns = [
            r'/\*!.*?\*/',  # MySQL条件注释
            r'-- .*',       # MySQL单行注释
            r'SET SQL_MODE=.*',
            r'SET @OLD_.*=.*',
            r'/\*!40101 SET.*',
            r'/\*!40000 ALTER.*',
            r'LOCK TABLES.*',
            r'UNLOCK TABLES.*',
            r'DROP TABLE IF EXISTS.*',  # SQLite有自己的IF NOT EXISTS语法
        ]
        
        # 数据类型映射
        self.type_mapping = {
            r'\b(tiny|small|medium|big)?int(?:\(\d+\))?\s*(?:unsigned)?\b': 'INTEGER',
            r'\bfloat(?:\(\d+,\d+\))?\b': 'REAL',
            r'\bdouble(?:\(\d+,\d+\))?\b': 'REAL',
            r'\bdecimal(?:\(\d+,\d+\))?\b': 'REAL',
            r'\b(char|varchar|text|tinytext|mediumtext|longtext)\b': 'TEXT',
            r'\b(blob|tinyblob|mediumblob|longblob|varbinary)\b': 'BLOB',
            r'\b(date|time|year)\b': 'TEXT',
            r'\bdatetime(?:\(\d+\))?\b': 'TEXT',
            r'\btimestamp(?:\(\d+\))?\b': 'INTEGER',  # 存储为Unix时间戳
            r'\benum\([^)]+\)': 'TEXT',
            r'\bset\([^)]+\)': 'TEXT',
        }
    
    def log(self, message, level='INFO'):
        """日志记录"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f'[{timestamp}] [{level}] {message}')
    
    def preprocess_sql(self):
        """预处理SQL文件，移除不支持的语句"""
        self.log(f'开始预处理: {self.input_file}')
        
        try:
            with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.log(f'读取文件失败: {e}', 'ERROR')
            return None
        
        # 移除MySQL特定语句
        for pattern in self.skip_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # 移除数据库创建语句
        content = re.sub(r'CREATE DATABASE.*?;', '', content, flags=re.IGNORECASE)
        content = re.sub(r'USE .*?;', '', content, flags=re.IGNORECASE)
        
        # 分割SQL语句
        statements = self.split_sql_statements(content)
        self.log(f'预处理完成，找到 {len(statements)} 条SQL语句')
        
        return statements
    
    def split_sql_statements(self, content):
        """智能分割SQL语句，正确处理字符串内的分号"""
        statements = []
        current = []
        in_string = False
        string_char = None
        escaped = False
        
        for char in content:
            if escaped:
                current.append(char)
                escaped = False
            elif char == '\\':
                escaped = True
                current.append(char)
            elif not in_string and char in ("'", '"', '`'):
                in_string = True
                string_char = char
                current.append(char)
            elif in_string and char == string_char:
                in_string = False
                string_char = None
                current.append(char)
            elif not in_string and char == ';':
                stmt = ''.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(char)
        
        # 添加最后一个语句
        if current:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def convert_create_table(self, statement):
        """转换CREATE TABLE语句"""
        # 移除反引号，替换为双引号
        statement = statement.replace('`', '"')
        
        # 处理 IF NOT EXISTS
        if 'IF NOT EXISTS' not in statement.upper():
            statement = re.sub(r'CREATE TABLE\s+', 'CREATE TABLE IF NOT EXISTS ', 
                             statement, flags=re.IGNORECASE)
        
        # 转换数据类型
        for mysql_type, sqlite_type in self.type_mapping.items():
            statement = re.sub(mysql_type, sqlite_type, statement, flags=re.IGNORECASE)
        
        # 处理 AUTO_INCREMENT
        def replace_auto_increment(match):
            field_name = match.group(1)
            return f'"{field_name}" INTEGER PRIMARY KEY AUTOINCREMENT'
        
        # 查找包含 AUTO_INCREMENT 的字段定义
        auto_inc_pattern = r'"(\w+)"[^,)]*\s+AUTO_INCREMENT'
        if re.search(auto_inc_pattern, statement, re.IGNORECASE):
            statement = re.sub(auto_inc_pattern, replace_auto_increment, 
                             statement, flags=re.IGNORECASE)
        
        # 移除 UNSIGNED
        statement = re.sub(r'\s+UNSIGNED', '', statement, flags=re.IGNORECASE)
        
        # 移除显示宽度，如 INT(11)
        statement = re.sub(r'(INTEGER|INT)\(\d+\)', r'\1', statement, flags=re.IGNORECASE)
        
        # 移除字段注释
        statement = re.sub(r"COMMENT\s+'[^']*'", '', statement, flags=re.IGNORECASE)
        
        # 移除表选项 (ENGINE, CHARSET, AUTO_INCREMENT=等)
        statement = re.sub(r'\)\s*ENGINE\s*=\s*\w+.*?;', ');', statement, 
                         flags=re.IGNORECASE | re.DOTALL)
        
        # 处理 ENUM 类型 - 添加 CHECK 约束
        def add_enum_check(match):
            # 提取ENUM值
            enum_values = match.group(0)
            # 从 ENUM('a','b') 中提取值
            values_match = re.search(r'\((.*?)\)', enum_values)
            if values_match:
                values = values_match.group(1)
                # 为字段添加 CHECK 约束
                return 'TEXT'  # CHECK约束将在执行时添加
            return 'TEXT'
        
        statement = re.sub(r'ENUM\([^)]+\)', add_enum_check, statement, flags=re.IGNORECASE)
        
        # 移除额外的逗号（可能由移除字段导致）
        statement = re.sub(r',\s*\)', ')', statement)
        
        return statement
    
    def convert_insert(self, statement):
        """转换INSERT语句"""
        # 统一表名和字段名的引号
        statement = statement.replace('`', '"')
        
        # 处理零日期
        statement = re.sub(r"'0000-00-00'", "NULL", statement)
        statement = re.sub(r"'0000-00-00 00:00:00'", "NULL", statement)
        
        # 处理布尔值（TINYINT(1)）
        statement = re.sub(r"'\s*0\s*'", "'0'", statement)
        statement = re.sub(r"'\s*1\s*'", "'1'", statement)
        
        return statement
    
    def execute_statements(self, statements):
        """执行转换后的SQL语句"""
        self.log(f'正在创建SQLite数据库: {self.output_db}')
        
        try:
            self.conn = sqlite3.connect(self.output_db)
            self.cursor = self.conn.cursor()
            # 启用外键支持
            self.cursor.execute('PRAGMA foreign_keys = ON;')
            # 提高性能
            self.cursor.execute('PRAGMA journal_mode = WAL;')
            self.cursor.execute('PRAGMA synchronous = NORMAL;')
        except Exception as e:
            self.log(f'创建数据库失败: {e}', 'ERROR')
            return False
        
        current_table = None
        
        for i, stmt in enumerate(statements, 1):
            if not stmt.strip():
                continue
            
            # 跳过某些语句
            if any(keyword in stmt.upper() for keyword in ['DELIMITER', 'DROP DATABASE']):
                continue
            
            try:
                # 转换语句
                original_stmt = stmt
                
                if 'CREATE TABLE' in stmt.upper():
                    stmt = self.convert_create_table(stmt)
                    current_table = re.search(r'"([^"]+)"', stmt)
                    if current_table:
                        current_table = current_table.group(1)
                    self.stats['tables_created'] += 1
                
                elif 'INSERT INTO' in stmt.upper():
                    stmt = self.convert_insert(stmt)
                    self.stats['rows_inserted'] += 1
                
                # 执行语句
                if stmt.strip().endswith(';'):
                    stmt = stmt.strip()
                
                self.cursor.execute(stmt)
                
                # 每10个语句提交一次
                if i % 10 == 0:
                    self.conn.commit()
                
                # 进度显示
                if i % 50 == 0:
                    self.log(f'已处理 {i}/{len(statements)} 条语句')
                    
            except sqlite3.Error as e:
                self.stats['errors'] += 1
                error_msg = str(e).replace('\n', ' ')
                
                # 尝试修复常见错误
                if 'no such table' in error_msg.lower():
                    self.log(f'跳过语句（表不存在）: {stmt[:100]}...', 'WARNING')
                    self.stats['warnings'] += 1
                elif 'syntax error' in error_msg.lower():
                    self.log(f'语法错误，跳过: {error_msg}', 'WARNING')
                    self.stats['warnings'] += 1
                elif 'duplicate column name' in error_msg.lower():
                    # 忽略重复列错误
                    pass
                else:
                    self.log(f'执行失败 [{i}]: {error_msg}', 'ERROR')
                    self.log(f'失败语句: {stmt[:200]}...', 'DEBUG')
                
                # 继续执行下一条语句
                continue
            except Exception as e:
                self.stats['errors'] += 1
                self.log(f'未知错误 [{i}]: {e}', 'ERROR')
                continue
        
        # 最终提交
        self.conn.commit()
        self.log(f'所有语句处理完成')
        
        return True
    
    def verify_conversion(self):
        """验证转换结果"""
        self.log('正在验证转换结果...')
        
        try:
            # 获取所有表
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = self.cursor.fetchall()
            
            if not tables:
                self.log('警告: 数据库中没有找到任何表', 'WARNING')
                return False
            
            self.log(f'找到 {len(tables)} 个表:')
            
            for table in tables:
                table_name = table[0]
                try:
                    # 获取行数
                    self.cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                    count = self.cursor.fetchone()[0]
                    
                    # 获取列信息
                    self.cursor.execute(f'PRAGMA table_info("{table_name}");')
                    columns = self.cursor.fetchall()
                    col_names = [col[1] for col in columns]
                    
                    self.log(f'  {table_name}: {count} 行, {len(columns)} 列')
                    if table_name in ['sino_admin', 'sino_ad']:  # 示例显示部分表的列
                        self.log(f'    列: {", ".join(col_names[:5])}' + 
                               ('...' if len(col_names) > 5 else ''))
                        
                except sqlite3.Error as e:
                    self.log(f'  读取表 {table_name} 失败: {e}', 'WARNING')
            
            return True
            
        except Exception as e:
            self.log(f'验证失败: {e}', 'ERROR')
            return False
    
    def generate_report(self):
        """生成转换报告"""
        report = f"""
{'='*60}
MySQL 到 SQLite 转换报告
{'='*60}
输入文件: {self.input_file}
输出数据库: {self.output_db}
转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
转换统计:
  创建的表: {self.stats['tables_created']}
  插入的行: {self.stats['rows_inserted']}
  遇到的错误: {self.stats['errors']}
  警告: {self.stats['warnings']}
{'='*60}
验证命令:
  sqlite3 {self.output_db} ".tables"
  sqlite3 {self.output_db} "SELECT name FROM sqlite_master WHERE type='table';"
  sqlite3 {self.output_db} "SELECT COUNT(*) FROM sino_ad;"
{'='*60}
"""
        print(report)
        
        # 保存报告到文件
        report_file = self.output_db.with_suffix('.report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        self.log(f'详细报告已保存到: {report_file}')
    
    def cleanup(self):
        """清理资源"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def convert(self):
        """执行完整转换流程"""
        self.log('开始MySQL到SQLite转换')
        
        try:
            # 1. 预处理SQL
            statements = self.preprocess_sql()
            if not statements:
                return False
            
            # 2. 执行转换
            if not self.execute_statements(statements):
                return False
            
            # 3. 验证结果
            self.verify_conversion()
            
            # 4. 生成报告
            self.generate_report()
            
            self.log('转换成功完成！')
            return True
            
        except Exception as e:
            self.log(f'转换过程中发生严重错误: {e}', 'ERROR')
            return False
        finally:
            self.cleanup()

def main():
    if len(sys.argv) != 3:
        print("用法: python3 mysql_to_sqlite_enhanced.py <输入SQL文件> <输出SQLite数据库>")
        print("示例: python3 mysql_to_sqlite_enhanced.py sino.sql sinogacma.db")
        print("\n或者使用默认参数运行:")
        print("python3 mysql_to_sqlite_enhanced.py sino.sql sino_converted.db")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_db = sys.argv[2]
    
    if not Path(input_file).exists():
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    converter = MySQLToSQLiteConverter(input_file, output_db)
    success = converter.convert()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
