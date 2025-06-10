import { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const newMessage = { sender: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput('');
    setLoading(true);

    try {
      let response;
      let responseData;

      if (input.toLowerCase().startsWith('search ')) {
        const query = input.substring('search '.length).trim();
        response = await fetch('http://localhost:5000/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });
        responseData = await response.json();

        if (response.ok) {
          if (responseData.length > 0) {
            // Store papers as objects to render them interactively
            setMessages((prevMessages) => [...prevMessages, { sender: 'bot', type: 'papers', data: responseData }]);
          } else {
            setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: 'No papers found for your query.' }]);
          }
        } else {
          setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: `Error: ${responseData.error || 'Unknown error during search.'}` }]);
        }
      } else if (input.toLowerCase().startsWith('summarize ')) {
        const pdf_url = input.substring('summarize '.length).trim();
        response = await fetch('http://localhost:5000/summarize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ pdf_url }),
        });

        if (!response.ok) {
          const errorText = await response.text(); // Read error as text
          throw new Error(errorText || 'Failed to summarize PDF.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let currentSummary = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          currentSummary += decoder.decode(value, { stream: true });
          setMessages((prevMessages) => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            if (lastMessage && lastMessage.type === 'summary') {
              // Update the last summary message
              return prevMessages.map((msg, idx) =>
                idx === prevMessages.length - 1
                  ? { ...msg, data: currentSummary.split('\n').filter(line => line.trim() !== '') }
                  : msg
              );
            } else {
              // Add a new summary message
              return [...prevMessages, { sender: 'bot', type: 'summary', data: currentSummary.split('\n').filter(line => line.trim() !== '') }];
            }
          });
        }

      } else {
        setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: 'Invalid command. Please use "search <query>" or "summarize <PDF_URL>".' }]);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: `Failed to connect to the backend. Please ensure the Flask server is running. Error: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!pdfUrl) return;
    setLoading(true);
    setError(null);
    setSummary('');

    try {
      const response = await fetch(`${backendUrl}/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pdf_url: pdfUrl }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to summarize PDF.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let result = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        result += decoder.decode(value, { stream: true });
        setSummary(result);
      }

    } catch (err) {
      setError(`Failed to connect to the backend. Please ensure the Flask server is running. Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Scientific-Paper Scout Agent</h1>
      </header>
      <div className="chat-container">
        <div className="messages-display">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              {msg.type === 'papers' ? (
                <div>
                  <h3>Found Papers:</h3>
                  {msg.data.map((paper, paperIndex) => (
                    <div key={paperIndex} className="paper-card">
                      <h4>{paper.title}</h4>
                      <p><strong>Authors:</strong> {paper.authors}</p>
                      <p><strong>Summary:</strong> {paper.summary}</p>
                      {paper.pdf_url && (
                        <p>
                          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">View PDF</a>
                          {' '}
                          <span className="pdf-url">({paper.pdf_url})</span>
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : msg.type === 'summary' ? (
                <div>
                  <h3>Summary:</h3>
                  {msg.data.map((line, lineIndex) => (
                    <p key={lineIndex}>{line}</p>
                  ))}
                </div>
              ) : (
                msg.text
              )}
            </div>
          ))}
          {loading && <div className="message bot">Typing...</div>}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSendMessage();
              }
            }}
            placeholder="Type your command (e.g., search LLMs, summarize PDF_URL)"
            disabled={loading}
          />
          <button onClick={handleSendMessage} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
