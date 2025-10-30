import re

with open('summarization.py', 'r') as f:
    content = f.read()

# Extract the /text endpoint (from line ~473)
text_endpoint_pattern = r'(@router\.post\("/text"\).*?(?=@router\.post|$))'
text_match = re.search(text_endpoint_pattern, content, re.DOTALL)

if text_match:
    text_endpoint = text_match.group(1).rstrip()
    
    # Remove it from its current position
    content = content.replace(text_endpoint, '')
    
    # Find the position right before /{document_id}
    doc_id_pattern = r'(@router\.post\("/{document_id}")'
    
    # Insert the /text endpoint before /{document_id}
    content = re.sub(
        doc_id_pattern,
        text_endpoint + '\n\n\n' + r'\1',
        content
    )
    
    with open('summarization.py', 'w') as f:
        f.write(content)
    
    print("✅ Routes reordered successfully!")
    print("   /text is now before /{document_id}")
else:
    print("❌ Could not find /text endpoint")
