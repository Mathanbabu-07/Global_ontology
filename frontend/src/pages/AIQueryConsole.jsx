import { useState, useRef, useEffect } from 'react';
import { HiOutlinePaperAirplane, HiOutlineMicrophone } from 'react-icons/hi';
import { TbBrain } from 'react-icons/tb';
import { sendQuery } from '../services/api';

const SUGGESTIONS = [
    'Collect latest geopolitical developments related to India',
    'Extract economic policy updates from monitored sources',
    'Find defense related updates from the last 24 hours',
    'Summarize climate change developments globally',
];

export default function AIQueryConsole() {
    const [messages, setMessages] = useState([
        {
            role: 'ai',
            content: 'Welcome to the AI Query Console. I can help you extract intelligence from monitored sources. Try asking about geopolitical developments, economic trends, defense updates, or any other intelligence domain.',
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [listening, setListening] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSpeech = () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Voice input is not supported in this browser.');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => setListening(true);
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setInput(prev => prev + (prev ? ' ' : '') + transcript);
        };
        recognition.onerror = (e) => console.error('Speech recognition error:', e.error);
        recognition.onend = () => setListening(false);

        recognition.start();
    };

    const handleSend = async (text) => {
        const prompt = text || input.trim();
        if (!prompt || loading) return;

        setMessages((prev) => [...prev, { role: 'user', content: prompt }]);
        setInput('');
        setLoading(true);

        try {
            const res = await sendQuery(prompt);
            setMessages((prev) => [...prev, { role: 'ai', content: res.data.response || res.data.message || JSON.stringify(res.data, null, 2) }]);
        } catch (err) {
            setMessages((prev) => [...prev, {
                role: 'ai',
                content: `⚠️ Error: ${err.response?.data?.error || 'Could not reach the backend. Make sure the Flask server is running on port 5000.'}`,
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div>
            <div className="page-header">
                <h1>AI Query Console</h1>
                <p>Query monitored sources using natural language</p>
            </div>

            {/* Suggestions */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
                {SUGGESTIONS.map((s, i) => (
                    <button
                        key={i}
                        className="btn btn-secondary"
                        style={{ fontSize: '12px', padding: '7px 14px' }}
                        onClick={() => handleSend(s)}
                        disabled={loading}
                    >
                        {s}
                    </button>
                ))}
            </div>

            <div className="chat-container">
                <div className="chat-messages">
                    {messages.map((msg, i) => (
                        <div key={i} className={`chat-message ${msg.role}`}>
                            <div className="msg-avatar">
                                {msg.role === 'user' ? '👤' : <TbBrain />}
                            </div>
                            <div className="msg-bubble">
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="chat-message ai">
                            <div className="msg-avatar"><TbBrain /></div>
                            <div className="msg-bubble thinking-bubble">
                                <span className="thinking-font">Thinking... processing intelligence</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-area">
                    <button
                        className={`mic-btn ${listening ? 'listening' : ''}`}
                        onClick={handleSpeech}
                        title="Voice Input"
                        disabled={loading}
                    >
                        <HiOutlineMicrophone />
                    </button>
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about geopolitics, economics, defense, technology, climate, society..."
                        disabled={loading}
                    />
                    <button
                        className={`send-btn ${input.trim() ? 'active' : ''}`}
                        onClick={() => handleSend()}
                        disabled={loading || !input.trim()}
                    >
                        <HiOutlinePaperAirplane />
                    </button>
                </div>
            </div>
        </div>
    );
}
