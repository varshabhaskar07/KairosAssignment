import sys
import os
import time
import json
from datetime import datetime
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, 'kairos-take-home-0')
sys.path.append(project_root)

from paper_search_server import search_arxiv
from pdf_summarize_server import download_pdf, extract_text_from_pdf, summarize_text_with_llm

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Define the path to the backend scripts
PAPER_SEARCH_SCRIPT = "d:\\KairosAssignment\\kairos-take-home-0\\paper_search_server.py"
PDF_SUMMARIZE_SCRIPT = "d:\\KairosAssignment\\kairos-take-home-0\\pdf_summarize_server.py"

@app.route('/')
def index():
    return "Scientific Paper Scout Backend is running!"

def main():
    print("Welcome to the Scientific-Paper Scout Agent!")
    print("You can search for papers (e.g., 'search large language models') or summarize a PDF (e.g., 'summarize <PDF_URL>').")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == 'exit':
            print("Exiting.")
            break
        elif user_input.lower().startswith('search '):
            query = user_input[len('search '):].strip()
            print(f"Searching for papers related to: '{query}'...")
            
            start_time = time.time()
            print(f"Tool Call: search_arxiv(query='{query}')")
            try:
                papers = search_arxiv(query)
                end_time = time.time()
                latency = end_time - start_time
                print(f"Tool Outcome: search_arxiv - Success (Latency: {latency:.2f}s)")
                if papers:
                    for i, paper in enumerate(papers):
                        print(f"\n--- Paper {i+1} ---")
                        print(f"Title: {paper['title']}")
                        print(f"Authors: {', '.join(paper['authors'])}")
                        print(f"Summary: {paper['summary']}") 
                        print(f"PDF URL: {paper['pdf_url']}")
                else:
                    print("No papers found for your query.")
            except Exception as e:
                end_time = time.time()
                latency = end_time - start_time
                print(f"Tool Outcome: search_arxiv - Failed (Error: {e}, Latency: {latency:.2f}s)")
                print(f"An error occurred during search: {e}")

        elif user_input.lower().startswith('summarize '):
            pdf_url = user_input[len('summarize '):].strip()
            if pdf_url:
                print(f"Downloading and summarizing PDF from: {pdf_url}...")
                try:
                    # Log download_pdf call
                    start_time_download = time.time()
                    print(f"Tool Call: download_pdf(pdf_url='{pdf_url}')")
                    pdf_path = download_pdf(pdf_url)
                    end_time_download = time.time()
                    latency_download = end_time_download - start_time_download
                    if pdf_path:
                        print(f"Tool Outcome: download_pdf - Success (Latency: {latency_download:.2f}s)")
                        
                        # Log extract_text_from_pdf call
                        start_time_extract = time.time()
                        print(f"Tool Call: extract_text_from_pdf(pdf_path='{pdf_path}')")
                        text = extract_text_from_pdf(pdf_path)
                        end_time_extract = time.time()
                        latency_extract = end_time_extract - start_time_extract
                        if text:
                            print(f"Tool Outcome: extract_text_from_pdf - Success (Latency: {latency_extract:.2f}s)")
                            print("Text extracted. Summarizing...")
                            
                            # Log summarize_text_with_llm call
                            start_time_summarize = time.time()
                            print(f"Tool Call: summarize_text_with_llm(text_length={len(text)}) ")
                            summary = summarize_text_with_llm(text)
                            end_time_summarize = time.time()
                            latency_summarize = end_time_summarize - start_time_summarize
                            print(f"Tool Outcome: summarize_text_with_llm - Success (Latency: {latency_summarize:.2f}s)")
                            print("\n--- Summary ---")
                            print(summary)
                            print("-----------------") 
                        else:
                            print(f"Tool Outcome: extract_text_from_pdf - Failed (No text extracted, Latency: {latency_extract:.2f}s)")
                            print("Could not extract text from PDF.")
                    else:
                        print(f"Tool Outcome: download_pdf - Failed (Could not download, Latency: {latency_download:.2f}s)")
                        print("Could not download PDF.")
                except Exception as e:
                    print(f"An error occurred during summarization: {e}")
            else:
                print("Please provide a PDF URL to summarize.")
        else:
            print("Invalid command. Please use 'search <query>' or 'summarize <PDF_URL>'.")


def log_tool_call(tool_name, arguments, outcome, latency):
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "tool_name": tool_name,
        "arguments": arguments,
        "outcome": outcome,
        "latency": f"{latency:.2f}s"
    }
    print(f"[LOG] {json.dumps(log_entry)}")

@app.route('/search', methods=['POST'])
def search_papers_api():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    start_time = time.time()
    try:
        papers = search_arxiv(query)
        outcome = "success"
        response_data = []
        for paper in papers:
            response_data.append({
                "title": paper['title'],
                "authors": paper['authors'],
                "summary": paper['summary'],
                "pdf_url": paper['pdf_url']
            })
        return jsonify(response_data)
    except Exception as e:
        outcome = f"error: {e}"
        return jsonify({'error': str(e)}), 500
    finally:
        end_time = time.time()
        latency = end_time - start_time
        log_tool_call("search_arxiv", {"query": query}, outcome, latency)

@app.route('/summarize', methods=['POST'])
def summarize_pdf_api():
    data = request.get_json()
    pdf_url = data.get('pdf_url')

    if not pdf_url:
        return jsonify({'error': 'PDF URL parameter is required'}), 400

    def generate():
        try:
            
            start_time_download = time.time()
            pdf_path = download_pdf(pdf_url)
            latency_download = time.time() - start_time_download
            log_tool_call("download_pdf", {"pdf_url": pdf_url}, "success", latency_download)

            # Extract text
            start_time_extract = time.time()
            log_pdf_path_arg = f"BytesIO object (size: {pdf_path.getbuffer().nbytes} bytes)" if pdf_path else "None"
            text_content = extract_text_from_pdf(pdf_path)
            latency_extract = time.time() - start_time_extract
            log_tool_call("extract_text_from_pdf", {"pdf_path": log_pdf_path_arg}, "success", latency_extract)

            
            start_time_summarize = time.time()
            
            for chunk in summarize_text_with_llm(text_content):
                yield chunk
            latency_summarize = time.time() - start_time_summarize
            log_tool_call("summarize_text_with_llm", {"text_length": len(text_content)}, "success", latency_summarize)

        except Exception as e:
            error_message = str(e)
            
            if "download_pdf" not in locals() or "latency_download" not in locals():
                log_tool_call("download_pdf", {"pdf_url": pdf_url}, f"error: {error_message}", 0)
            if "extract_text_from_pdf" not in locals() or "latency_extract" not in locals():
                log_tool_call("extract_text_from_pdf", {"pdf_url": pdf_url}, f"error: {error_message}", 0)
            if "summarize_text_with_llm" not in locals() or "latency_summarize" not in locals():
                log_tool_call("summarize_text_with_llm", {"pdf_url": pdf_url}, f"error: {error_message}", 0)
            yield f"Error: {error_message}"

    return Response(generate(), mimetype='text/plain')


if __name__ == "__main__":
    app.run(debug=True, port=5000)