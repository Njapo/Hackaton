#!/usr/bin/env python3
import re

# Read the file
with open('/home/v-nikolozij/hackaton/app/main.py', 'r') as f:
    content = f.read()

# Replace the problematic line
old_code = '    # 3. Get the response from the generative AI\n    ai_response_text = get_ai_response(prompt)'
new_code = '''    # 3. Get the response from the generative AI
    ai_response_dict = get_ai_response(prompt)
    
    # Extract the text from the response
    ai_response_text = ai_response_dict.get("response", "Unable to generate response")'''

content = content.replace(old_code, new_code)

# Write it back
with open('/home/v-nikolozij/hackaton/app/main.py', 'w') as f:
    f.write(content)

print("✅ FIXED!")
