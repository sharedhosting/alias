#!/usr/bin/env python3
import re

# Read the original sqlite.sql file
with open('/workspace/sqlite.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the problematic characters step by step
# 1. Replace \r\n sequences with actual newlines
content = content.replace('\\r\\n', '\n')

# 2. Replace \n sequences with actual newlines
content = content.replace('\\n', '\n')

# 3. Fix single quotes in a way that's safe for SQL
content = content.replace("\\'", "''")

# 4. Handle other potential escape sequences
content = content.replace('\\\\', '\\')

# 5. Fix potential SQL syntax issues with quotes
# Replace problematic quote sequences
content = re.sub(r"(?<!')'(?!')", "''", content)  # Replace single quotes that are not part of '' with ''

# Write the fixed content to a new file
with open('/workspace/sqlite_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed SQL file has been created: sqlite_fixed.sql")