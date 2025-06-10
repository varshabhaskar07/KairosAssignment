import requests
import xml.etree.ElementTree as ET

def search_arxiv(query: str, max_results: int = 10):
    """
    Queries the arXiv API for scientific papers.

    Args:
        query (str): The search query.
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries, each representing a paper with title, authors, summary, and URL.
    """
    base_url = "http://export.arxiv.org/api/query?"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        root = ET.fromstring(response.content)

        papers = []
        # arXiv API uses Atom XML format, namespace needs to be handled
        # Atom namespace: http://www.w3.org/2005/Atom
        # arXiv namespace: http://arxiv.org/schemas/atom
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else 'N/A'
            summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else 'N/A'
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            
            authors = []
            for author_elem in entry.findall('atom:author', ns):
                name_elem = author_elem.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())

            papers.append({
                "title": title,
                "authors": ", ".join(authors),
                "summary": summary,
                "pdf_url": pdf_url
            })
        return papers

    except requests.exceptions.RequestException as e:
        print(f"Error querying arXiv API: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML response from arXiv: {e}")
        return []

if __name__ == "__main__":
    # Example usage:
    print("Searching for 'large language models'...")
    results = search_arxiv("large language models", max_results=3)
    if results:
        for i, paper in enumerate(results):
            print(f"\n--- Paper {i+1} ---")
            print(f"Title: {paper['title']}")
            print(f"Authors: {paper['authors']}")
            print(f"Summary: {paper['summary'][:200]}...") # Truncate summary for display
            print(f"PDF URL: {paper['pdf_url']}")
    else:
        print("No results found or an error occurred.")