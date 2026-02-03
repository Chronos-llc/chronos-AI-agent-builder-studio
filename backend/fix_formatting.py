
with open('app/api/agents.py', 'r') as f:
    content = f.read()

# Replace escaped newlines and tabs with actual ones
content = content.replace(r'\n', '\n').replace(r'\t', '\t')

with open('app/api/agents.py', 'w') as f:
    f.write(content)

print('File formatting fixed successfully')
