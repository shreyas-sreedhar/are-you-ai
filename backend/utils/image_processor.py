"""Image processing utilities for frame preprocessing."""
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def decode_base64_image(base64_string: str) -> Image.Image:
    """
    Decode base64 encoded image string to PIL Image.
    
    Args:
        base64_string: Base64 encoded image string (with or without data URL prefix)
        
    Returns:
        PIL Image object
        
    Raises:
        ValueError: If image cannot be decoded
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if "," in base64_string:
            base64_string = base64_string.split(",", 1)[1]
        
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_string)
        
        # Create PIL Image from bytes
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if needed (removes alpha channel, etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        return image
        
    except Exception as e:
        logger.error(f"Error decoding base64 image: {e}")
        raise ValueError(f"Failed to decode base64 image: {str(e)}")


def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Resize image maintaining aspect ratio, ensuring max dimension doesn't exceed max_size.
    
    Args:
        image: PIL Image object
        max_size: Maximum dimension (width or height) in pixels
        
    Returns:
        Resized PIL Image
    """
    width, height = image.size
    
    # If image is already smaller than max_size, return as is
    if width <= max_size and height <= max_size:
        return image
    
    # Calculate new dimensions maintaining aspect ratio
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    
    # Resize using LANCZOS resampling for quality
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
    return resized


def preprocess_frame(base64_string: str, max_size: int = 1024) -> Image.Image:
    """
    Complete preprocessing pipeline: decode base64, convert to RGB, resize.
    
    Args:
        base64_string: Base64 encoded image string
        max_size: Maximum dimension for resizing
        
    Returns:
        Preprocessed PIL Image ready for analysis
    """
    image = decode_base64_image(base64_string)
    image = resize_image(image, max_size)
    return image


def image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image: PIL Image object
        format: Image format (JPEG, PNG, etc.)
        
    Returns:
        Base64 encoded string (without data URL prefix)
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")

