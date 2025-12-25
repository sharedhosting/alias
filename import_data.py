import re
import sqlite3

# Read the MySQL dump file
with open('/workspace/sino.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all INSERT statements
insert_statements = re.findall(r'INSERT INTO `(\w+)` \([^)]+\) VALUES([\s\S]*?)(?=;[\s\n\r]*INSERT INTO|\Z)', content)

# Connect to SQLite database
conn = sqlite3.connect('/workspace/sino_new.db')
cursor = conn.cursor()

# Execute each INSERT statement
for table, values in insert_statements:
    # Remove leading/trailing whitespace and semicolon
    values = values.strip()
    if values.startswith('ON DUPLICATE KEY UPDATE'):
        continue
    
    # Split multiple rows
    rows = []
    current_row = ''
    paren_count = 0
    in_quotes = False
    quote_char = None
    
    for char in values:
        if char in ['\"', "'"] and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            # Check if this quote is escaped
            if len(current_row) > 0 and current_row[-1] == '\\':
                current_row += char
            else:
                in_quotes = False
                quote_char = None
            continue
        
        if not in_quotes:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    # End of a row
                    current_row += char
                    rows.append(current_row.strip())
                    current_row = ''
                    continue
        
        current_row += char
    
    # Execute each row
    for row in rows:
        if row.strip():
            # Replace MySQL-specific escape sequences
            row = row.replace('\\\\r', '\\r').replace('\\\\n', '\\n')
            # Create the INSERT statement for SQLite
            sql = f'INSERT INTO {table} VALUES {row}'
            try:
                cursor.execute(sql)
            except sqlite3.Error as e:
                print(f'Error inserting into {table}: {e}')
                print(f'Problematic SQL: {sql[:200]}...')

# Commit changes and close connection
conn.commit()
conn.close()