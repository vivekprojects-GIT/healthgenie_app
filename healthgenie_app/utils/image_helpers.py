"""
Utility functions for image processing and validation
"""
import io
import base64
from PIL import Image
import streamlit as st
from typing import Optional, Tuple

def validate_image_file(uploaded_file) -> bool:
    """
    Validate if the uploaded file is a supported image format
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        bool: True if valid image, False otherwise
    """
    if uploaded_file is None:
        return False
    
    try:
        # Check file extension
        file_extension = uploaded_file.name.lower().split('.')[-1]
        supported_extensions = ['jpg', 'jpeg', 'png', 'bmp']
        
        if file_extension not in supported_extensions:
            return False
        
        # Try to open the image to verify it's valid
        image = Image.open(uploaded_file)
        image.verify()
        return True
        
    except Exception:
        return False

def process_image_for_gemini(uploaded_file) -> Optional[bytes]:
    """
    Process uploaded image file for Gemini API
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        bytes: Processed image bytes, None if error
    """
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read the image
        image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large (max 4MB for Gemini)
        max_size = (1024, 1024)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def encode_image_base64(image_bytes: bytes) -> str:
    """
    Encode image bytes to base64 string
    
    Args:
        image_bytes: Image data as bytes
        
    Returns:
        str: Base64 encoded image
    """
    return base64.b64encode(image_bytes).decode('utf-8')

def display_image_preview(uploaded_file, max_width: int = 300) -> None:
    """
    Display image preview in Streamlit
    
    Args:
        uploaded_file: Streamlit uploaded file object
        max_width: Maximum width for display
    """
    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=max_width)
    except Exception as e:
        st.error(f"Error displaying image: {str(e)}")

def get_image_info(uploaded_file) -> dict:
    """
    Get basic information about uploaded image
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        dict: Image information
    """
    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        
        return {
            "filename": uploaded_file.name,
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "file_size_mb": round(uploaded_file.size / (1024 * 1024), 2)
        }
    except Exception:
        return {"error": "Could not read image information"} 