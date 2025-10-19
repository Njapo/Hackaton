#!/usr/bin/env python3

# Read the file
with open('/home/v-nikolozij/hackaton/app/ai_client.py', 'r') as f:
    content = f.read()

# Replace the dog fallback message
old_fallback = '''                fallback_message = (
                    "I understand you're concerned about your dog's coughing. While I cannot provide specific "
                    "medical advice due to safety restrictions, here are general recommendations:\\n\\n"
                    "1. **Monitor the cough**: Note if it's dry, wet, or accompanied by other symptoms\\n"
                    "2. **Check for triggers**: Exercise, eating/drinking, or environmental factors\\n"
                    "3. **Ensure hydration**: Make sure fresh water is always available\\n"
                    "4. **Watch for warning signs**: Difficulty breathing, lethargy, loss of appetite\\n"
                    "5. **Veterinary consultation**: If coughing persists >24-48 hours or worsens, contact your vet\\n\\n"
                    "Common causes include kennel cough, allergies, or heart issues. A vet examination is recommended."
                )'''

new_fallback = '''                fallback_message = (
                    "⚠️ **IMPORTANT MEDICAL DISCLAIMER**: I am an AI assistant, not a medical professional. "
                    "This is NOT a medical diagnosis. Please consult a licensed dermatologist or doctor for proper diagnosis and treatment.\\n\\n"
                    "Based on the image analysis and your symptoms, here are general recommendations:\\n\\n"
                    "1. **Consult a dermatologist**: Schedule an appointment as soon as possible\\n"
                    "2. **Keep the area clean**: Gently wash with mild soap and water\\n"
                    "3. **Avoid scratching**: This can worsen the condition or cause infection\\n"
                    "4. **Document symptoms**: Take photos and note when symptoms started\\n"
                    "5. **Avoid self-medication**: Wait for professional medical advice\\n\\n"
                    "Skin conditions can have various causes and require proper medical evaluation."
                )'''

content = content.replace(old_fallback, new_fallback)

# Write it back
with open('/home/v-nikolozij/hackaton/app/ai_client.py', 'w') as f:
    f.write(content)

print("✅ AI CLIENT FIXED!")
