#!/usr/bin/env python3
"""Quick script to verify endpoints are in the WSL main.py file"""

import sys

# Read the main.py file
with open('/home/v-nikolozij/hackaton/app/main.py', 'r') as f:
    content = f.read()

# Check for new endpoint patterns  
checks = {
    "Lesion Sections Tag": 'tags=["Lesion Sections"]',
    "Progress Tracking Tag": 'tags=["Progress Tracking"]',
    "Create Section Endpoint": '@app.post("/api/sections/create"',
    "Get Sections Endpoint": '@app.get("/api/sections"',
    "Progress Review Endpoint": '@app.post("/api/history/progress-review"',
    "Enhanced Analyze Endpoint": '@app.post("/api/ai/analyze"',
    "Section History Endpoint": '@app.get("/api/sections/{section_id}/history"'
}

print("="*60)
print("WSL FILE ENDPOINT VERIFICATION")
print("="*60)

all_found = True
for name, pattern in checks.items():
    found = pattern in content
    status = "✅ FOUND" if found else "❌ MISSING"
    print(f"{status} - {name}")
    if not found:
        all_found = False

print("="*60)
print(f"Total file lines: {len(content.splitlines())}")
print("="*60)
if all_found:
    print("✅ ALL ENDPOINTS ARE IN WSL FILE!")
else:
    print("❌ SOME ENDPOINTS ARE MISSING FROM WSL FILE!")
    
sys.exit(0 if all_found else 1)
