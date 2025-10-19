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


def get_image_embedding(image_file, normalize=True):
    """
    Extract the 768-dimensional embedding vector from DinoV2 model.
    
    This embedding can be used for:
    - Similarity comparison between images
    - Tracking healing progress over time
    - Finding similar historical cases
    
    Args:
        image_file: The image file uploaded by the user
        normalize: Whether to normalize the embedding vector (default: True)
        
    Returns:
        List of 768 float values representing the image embedding,
        or None if extraction fails
    """
    try:
        # Open the image
        image = Image.open(image_file.file).convert("RGB")
        
        # Process the image and get model inputs
        inputs = processor(images=image, return_tensors="pt")
        
        # Get the model's prediction with hidden states
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)
            
            # Extract the embedding from the last hidden state
            # For ViT-based models like DinoV2, we can use the CLS token (first token)
            # or average all tokens. Using CLS token:
            hidden_states = outputs.hidden_states[-1]  # Last layer
            cls_embedding = hidden_states[:, 0, :].squeeze()  # CLS token
            
            # Alternatively, you could use average pooling:
            # embedding = hidden_states.mean(dim=1).squeeze()
        
        # Convert to list
        embedding = cls_embedding.tolist()
        
        # Normalize if requested (recommended for cosine similarity)
        if normalize:
            norm = torch.norm(cls_embedding).item()
            if norm > 0:
                embedding = [x / norm for x in embedding]
        
        return embedding
        
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None


def analyze_and_extract(image_file):
    """
    Convenience function that both analyzes the image and extracts embedding.
    
    Args:
        image_file: The image file uploaded by the user
        
    Returns:
        Tuple of (predictions list, embedding list) or (None, None) on error
    """
    try:
        # Need to reset file pointer since we'll read it twice
        image_file.file.seek(0)
        predictions = analyze_skin_image_with_confidence(image_file, top_k=5)
        
        image_file.file.seek(0)
        embedding = get_image_embedding(image_file, normalize=True)
        
        return predictions, embedding
    
    except Exception as e:
        print(f"Error in analyze_and_extract: {e}")
        return None, None
