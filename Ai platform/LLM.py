import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("Google_api_key"))
model = genai.GenerativeModel("gemini-2.5-flash")


def create_model(model_name: str = "gemini-2.5-flash"):
    """
    Create a new Gemini model instance.
    
    Args:
        model_name: Name of the model to create (default: "gemini-2.5-flash")
    
    Returns:
        A new GenerativeModel instance
    """
    return genai.GenerativeModel(model_name)


def generate_content(prompt: str, stream: bool = False, model_instance=None):
    """
    Generate content using the Gemini model.
    
    Args:
        prompt: The prompt to send to the model
        stream: Whether to stream the response (default: False)
        model_instance: Optional model instance to use. If None, uses the default model.
    
    Returns:
        If stream=False: The complete response text
        If stream=True: Generator of response chunks
    """
    model_to_use = model_instance if model_instance is not None else model
    response = model_to_use.generate_content(prompt, stream=stream)
    
    if stream:
        return response
    else:
        return response.text


def generate_content_sync(prompt: str, model_instance=None) -> str:
    """
    Generate content synchronously and return the complete text.
    
    Args:
        prompt: The prompt to send to the model
        model_instance: Optional model instance to use. If None, uses the default model.
    
    Returns:
        The complete response text
    """
    return generate_content(prompt, stream=False, model_instance=model_instance)
