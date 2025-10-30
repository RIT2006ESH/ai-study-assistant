import re

with open('summarization.py', 'r') as f:
    content = f.read()

# Extract the /solve endpoint
solve_pattern = r'(@router\.post\("/solve"\).*?(?=\n@router\.post|$))'
solve_match = re.search(solve_pattern, content, re.DOTALL)

if solve_match:
    solve_endpoint = solve_match.group(1).rstrip()
    
    # Remove it
    content = content.replace(solve_endpoint, '')
    
    # Insert before /{document_id}
    content = re.sub(
        r'(@router\.post\("/{document_id}")',
        solve_endpoint + '\n\n\n' + r'\1',
        content
    )
    
    with open('summarization.py', 'w') as f:
        f.write(content)
    
    print("✅ /solve moved before /{document_id}")
else:
    print("❌ Could not find /solve endpoint")
