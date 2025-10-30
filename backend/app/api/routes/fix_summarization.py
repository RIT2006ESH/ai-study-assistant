with open('summarization.py', 'r') as f:
    lines = f.readlines()

# Fix the broken f-strings
new_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    # Fix the brief prompt
    if 'prompt = f"Provide a brief 2-3 sentence summary of the following text:' in line and not line.strip().endswith('}"'):
        new_lines.append('            prompt = f"Provide a brief 2-3 sentence summary of the following text:\\n\\n{text}"\n')
        skip_next = True
    # Fix the detailed prompt
    elif 'prompt = f"Provide a detailed summary with key points and important details from the following text:' in line and not line.strip().endswith('}"'):
        new_lines.append('            prompt = f"Provide a detailed summary with key points and important details from the following text:\\n\\n{text}"\n')
        skip_next = True
    # Fix the moderate prompt
    elif 'prompt = f"Provide a clear and concise summary of the following text:' in line and not line.strip().endswith('}"'):
        new_lines.append('            prompt = f"Provide a clear and concise summary of the following text:\\n\\n{text}"\n')
        skip_next = True
    else:
        new_lines.append(line)

with open('summarization.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed the broken f-strings!")
