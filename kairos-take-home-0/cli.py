import requests
import time
import sys
import os


BACKEND_URL = "http://127.0.0.1:5000"

BASE_URL = "http://localhost:5000"

def search_papers(query):
    url = f"{BASE_URL}/search"
    start_time = time.time()
    print(f"Tool Call: search_papers_api(query='{query}')")
    try:
        response = requests.post(url, json={"query": query})
        response.raise_for_status()  # Raise an exception for HTTP errors
        papers = response.json()
        end_time = time.time()
        latency = end_time - start_time
        print(f"Tool Outcome: search_papers_api - Success (Latency: {latency:.2f}s)")
        if papers:
            print("Found Papers:")
            for i, paper in enumerate(papers):
                print(f"\n--- Paper {i+1} ---")
                print(f"Title: {paper.get('title', 'N/A')}")
                print(f"Authors: {paper.get('authors', 'N/A')}")
                print(f"Summary: {paper.get('summary', 'N/A')}")
                if paper.get('pdf_url'):
                    print(f"PDF URL: {paper['pdf_url']}")
        else:
            print("No papers found for your query.")
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        latency = end_time - start_time
        print(f"Tool Outcome: search_papers_api - Failed (Error: {e}, Latency: {latency:.2f}s)")
        print(f"Error connecting to backend: {e}")
    except ValueError:
        end_time = time.time()
        latency = end_time - start_time
        print(f"Tool Outcome: search_papers_api - Failed (Error: Could not decode JSON response, Latency: {latency:.2f}s)")
        print("Error: Could not decode JSON response from backend.")

def summarize_pdf(pdf_url):
    url = f"{BASE_URL}/summarize"
    start_time = time.time()
    print(f"Tool Call: summarize_pdf_api(pdf_url='{pdf_url}')")
    try:
        response = requests.post(url, json={"pdf_url": pdf_url})
        response.raise_for_status()  # Raise an exception for HTTP errors
        summary_data = response.json()
        end_time = time.time()
        latency = end_time - start_time
        print(f"Tool Outcome: summarize_pdf_api - Success (Latency: {latency:.2f}s)")
        print(f"Summary:\n{summary_data.get('summary', 'N/A')}")
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        latency = end_time - start_time
        print(f"Tool Outcome: summarize_pdf_api - Failed (Error: {e}, Latency: {latency:.2f}s)")
        print(f"Error connecting to backend: {e}")
    except ValueError:
        end_time = time.time()
        latency = end_time - start_time
        print(f"Tool Outcome: summarize_pdf_api - Failed (Error: Could not decode JSON response, Latency: {latency:.2f}s)")
        print("Error: Could not decode JSON response from backend.")

def main():
    print("Scientific-Paper Scout Agent CLI (Type 'exit' to quit)")
    while True:
        user_input = input("\nEnter command (e.g., search LLMs, summarize PDF_URL): ").strip()
        if user_input.lower() == 'exit':
            print("Exiting CLI. Goodbye!")
            break

        if user_input.lower().startswith('search '):
            query = user_input[len('search '):].strip()
            if query:
                search_papers(query)
            else:
                print("Please provide a search query. Example: search LLMs")
        elif user_input.lower().startswith('summarize '):
            pdf_url = user_input[len('summarize '):].strip()
            if pdf_url:
                print(f"Downloading and summarizing PDF from: {pdf_url}...")
                try:
                    start_time_api = time.time()
                    print(f"Tool Call: summarize_pdf_api(pdf_url='{pdf_url}')")
                    response = requests.post(f"{BACKEND_URL}/summarize", json={'pdf_url': pdf_url}, stream=True)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    full_summary = ""
                    print("\n--- Summary ---")
                    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                        if chunk:
                            full_summary += chunk
                            print(chunk, end='', flush=True)
                    print("\n-----------------")

                    end_time_api = time.time()
                    latency_api = end_time_api - start_time_api
                    print(f"Tool Outcome: summarize_pdf_api - Success (Latency: {latency_api:.2f}s)")

                except requests.exceptions.RequestException as e:
                    end_time_api = time.time()
                    latency_api = end_time_api - start_time_api
                    print(f"Tool Outcome: summarize_pdf_api - Failed (Error: {e}, Latency: {latency_api:.2f}s)")
                    print(f"Error connecting to backend: {e}")
                except Exception as e:
                    end_time_api = time.time()
                    latency_api = end_time_api - start_time_api
                    print(f"Tool Outcome: summarize_pdf_api - Failed (Error: {e}, Latency: {latency_api:.2f}s)")
                    print(f"An unexpected error occurred: {e}")
            else:
                print("Please provide a PDF URL to summarize.")
        else:
            print("Invalid command. Please use 'search <query>' or 'summarize <PDF_URL>'.")

if __name__ == "__main__":
    main()