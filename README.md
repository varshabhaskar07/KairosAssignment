# Scientific Paper Scout Agent

## Project Overview

This project implements a backend system for a "Scientific Paper Scout Agent" application. It allows users to search for scientific papers and summarize PDF documents using various Large Language Models (LLMs). The system is designed with a modular and extensible architecture, supporting different LLM providers and offering both a Command Line Interface (CLI) and a React-based web interface.

## Features

-   **Paper Search**: Search for scientific papers using the arXiv API.
-   **PDF Summarization**: Summarize the content of PDF documents using LLMs.
-   **Streaming**: Supports streaming responses for long-running LLM operations.
-   **Model Agnosticism**: Easily integrate and switch between different LLM providers (e.g., Gemini, Anthropic, OpenAI).
-   **Tool Call Logging**: Logs all tool calls made by the LLM for transparency and debugging.
-   **Modular Architecture**: Clear separation of concerns with dedicated servers for paper search and PDF summarization.
-   **User Interfaces**: Provides both a CLI for quick interactions and a React frontend for a rich user experience.

## Architecture

The project follows a client-server architecture with several key components:

1.  **Agent Host (main.py)**: The central Flask-based backend server that exposes API endpoints for paper search and PDF summarization. It orchestrates calls to the specialized MCP servers and handles LLM interactions.
2.  **Paper Search MCP Server (paper_search_server.py)**: A module responsible for interacting with external paper databases (currently arXiv) and retrieving paper metadata.
3.  **PDF Summarize MCP Server (pdf_summarize_server.py)**: A module responsible for downloading PDFs, extracting text, and summarizing the content using configured LLMs.
4.  **CLI (cli.py)**: A command-line interface for interacting with the Agent Host.
5.  **React Frontend**: A web-based user interface for a more interactive experience.

```mermaid
graph TD
    A[User] -->|Interacts with| B(CLI) 
    A -->|Interacts with| C(React Frontend)

    B -->|Sends requests to| D(Agent Host: main.py)
    C -->|Sends requests to| D

    D -->|Calls| E(Paper Search MCP Server: paper_search_server.py)
    D -->|Calls| F(PDF Summarize MCP Server: pdf_summarize_server.py)

    E -->|Queries| G(arXiv API)
    F -->|Downloads| I(PDF URLs)
    F -->|Uses| H(LLM Providers: Gemini, Anthropic, OpenAI)

    G -->|Returns search results| E
    I -->|Provides content| F
    H -->|Returns summaries| F

    E -->|Returns paper data| D
    F -->|Returns summarized text| D

    D -->|Sends responses to| B
    D -->|Sends responses to| C