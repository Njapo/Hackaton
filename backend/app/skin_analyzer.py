from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch

# Load the model and processor from Hugging Face
processor = AutoImageProcessor.from_pretrained('Jayanth2002/dinov2-base-finetuned-SkinDisease')
model = AutoModelForImageClassification.from_pretrained('Jayanth2002/dinov2-base-finetuned-SkinDisease', ignore_mismatched_sizes=True)

def analyze_skin_image(image_file):
    """
    Analyzes an uploaded image file to predict the skin disease.
    
    Args:
        image_file: The image file uploaded by the user.
        
    Returns:
        A string with the predicted disease name.
    """
    try:
        # Open the image
        image = Image.open(image_file.file).convert("RGB")
        
        # Process the image and get model inputs
        inputs = processor(images=image, return_tensors="pt")
        
        # Get the model's prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
        
        # Find the class with the highest probability
        predicted_class_idx = logits.argmax(-1).item()
        
        # Get the name of the predicted class
        predicted_disease = model.config.id2label[predicted_class_idx]
        
        return predicted_disease
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return "Could not analyze image"
