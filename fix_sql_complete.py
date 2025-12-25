#!/usr/bin/env python3
import re

def fix_sql_content(content):
    # Fix the problematic characters step by step
    
    # 1. Replace \r\n sequences with actual newlines
    content = content.replace('\\r\\n', '\n')
    
    # 2. Replace \n sequences with actual newlines
    content = content.replace('\\n', '\n')
    
    # 3. Fix single quotes that are part of escape sequences
    content = content.replace("\\'", "''")
    
    # 4. Fix the numeric values that are incorrectly quoted in DEFAULT clauses
    # Pattern: DEFAULT 'number' -> DEFAULT number
    content = re.sub(r"DEFAULT '(\d+)'", r"DEFAULT \1", content)
    
    # 5. Also handle other quoted defaults that should be numbers
    content = re.sub(r"DEFAULT '(\d+\.?\d*)'", r"DEFAULT \1", content)
    
    # 6. Fix problematic INSERT statements by properly escaping quotes in content
    # First, let's identify INSERT statements and handle them carefully
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if this is a line that contains values for INSERT statement
        if "VALUES" in line.upper() and ("'" in line or '"' in line):
            # Handle single quotes in content properly for SQLite
            # Replace single quotes with two single quotes for SQL escaping
            line = line.replace("''", "''")  # Preserve existing doubled quotes
            # Then escape single quotes that are not already escaped
            # This is a complex regex to match single quotes that are not part of ''
            # For now, a simpler approach: replace single quotes with doubled quotes in values
            pass
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    return content

# Alternative approach: Use a more comprehensive replacement
def fix_sql_comprehensive():
    with open('/workspace/sqlite.sql', 'r', encoding='utf-8') as f:
        content = f.read()

    # First fix escape sequences
    content = content.replace('\\r\\n', '\n')
    content = content.replace('\\n', '\n')
    content = content.replace('\\t', '\t')
    
    # Fix the DEFAULT clauses with numbers in quotes
    content = re.sub(r"DEFAULT '(\d+)'", r"DEFAULT \1", content)
    content = re.sub(r"DEFAULT '(\d+\.?\d*)'", r"DEFAULT \1", content)
    
    # The main issue: properly escape single quotes in INSERT statements
    # We need to find INSERT statements and fix quotes within them
    # Use a regex to match INSERT statements and their values
    def fix_insert_values(match):
        statement = match.group(0)
        # Replace single quotes with doubled single quotes (SQLite escape method)
        # But be careful not to double already doubled quotes
        # Replace ' with '' but preserve ''
        fixed = re.sub(r"(?<!')'(?!\s*[),])", "''", statement)
        return fixed
    
    # Process the entire content to fix INSERT statements
    # This is a more targeted approach to handle the quotes in values
    lines = content.split('\n')
    result_lines = []
    
    in_insert_statement = False
    current_insert = ""
    
    for line in lines:
        upper_line = line.upper().strip()
        
        if upper_line.startswith('INSERT INTO'):
            in_insert_statement = True
            current_insert = line
        elif in_insert_statement:
            current_insert += '\n' + line
            # Check if this line ends the INSERT statement
            if line.strip().endswith(';') or line.strip().endswith(';;'):
                # Process this INSERT statement to fix quotes
                # Replace single quotes with double single quotes in string values
                processed_insert = process_insert_statement(current_insert)
                result_lines.append(processed_insert)
                in_insert_statement = False
                current_insert = ""
        else:
            result_lines.append(line)
    
    if in_insert_statement and current_insert:
        # Handle unfinished INSERT statement
        processed_insert = process_insert_statement(current_insert)
        result_lines.append(processed_insert)
    
    content = '\n'.join(result_lines)
    
    return content

def process_insert_statement(insert_stmt):
    # Find the VALUES part and properly escape quotes within string values
    # This is a simplified approach - replace single quotes with double quotes in string values
    parts = insert_stmt.split('VALUES', 1)
    if len(parts) != 2:
        return insert_stmt
    
    query_part = parts[0]
    values_part = parts[1]
    
    # The complex part: process the values to escape quotes properly
    # We need to identify string values (wrapped in quotes) and escape internal quotes
    processed_values = escape_sql_string_values(values_part)
    
    return query_part + 'VALUES' + processed_values

def escape_sql_string_values(values_text):
    # This function will process the values part of an INSERT statement
    # and properly escape single quotes in string values
    result = ""
    i = 0
    while i < len(values_text):
        char = values_text[i]
        
        if char == "'":
            # Start of a string value
            result += char
            i += 1
            # Process until we find the closing quote (that's not escaped)
            while i < len(values_text):
                char = values_text[i]
                if char == "'" and (i == 0 or values_text[i-1] != '\\'):
                    # Found end of string, but in SQLite we need to double the single quotes
                    # So we need to go back and double any single quotes inside the string
                    result += char
                    break
                elif char == "'":
                    # This is a single quote inside the string, need to double it for SQLite
                    result += "''"  # Double the single quote for SQLite
                else:
                    result += char
                i += 1
        else:
            result += char
        i += 1
    
    return result

# Actually process the file
with open('/workspace/sqlite.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# A simpler approach: Use sed-like replacements but more carefully
# First, replace escape sequences
content = content.replace('\\r\\n', '\\n')
content = content.replace('\\n', '\n')

# Fix DEFAULT clauses
content = re.sub(r"DEFAULT '(\d+)'", r"DEFAULT \1", content)
content = re.sub(r"DEFAULT '(\d+\.?\d*)'", r"DEFAULT \1", content)

# For SQLite, we need to handle quotes differently
# The main issue is that some values have single quotes inside them
# In SQLite, single quotes inside string literals need to be doubled ('' not ')

# A comprehensive replacement approach
import re

# Find INSERT statements and fix them
lines = content.split('\n')
result_lines = []
in_insert = False
insert_buffer = []

for line in lines:
    line_upper = line.upper().strip()
    
    if line_upper.startswith('INSERT INTO'):
        in_insert = True
        insert_buffer = [line]
    elif in_insert:
        insert_buffer.append(line)
        # Check if this line ends the INSERT statement
        if line.strip().endswith(';') or line.strip().endswith(';;') or ');' in line or ');;' in line:
            # Process the entire INSERT statement
            insert_text = '\n'.join(insert_buffer)
            
            # Replace single quotes with double single quotes in string values
            # But be careful with the VALUES part
            if 'VALUES' in insert_text:
                parts = insert_text.split('VALUES', 1)
                if len(parts) == 2:
                    query_part, values_part = parts[0], parts[1]
                    # Now process the values part to escape single quotes properly
                    processed_values = re.sub(r"(?<!')'(?=.*')", "''", values_part)
                    insert_text = query_part + 'VALUES' + processed_values
            
            result_lines.append(insert_text)
            in_insert = False
            insert_buffer = []
    else:
        result_lines.append(line)

content = '\n'.join(result_lines)

# Write the fixed content to a new file
with open('/workspace/sqlite_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed SQL file has been created: sqlite_fixed.sql")