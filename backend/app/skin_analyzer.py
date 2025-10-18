from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F

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


def analyze_skin_image_with_confidence(image_file, top_k=5):
    """
    Analyzes an uploaded image file and returns top predictions with confidence scores.
    
    Args:
        image_file: The image file uploaded by the user.
        top_k: Number of top predictions to return (default: 5)
        
    Returns:
        A list of dictionaries with disease names and confidence scores.
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
        
        # Apply softmax to get probabilities
        probabilities = F.softmax(logits, dim=-1)[0]
        
        # Get top k predictions
        top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(probabilities)))
        
        # Format results
        predictions = []
        for prob, idx in zip(top_probs, top_indices):
            predictions.append({
                "disease": model.config.id2label[idx.item()],
                "confidence": round(prob.item(), 3)
            })
        
        return predictions
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return [{"disease": "Could not analyze image", "confidence": 0.0}]
