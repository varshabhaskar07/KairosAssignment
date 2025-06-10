import requests
import PyPDF2
import io
import os
from dotenv import load_dotenv
import google.generativeai as genai
import anthropic # Add this import

# Load environment variables from .env file
load_dotenv()

def download_pdf(pdf_url: str) -> io.BytesIO or None:
    """
    Downloads a PDF from the given URL and returns its content as a BytesIO object.
    """
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        pdf_content = io.BytesIO(response.content)
        return pdf_content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF from {pdf_url}: {e}")
        return None

def extract_text_from_pdf(pdf_content: io.BytesIO) -> str:
    """
    Extracts text from a PDF BytesIO object.
    """
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_content)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def summarize_text_with_llm(text: str):
    """
    Summarizes the given text using an LLM based on environment variables,
    streaming the response.
    """
    llm_provider = os.getenv("LLM_PROVIDER")
    llm_model = os.getenv("LLM_MODEL")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not llm_provider or not llm_model:
        yield "Error: LLM configuration missing (LLM_PROVIDER or LLM_MODEL)."
        return

    if llm_provider == "gemini":
        if not google_api_key:
            yield "Error: GOOGLE_API_KEY not set for Gemini provider."
            return
        try:
            genai.configure(api_key=google_api_key)
            model = genai.GenerativeModel(llm_model)
            response_stream = model.generate_content(f"Summarize the following text:\n\n{text}", stream=True)
            for chunk in response_stream:
                yield chunk.text
        except Exception as e:
            if "404 models" in str(e) and "is not found" in str(e):
                error_message = f"Error summarizing with Gemini: {e}\nPlease update LLM_MODEL in your .env file with one of the available models listed above."
                yield error_message
                print("\n--- Available Gemini Models ---")
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            print(m.name)
                except Exception as list_error:
                    print(f"Error listing models: {list_error}")
                print("-----------------------------")
            else:
                yield f"Error summarizing with Gemini: {e}"
    elif llm_provider == "openai":
        # TODO: Implement OpenAI streaming integration here
        yield "OpenAI streaming integration not yet implemented."
    elif llm_provider == "anthropic":
        if not anthropic_api_key:
            yield "Error: ANTHROPIC_API_KEY not set for Anthropic provider."
            return
        try:
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            with client.messages.stream(
                model=llm_model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
                ]
            ) as stream:
                for text_chunk in stream.text_stream:
                    yield text_chunk
        except Exception as e:
            yield f"Error summarizing with Anthropic: {e}"
    else:
        yield f"Unsupported LLM provider: {llm_provider}"


if __name__ == "__main__":
    # Example usage:
    # You can replace this with a real PDF URL for testing.
    # For instance, a PDF from arXiv:
    # https://arxiv.org/pdf/2305.15334.pdf (A Survey of Large Language Models)
    example_pdf_url = "https://arxiv.org/pdf/2305.15334.pdf"

    print(f"Attempting to download PDF from: {example_pdf_url}")
    pdf_content = download_pdf(example_pdf_url)

    if pdf_content:
        print("PDF downloaded successfully. Extracting text...")
        extracted_text = extract_text_from_pdf(pdf_content)
        if extracted_text:
            print(f"Successfully extracted {len(extracted_text)} characters. Summarizing...")
            # For now, this will return a placeholder summary.
            summary = summarize_text_with_llm(extracted_text)
            print("\n--- Summary ---")
            print(summary)
        else:
            print("No text extracted from PDF.")
    else:
        print("Failed to download PDF.")