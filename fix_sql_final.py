#!/usr/bin/env python3
import re

# Read the original file
with open('/workspace/sqlite.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# First, fix the DEFAULT issues
content = re.sub(r"DEFAULT '(\d+)'", r"DEFAULT \1", content)
content = re.sub(r"DEFAULT '(\d+\.?\d*)'", r"DEFAULT \1", content)
content = re.sub(r"DEFAULT ,", r"DEFAULT '',", content)
content = re.sub(r"DEFAULT  ,", r"DEFAULT '',", content)
content = re.sub(r"DEFAULT $", r"DEFAULT ''", content)
content = re.sub(r"DEFAULT  $", r"DEFAULT ''", content)

# Fix escape sequences
content = content.replace('\\r\\n', '\\n')
content = content.replace('\\n', '\n')

# The key issue: Process INSERT statements to properly escape single quotes in string values
# We need to find the values part of INSERT statements and escape single quotes

def process_sql_inserts(sql_content):
    # Split the content into lines to process
    lines = sql_content.split('\n')
    result_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.strip().upper().startswith('INSERT INTO'):
            # This is an INSERT statement, collect all lines until we find the end
            insert_statement = line
            i += 1
            
            # Keep adding lines until we find the end of the INSERT statement
            while i < len(lines):
                next_line = lines[i]
                insert_statement += '\n' + next_line
                # Check if this line ends the INSERT statement
                if next_line.strip().endswith(';') or next_line.strip().endswith(';;'):
                    break
                i += 1
            
            # Process this INSERT statement to escape single quotes in string values
            processed_insert = process_single_insert(insert_statement)
            result_lines.append(processed_insert)
        else:
            result_lines.append(line)
        
        i += 1
    
    return '\n'.join(result_lines)

def process_single_insert(insert_sql):
    # Split the INSERT statement into query part and VALUES part
    if 'VALUES' not in insert_sql.upper():
        return insert_sql  # Not a VALUES statement, return as is
    
    # Find the position of VALUES to split the statement
    values_pos = insert_sql.upper().find('VALUES')
    query_part = insert_sql[:values_pos + 6]  # Include "VALUES"
    values_part = insert_sql[values_pos + 6:]
    
    # Now process the values part to escape single quotes
    # This is tricky because we need to identify string literals (text between single quotes)
    # and escape any single quotes within them by doubling them
    
    processed_values = escape_quotes_in_values(values_part)
    
    return query_part + processed_values

def escape_quotes_in_values(values_text):
    result = ""
    i = 0
    in_string = False
    quote_char = "'"
    
    while i < len(values_text):
        char = values_text[i]
        
        if not in_string and char == "'":
            # Starting a string literal
            in_string = True
            result += char
        elif in_string and char == "'":
            # Check if this is an escaped quote ('') or end of string
            if i + 1 < len(values_text) and values_text[i + 1] == "'":
                # This is an escaped quote '', add both and continue
                result += "''"  # In the original text this is '', in SQLite this becomes ''''
                i += 1  # Skip the next quote since we handled it
            else:
                # This is the end of the string
                in_string = False
                result += char
        else:
            result += char
        
        i += 1
    
    return result

# Process the SQL content
content = process_sql_inserts(content)

# Write the fixed content to a new file
with open('/workspace/sqlite_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed SQL file has been created: sqlite_fixed.sql")