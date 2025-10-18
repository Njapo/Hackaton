#!/usr/bin/env python3

# Read the Windows file
with open('/mnt/c/Users/v-nikolozij/Desktop/Hackaton/backend/app/main.py', 'r') as f:
    content = f.read()

# Write to WSL
with open('/home/v-nikolozij/hackaton/app/main.py', 'w') as f:
    f.write(content)

print("✅ MAIN.PY COPIED AND UPDATED!")
