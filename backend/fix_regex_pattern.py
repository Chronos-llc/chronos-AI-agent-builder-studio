import os
import re

# Directory containing the schema files
schemas_dir = 'app/schemas'

# Pattern to match 'regex' in field definitions
pattern = re.compile(r'regex=')

# Iterate through all Python files in the schemas directory
for filename in os.listdir(schemas_dir):
    if filename.endswith('.py'):
        file_path = os.path.join(schemas_dir, filename)
        
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace 'regex=' with 'pattern='
        modified_content = pattern.sub('pattern=', content)
        
        # Write the modified content back to the file
        with open(file_path, 'w') as f:
            f.write(modified_content)
        
        # Print the number of changes
        changes = len(re.findall(r'pattern=', modified_content)) - len(re.findall(r'pattern=', content))
        if changes > 0:
            print(f'Fixed {changes} occurrences in {filename}')

print('All changes completed')
