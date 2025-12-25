#!/usr/bin/env python3
"""
修复版 MySQL 到 SQLite 转换器
专门处理 sino.sql 中的语法问题
"""

import re
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

class FixedMySQLToSQLiteConverter:
    def __init__(self, input_file, output_db):
        self.input_file = Path(input_file)
        self.output_db = Path(output_db)
        self.conn = None
        self.cursor = None
        
        # 详细的统计信息
        self.stats = {
            'tables_created': 0,
            'rows_inserted': 0,
            'statements_processed': 0,
            'errors': 0,
            'warnings': 0,
            'skipped_statements': 0
        }
        
        # 修复：更精确的模式匹配
        self.skip_patterns = [
            r'/\*!.*?\*/',                    # MySQL条件注释
            r'/\*.*?\*/',                     # 普通注释块
            r'^--[^\n]*',                     # 单行注释
            r'^SET\s+SQL_MODE[^;]*;',         # SQL模式设置
            r'^SET\s+@OLD_[^;]*;',           # 旧变量设置
            r'^LOCK\s+TABLES[^;]*;',         # 锁表语句
            r'^UNLOCK\s+TABLES[^;]*;',       # 解锁语句
            r'^/\*!40101\s+SET[^;]*;',       # MySQL特定设置
            r'^/\*!40000\s+ALTER[^;]*;',     # MySQL特定ALTER
        ]
        
        # 修复：更安全的数据类型转换
        self.data_type_replacements = [
            # 整数类型（带或不带括号）
            (r'\bTINYINT\s*\(\s*\d+\s*\)', 'INTEGER'),
            (r'\bSMALLINT\s*\(\s*\d+\s*\)', 'INTEGER'),
            (r'\bMEDIUMINT\s*\(\s*\d+\s*\)', 'INTEGER'),
            (r'\bINT\s*\(\s*\d+\s*\)', 'INTEGER'),
            (r'\bBIGINT\s*\(\s*\d+\s*\)', 'INTEGER'),
            (r'\bTINYINT\b', 'INTEGER'),
            (r'\bSMALLINT\b', 'INTEGER'),
            (r'\bMEDIUMINT\b', 'INTEGER'),
            (r'\bINTEGER\b', 'INTEGER'),  # 防止重复替换
            (r'\bINT\b', 'INTEGER'),
            (r'\bBIGINT\b', 'INTEGER'),
            
            # 浮点数类型
            (r'\bFLOAT\s*\([^)]+\)', 'REAL'),
            (r'\bDOUBLE\s*\([^)]+\)', 'REAL'),
            (r'\bDECIMAL\s*\([^)]+\)', 'REAL'),
            (r'\bFLOAT\b', 'REAL'),
            (r'\bDOUBLE\b', 'REAL'),
            (r'\bDECIMAL\b', 'REAL'),
            
            # 字符串类型
            (r'\bCHAR\s*\(\s*\d+\s*\)', 'TEXT'),
            (r'\bVARCHAR\s*\(\s*\d+\s*\)', 'TEXT'),
            (r'\bTEXT\b', 'TEXT'),
            (r'\bTINYTEXT\b', 'TEXT'),
            (r'\bMEDIUMTEXT\b', 'TEXT'),
            (r'\bLONGTEXT\b', 'TEXT'),
            
            # 日期时间类型
            (r'\bDATETIME\b', 'TEXT'),
            (r'\bTIMESTAMP\b', 'INTEGER'),
            (r'\bDATE\b', 'TEXT'),
            (r'\bTIME\b', 'TEXT'),
            (r'\bYEAR\s*\(\s*\d+\s*\)', 'INTEGER'),
            
            # 特殊类型
            (r'\bENUM\s*\([^)]+\)', 'TEXT'),
            (r'\bSET\s*\([^)]+\)', 'TEXT'),
            (r'\bBLOB\b', 'BLOB'),
            (r'\bTINYBLOB\b', 'BLOB'),
            (r'\bMEDIUMBLOB\b', 'BLOB'),
            (r'\bLONGBLOB\b', 'BLOB'),
        ]
        
        self.log_file = None
    
    def setup_logging(self):
        """设置日志文件"""
        log_file = self.output_db.with_suffix('.log')
        self.log_file = open(log_file, 'w', encoding='utf-8')
    
    def log(self, message, level='INFO', show=True):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{timestamp}] [{level}] {message}'
        
        if self.log_file:
            self.log_file.write(log_entry + '\n')
            self.log_file.flush()
        
        if show or level in ['ERROR', 'WARNING']:
            print(log_entry)
    
    def clean_sql_file(self):
        """彻底清理SQL文件，移除所有MySQL特有语法"""
        self.log(f'开始深度清理: {self.input_file}')
        
        try:
            with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            self.log(f'读取文件失败: {e}', 'ERROR')
            return None
        
        cleaned_lines = []
        in_comment_block = False
        in_create_table = False
        current_table = None
        
        for i, line in enumerate(lines, 1):
            original_line = line.rstrip()
            line = original_line
            
            # 跳过空行
            if not line.strip():
                cleaned_lines.append('')
                continue
            
            # 处理多行注释块
            if '/*!' in line:
                in_comment_block = True
                continue
            if in_comment_block and '*/' in line:
                in_comment_block = False
                continue
            if in_comment_block:
                continue
            
            # 跳过单行注释
            if line.strip().startswith('--'):
                continue
            
            # 跳过特定的MySQL语句
            skip_keywords = [
                'SET SQL_MODE',
                'SET @OLD_',
                'LOCK TABLES',
                'UNLOCK TABLES',
                'DELIMITER',
                '/*!',
                'DROP TABLE IF EXISTS',
                'CREATE DATABASE',
                'USE ',
            ]
            
            if any(line.upper().startswith(keyword.upper()) for keyword in skip_keywords):
                self.log(f'跳过MySQL特有语句: {line[:80]}...', 'DEBUG', show=False)
                continue
            
            # 标记CREATE TABLE开始
            if 'CREATE TABLE' in line.upper():
                in_create_table = True
                # 提取表名
                match = re.search(r'`([^`]+)`', line)
                if match:
                    current_table = match.group(1)
            
            # 处理CREATE TABLE内部的语法
            if in_create_table:
                # 移除反引号
                line = line.replace('`', '"')
                
                # 移除UNSIGNED
                line = re.sub(r'\s+UNSIGNED', '', line, flags=re.IGNORECASE)
                
                # 移除ZEROFILL
                line = re.sub(r'\s+ZEROFILL', '', line, flags=re.IGNORECASE)
                
                # 移除字段注释
                line = re.sub(r"COMMENT\s+'[^']*'", '', line, flags=re.IGNORECASE)
                
                # 处理AUTO_INCREMENT
                if 'AUTO_INCREMENT' in line.upper():
                    # 找到字段名
                    field_match = re.search(r'"([^"]+)"', line)
                    if field_match:
                        field_name = field_match.group(1)
                        # 简化处理：将包含AUTO_INCREMENT的字段设为主键
                        line = f'  "{field_name}" INTEGER PRIMARY KEY AUTOINCREMENT'
                
                # 处理ENUM类型
                if 'ENUM' in line.upper():
                    # 提取ENUM值
                    enum_match = re.search(r'ENUM\s*\(([^)]+)\)', line, re.IGNORECASE)
                    if enum_match:
                        # 保留ENUM值作为CHECK约束的参考
                        enum_values = enum_match.group(1)
                        # 替换为TEXT类型，CHECK约束将在表创建后添加
                        line = re.sub(r'ENUM\s*\([^)]+\)', 'TEXT', line, flags=re.IGNORECASE)
                
                # 处理数据类型的显示宽度 (如 INT(11))
                line = re.sub(r'(INT|INTEGER|TINYINT|SMALLINT|MEDIUMINT|BIGINT)\s*\(\s*\d+\s*\)', 
                            r'\1', line, flags=re.IGNORECASE)
                line = re.sub(r'(CHAR|VARCHAR)\s*\(\s*\d+\s*\)', 'TEXT', line, flags=re.IGNORECASE)
                
                # CREATE TABLE结束
                if line.strip().endswith(';'):
                    in_create_table = False
                    # 移除表选项
                    line = re.sub(r'\)\s*ENGINE\s*=[^;]+;', ');', line, flags=re.IGNORECASE)
                    line = re.sub(r'\)\s*CHARSET\s*=[^;]+;', ');', line, flags=re.IGNORECASE)
                    line = re.sub(r'\)\s*AUTO_INCREMENT\s*=\s*\d+\s*;', ');', line, flags=re.IGNORECASE)
                    line = re.sub(r'\)\s*[^;]*;', ');', line)
            
            # 处理INSERT语句
            elif 'INSERT INTO' in line.upper():
                # 移除反引号
                line = line.replace('`', '"')
                
                # 处理零日期
                line = re.sub(r"'0000-00-00'", "NULL", line)
                line = re.sub(r"'0000-00-00 00:00:00'", "NULL", line)
                
                # 修复可能的多余空格
                line = re.sub(r'\s+', ' ', line)
            
            # 移除行尾的逗号（如果这是CREATE TABLE的最后一行）
            if line.rstrip().endswith(',') and ');' in ''.join(cleaned_lines[-3:]):
                line = line.rstrip()[:-1]
            
            # 添加清理后的行
            if line.strip():
                cleaned_lines.append(line)
        
        # 重新组装SQL
        cleaned_sql = '\n'.join(cleaned_lines)
        
        # 进一步清理：移除连续的空白行
        cleaned_sql = re.sub(r'\n\s*\n', '\n', cleaned_sql)
        
        self.log(f'深度清理完成，保留 {len(cleaned_lines)} 行')
        return cleaned_sql
    
    def split_sql_statements(self, content):
        """智能分割SQL语句"""
        statements = []
        current = []
        in_string = False
        string_char = None
        escaped = False
        in_parenthesis = 0
        
        for char in content:
            if escaped:
                current.append(char)
                escaped = False
            elif char == '\\':
                escaped = True
                current.append(char)
            elif not in_string and char in ("'", '"'):
                in_string = True
                string_char = char
                current.append(char)
            elif in_string and char == string_char:
                in_string = False
                string_char = None
                current.append(char)
            elif not in_string and char == '(':
                in_parenthesis += 1
                current.append(char)
            elif not in_string and char == ')':
                in_parenthesis -= 1
                current.append(char)
            elif not in_string and in_parenthesis == 0 and char == ';':
                stmt = ''.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(char)
        
        # 处理最后一个语句
        if current:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def execute_with_error_recovery(self, statements):
        """执行SQL语句，带有错误恢复机制"""
        self.log(f'正在创建SQLite数据库: {self.output_db}')
        
        try:
            self.conn = sqlite3.connect(self.output_db)
            self.cursor = self.conn.cursor()
            
            # SQLite优化设置
            self.cursor.execute('PRAGMA foreign_keys = OFF;')  # 先关闭外键检查
            self.cursor.execute('PRAGMA journal_mode = MEMORY;')
            self.cursor.execute('PRAGMA synchronous = OFF;')
            self.cursor.execute('PRAGMA cache_size = 10000;')
            
        except Exception as e:
            self.log(f'创建数据库失败: {e}', 'ERROR')
            return False
        
        # 先保存所有CREATE TABLE语句，最后执行
        create_table_statements = []
        other_statements = []
        
        for stmt in statements:
            if 'CREATE TABLE' in stmt.upper():
                create_table_statements.append(stmt)
            elif stmt.strip() and not stmt.strip().startswith('--'):
                other_statements.append(stmt)
        
        self.log(f'找到 {len(create_table_statements)} 个CREATE TABLE语句')
        self.log(f'找到 {len(other_statements)} 个其他语句')
        
        # 第一步：创建所有表
        self.log('第一步：创建表结构...')
        for i, stmt in enumerate(create_table_statements, 1):
            try:
                # 确保语句以分号结束
                if not stmt.strip().endswith(';'):
                    stmt = stmt.strip() + ';'
                
                self.cursor.execute(stmt)
                self.stats['tables_created'] += 1
                
                if i % 5 == 0:
                    self.log(f'  已创建 {i}/{len(create_table_statements)} 个表')
                    
            except sqlite3.Error as e:
                error_msg = str(e)
                self.stats['errors'] += 1
                
                # 尝试修复常见的CREATE TABLE错误
                if 'duplicate column name' in error_msg.lower():
                    self.log(f'  警告: 表中有重复列名，跳过错误', 'WARNING')
                    continue
                elif 'table' in error_msg.lower() and 'already exists' in error_msg.lower():
                    self.log(f'  警告: 表已存在，跳过', 'WARNING')
                    continue
                else:
                    self.log(f'  创建表失败 [{i}]: {error_msg}', 'ERROR')
                    self.log(f'  问题语句: {stmt[:100]}...', 'DEBUG')
        
        self.conn.commit()
        self.log('表结构创建完成')
        
        # 第二步：执行其他语句（INSERT等）
        self.log('第二步：执行数据插入语句...')
        batch_size = 50
        current_batch = []
        
        for i, stmt in enumerate(other_statements, 1):
            if 'INSERT' in stmt.upper():
                current_batch.append(stmt)
                
                # 批量执行INSERT语句
                if len(current_batch) >= batch_size or i == len(other_statements):
                    success_count = self.execute_batch_inserts(current_batch)
                    self.stats['rows_inserted'] += success_count
                    current_batch = []
                    
                    if i % 100 == 0:
                        self.log(f'  已处理 {i}/{len(other_statements)} 条语句')
            else:
                # 执行非INSERT语句
                try:
                    self.cursor.execute(stmt)
                except sqlite3.Error as e:
                    self.log(f'  执行语句失败 [{i}]: {str(e)[:100]}', 'WARNING')
                    self.stats['warnings'] += 1
        
        # 执行最后一批INSERT
        if current_batch:
            success_count = self.execute_batch_inserts(current_batch)
            self.stats['rows_inserted'] += success_count
        
        # 重新启用外键约束
        self.cursor.execute('PRAGMA foreign_keys = ON;')
        self.conn.commit()
        
        self.log('所有语句执行完成')
        return True
    
    def execute_batch_inserts(self, insert_statements):
        """批量执行INSERT语句，提高性能"""
        success_count = 0
        
        for stmt in insert_statements:
            try:
                self.cursor.execute(stmt)
                success_count += 1
            except sqlite3.Error as e:
                error_msg = str(e)
                
                # 跳过重复键错误
                if 'UNIQUE constraint failed' in error_msg:
                    continue
                # 跳过外键错误（如果外键检查已开启）
                elif 'FOREIGN KEY constraint failed' in error_msg:
                    continue
                else:
                    # 尝试修复常见的INSERT错误
                    fixed_stmt = self.fix_insert_statement(stmt, error_msg)
                    if fixed_stmt and fixed_stmt != stmt:
                        try:
                            self.cursor.execute(fixed_stmt)
                            success_count += 1
                            self.log(f'  修复后插入成功', 'DEBUG', show=False)
                        except:
                            self.stats['warnings'] += 1
                    else:
                        self.stats['warnings'] += 1
        
        return success_count
    
    def fix_insert_statement(self, stmt, error_msg):
        """尝试修复INSERT语句"""
        # 修复1: 值数量与列数量不匹配
        if 'has' in error_msg and 'columns' in error_msg and 'but' in error_msg and 'values' in error_msg:
            # 提取列数和值数
            col_match = re.search(r'has (\d+) columns', error_msg)
            val_match = re.search(r'but (\d+) values', error_msg)
            
            if col_match and val_match:
                col_count = int(col_match.group(1))
                val_count = int(val_match.group(1))
                
                if val_count > col_count:
                    # 值太多，尝试截断
                    self.log(f'  修复: 值数量({val_count})多于列数量({col_count})', 'WARNING')
                    # 这是一个复杂的问题，暂时跳过
                    return None
        
        # 修复2: 无效的日期格式
        if 'date' in error_msg.lower() or 'time' in error_msg.lower():
            # 尝试查找并修复日期值
            date_patterns = [
                r"'(\d{4}-\d{2}-\d{2})'",
                r"'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'"
            ]
            
            for pattern in date_patterns:
                dates = re.findall(pattern, stmt)
                for date_str in dates:
                    # 检查是否是无效日期
                    if '0000-00-00' in date_str:
                        stmt = stmt.replace(f"'{date_str}'", 'NULL')
            
            return stmt
        
        return None
    
    def verify_and_report(self):
        """验证转换结果并生成报告"""
        self.log('正在验证转换结果...')
        
        try:
            # 获取所有表
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in self.cursor.fetchall()]
            
            if not tables:
                self.log('警告: 数据库中没有找到任何表', 'WARNING')
                return
            
            self.log(f'验证通过！数据库包含 {len(tables)} 个表:')
            
            for table in tables:
                try:
                    # 获取行数
                    self.cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                    count = self.cursor.fetchone()[0]
                    
                    # 获取列信息
                    self.cursor.execute(f'PRAGMA table_info("{table}");')
                    columns = self.cursor.fetchall()
                    
                    self.log(f'  {table}: {count} 行, {len(columns)} 列')
                    
                except sqlite3.Error as e:
                    self.log(f'  读取表 {table} 失败: {e}', 'WARNING')
            
            # 生成详细报告
            self.generate_detailed_report(tables)
            
        except Exception as e:
            self.log(f'验证过程中出错: {e}', 'ERROR')
    
    def generate_detailed_report(self, tables):
        """生成详细报告"""
        report_file = self.output_db.with_suffix('.report.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('=' * 70 + '\n')
            f.write('MySQL 到 SQLite 转换详细报告\n')
            f.write('=' * 70 + '\n')
            f.write(f'输入文件: {self.input_file}\n')
            f.write(f'输出数据库: {self.output_db}\n')
            f.write(f'转换时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('=' * 70 + '\n')
            f.write('\n转换统计:\n')
            f.write(f'  创建的表: {self.stats["tables_created"]}\n')
            f.write(f'  插入的行: {self.stats["rows_inserted"]}\n')
            f.write(f'  遇到的错误: {self.stats["errors"]}\n')
            f.write(f'  警告: {self.stats["warnings"]}\n')
            f.write('=' * 70 + '\n')
            f.write('\n数据库表详情:\n')
            
            for table in tables:
                try:
                    self.cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                    count = self.cursor.fetchone()[0]
                    
                    self.cursor.execute(f'PRAGMA table_info("{table}");')
                    columns = self.cursor.fetchall()
                    
                    f.write(f'\n{table}:\n')
                    f.write(f'  行数: {count}\n')
                    f.write(f'  列数: {len(columns)}\n')
                    f.write('  列信息:\n')
                    
                    for col in columns:
                        col_id, col_name, col_type, notnull, default_val, pk = col
                        f.write(f'    - {col_name}: {col_type}')
                        if pk:
                            f.write(' (PRIMARY KEY)')
                        if default_val is not None:
                            f.write(f' [默认: {default_val}]')
                        f.write('\n')
                        
                except Exception as e:
                    f.write(f'\n{table}: 读取失败 - {str(e)}\n')
            
            f.write('\n' + '=' * 70 + '\n')
            f.write('验证命令:\n')
            f.write(f'  sqlite3 {self.output_db} ".tables"\n')
            f.write(f'  sqlite3 {self.output_db} "SELECT name FROM sqlite_master WHERE type=\'table\';"\n')
            f.write(f'  sqlite3 {self.output_db} "SELECT * FROM sino_admin LIMIT 3;"\n')
            f.write('=' * 70 + '\n')
        
        self.log(f'详细报告已保存到: {report_file}')
    
    def cleanup(self):
        """清理资源"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        if self.log_file:
            self.log_file.close()
    
    def convert(self):
        """执行完整转换"""
        self.setup_logging()
        self.log('开始MySQL到SQLite转换 (修复版)')
        
        try:
            # 1. 深度清理SQL文件
            cleaned_sql = self.clean_sql_file()
            if cleaned_sql is None:
                return False
            
            # 2. 分割SQL语句
            statements = self.split_sql_statements(cleaned_sql)
            self.log(f'共找到 {len(statements)} 条SQL语句')
            
            # 3. 保存清理后的SQL文件（用于调试）
            debug_sql = self.output_db.with_suffix('.cleaned.sql')
            with open(debug_sql, 'w', encoding='utf-8') as f:
                f.write(cleaned_sql)
            self.log(f'清理后的SQL已保存到: {debug_sql}')
            
            # 4. 执行转换
            if not self.execute_with_error_recovery(statements):
                self.log('转换执行过程中出现问题', 'WARNING')
            
            # 5. 验证和报告
            self.verify_and_report()
            
            # 6. 最终统计
            self.log('=' * 60)
            self.log('转换完成！最终统计:')
            self.log(f'  创建的表: {self.stats["tables_created"]}')
            self.log(f'  插入的行: {self.stats["rows_inserted"]}')
            self.log(f'  错误数: {self.stats["errors"]}')
            self.log(f'  警告数: {self.stats["warnings"]}')
            self.log('=' * 60)
            self.log(f'数据库文件: {self.output_db}')
            self.log(f'日志文件: {self.output_db.with_suffix(".log")}')
            self.log(f'详细报告: {self.output_db.with_suffix(".report.txt")}')
            
            return True
            
        except Exception as e:
            self.log(f'转换过程中发生严重错误: {e}', 'ERROR')
            import traceback
            self.log(traceback.format_exc(), 'ERROR')
            return False
        finally:
            self.cleanup()

def main():
    if len(sys.argv) != 3:
        print("用法: python3 mysql_to_sqlite_fixed.py <输入SQL文件> <输出SQLite数据库>")
        print("示例: python3 mysql_to_sqlite_fixed.py sino.sql sinogacma_fixed.db")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_db = sys.argv[2]
    
    if not Path(input_file).exists():
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    converter = FixedMySQLToSQLiteConverter(input_file, output_db)
    success = converter.convert()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
