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

# 3. Fix single quotes that are part of escape sequences
content = content.replace("\\'", "''")

# 4. Fix the numeric values that are incorrectly quoted in DEFAULT clauses
# Pattern: DEFAULT 'number' -> DEFAULT number
content = re.sub(r"DEFAULT '(\d+)'", r"DEFAULT \1", content)

# 5. Also handle other quoted defaults that should be numbers
content = re.sub(r"DEFAULT '(\d+\.?\d*)'", r"DEFAULT \1", content)

# 6. Fix other potential issues with quotes in the SQL
# But be careful not to break actual string values

# Write the fixed content to a new file
with open('/workspace/sqlite_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed SQL file has been created: sqlite_fixed.sql")