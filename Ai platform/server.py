from mcp.server.fastmcp import FastMCP
import logging
from LLM import create_model, generate_content_sync
from tts import hamsa_tts
from ASR import hamsa_stt
import base64

# Initialize FastMCP with no tools registered
mcp = FastMCP("MCPServer", host="localhost", port=8000)

logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a new model instance for the llm tool
llm_model = create_model("gemini-2.5-flash")

@mcp.tool()
def hello(name: str):
    """ a function that says hello"""
    return f"Hello, {name}!"

@mcp.tool()
def llm_tool(prompt: str):
    """
    Invokes the underlying Gemini LLM to generate text based on a client-provided prompt.

    This tool provides a unified interface for natural-language generation inside the
    MCP server, supporting both synchronous and streaming output modes. It can be used
    for a wide range of LLM-driven behaviors, including answering questions, generating
    structured text, creative writing, code assistance, and multi-step reasoning.

    Args:
        prompt (str): The textual instruction or query sent to the model.

    Returns:
        str or AsyncIterator[str]:
            - A full, non-streamed response when called synchronously.
            - A token/word-level async iterator when streaming is enabled.
    """

    try:
        logging.info(f"LLM tool called with prompt: {prompt}")
        response = generate_content_sync(prompt, model_instance=llm_model)
        logging.info(f"LLM tool response generated successfully")
        return response
    except Exception as e:
        error_msg = f"Error generating LLM response: {str(e)}"
        logging.error(error_msg)
        return error_msg

@mcp.tool()
def tts_tool(text: str, speaker="Noura", dialect="pls"):
    """
    Convert text into spoken audio using the Hamsa real-time TTS engine.

    This tool provides a simple MCP interface for generating natural-sounding
    Arabic speech. Clients can specify the text to be synthesized along with
    the desired speaker voice and dialect. The resulting audio is returned as
    a base64-encoded byte stream, allowing MCP clients or UIs to play, store,
    or process the audio without additional decoding steps.

    Args:
        text (str): The text content to synthesize into speech.
        speaker (str): The TTS voice model to use (e.g., "Noura", "Adam").
        dialect (str): The target dialect code supported by Hamsa
                       (e.g., "pls" for Gulf/Modern Standard variants).

    Returns:
        dict: A structured response containing:
            - "audio_base64" (str): Base64-encoded audio bytes produced by the TTS service.
            - "speaker" (str): The speaker voice used.
            - "dialect" (str): The dialect used for synthesis.

    Raises:
        Exception: If the TTS API request fails or returns a non-200 response.
    """
    audio_bytes = hamsa_tts(text, speaker, dialect)
    return {
        "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
    }

@mcp.tool()
def stt_tool(audio_path: str, language: str = "ar") -> dict:
    """
    MCP Tool: Convert speech audio to text using the Hamsa STT service.

    This tool accepts a path to a WAV file, normalizes the audio into
    16-kHz mono PCM format, encodes it as Base64, and submits it to the
    Hamsa real-time speech recognition API. The transcription returned
    by the API is structured and ready for use inside an MCP client or
    downstream processing pipeline.

    Args:
        audio_path (str): Path to the input audio (WAV). The tool ensures
                          proper conversion to a supported PCM format.
        language (str): Language code for recognition (default: 'ar').

    Returns:
        dict: {
            "transcript": str,   # Recognized text
            "language": str,     # Language used
            "raw_response": dict # Full API response for debugging or metadata
        }

    Raises:
        Exception: If audio processing or API interaction fails.
    """
    result = hamsa_stt(audio_path, language)

    return {
        "transcript": result.get("transcript") or result.get("text") or "",
        "language": language,
        "raw_response": result
    }

if __name__ == "__main__":
    # Run MCP server using streamable HTTP transport
    mcp.run(transport="streamable-http")
