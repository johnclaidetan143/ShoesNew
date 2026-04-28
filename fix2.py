with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the mangled line from PowerShell
bad = (
    'if database_url.startswith("postgres://"):`n    database_url = database_url.replace("postgres://", '
    '"postgresql://", 1)`nif database_url.startswith("postgresql://") and "+" not in database_url.split("://")[0]:`n    \n'
    'database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)'
)
good = (
    'if database_url.startswith("postgres://"):\n'
    '    database_url = database_url.replace("postgres://", "postgresql://", 1)\n'
    'if database_url.startswith("postgresql://") and "+pg8000" not in database_url:\n'
    '    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)'
)
content = content.replace(bad, good)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
