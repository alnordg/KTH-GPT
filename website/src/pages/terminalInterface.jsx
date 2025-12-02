import { useState, useRef, useEffect } from 'react';
import './terminalInterface.css';

const INITIAL_HISTORY = [
    { type: 'system', text: 'KTH-GPT Terminal v1.0.0' },
    { type: 'system', text: 'By Students for Students' },
    { type: 'system', text: '' },
];

function TerminalInterface() {
    const [history, setHistory] = useState(INITIAL_HISTORY);
    const [inputValue, setInputValue] = useState('');
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [isLoading, setIsLoading] = useState(false);
    const terminalEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [history, isLoading]);

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const trimmedInput = inputValue.trim();
        if (!trimmedInput || isLoading) return;

        if (trimmedInput.toLowerCase() === 'clear') {
            setHistory(INITIAL_HISTORY);
            setInputValue('');
            setHistoryIndex(-1);
            if (inputRef.current) inputRef.current.style.height = 'auto';
            return;
        }

        // Add user command to history
        const userCommand = {
            type: 'command',
            text: inputValue
        };

        setHistory(prev => [...prev, userCommand]);
        setInputValue('');
        setHistoryIndex(-1);
        if (inputRef.current) inputRef.current.style.height = 'auto';
        setIsLoading(true);

        // Mock AI response
        setTimeout(() => {
            setIsLoading(false);
            const botResponse = {
                type: 'response',
                text: 'I am a helpful AI assistant. I can help you with coding, writing, and analysis.'
            };
            setHistory(prev => [...prev, botResponse, { type: 'system', text: '' }]);
        }, 1500);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSubmit(e);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            const commands = history.filter(h => h.type === 'command').map(h => h.text);
            if (commands.length === 0) return;
            if (historyIndex === -1 && inputValue.length > 0) return;

            const newIndex = historyIndex === -1 ? commands.length - 1 : Math.max(0, historyIndex - 1);
            setHistoryIndex(newIndex);
            setInputValue(commands[newIndex]);
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex === -1) return;

            const commands = history.filter(h => h.type === 'command').map(h => h.text);
            if (historyIndex >= commands.length - 1) {
                setHistoryIndex(-1);
                setInputValue('');
            } else {
                const newIndex = historyIndex + 1;
                setHistoryIndex(newIndex);
                setInputValue(commands[newIndex]);
            }
        }
    };

    return (
        <div className="terminal-container" onClick={() => !isLoading && inputRef.current?.focus()}>
            <div className="terminal-header">
                <div className="terminal-title">
                    <span className="terminal-icon">●</span>
                    <span>kth-gpt@terminal</span>
                </div>
            </div>

            <div className="terminal-body">
                <div className="terminal-output">

                    {/* ⭐ Neon ASCII Banner */}

                    {/* ⭐ Neon ASCII Banner */}
                    <div className="banner-container">
                        <pre className="ascii-banner">
                            {String.raw`
██╗  ██╗████████╗██╗  ██╗         ██████╗ ██████╗ ████████╗
██║ ██╔╝╚══██╔══╝██║  ██║        ██╔════╝ ██╔══██╗╚══██╔══╝
█████╔╝    ██║   ███████║ █████╗ ██║  ███╗██████╔╝   ██║   
██╔═██╗    ██║   ██╔══██║ ╚════╝ ██║   ██║██╔═══╝    ██║   
██║  ██╗   ██║   ██║  ██║        ╚██████╔╝██║        ██║   
╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝         ╚═════╝ ╚═╝        ╚═╝     
`}
                        </pre>
                        <img src="/logo.png" alt="KTH-GPT Logo" className="terminal-logo" />
                    </div>

                    {/* Terminal History Lines */}
                    {history.map((entry, index) => (
                        <div key={index} className={`terminal-line ${entry.type}`}>
                            {entry.type === 'command' && (
                                <>
                                    <span className="prompt">user@kth-gpt:~$</span>
                                    <span className="command-text">{entry.text}</span>
                                </>
                            )}
                            {entry.type === 'response' && (
                                <>
                                    <span className="response-prefix">[AI]</span>
                                    <span className="response-text">{entry.text}</span>
                                </>
                            )}
                            {entry.type === 'system' && (
                                <span className="system-text">{entry.text}</span>
                            )}
                        </div>
                    ))}

                    {isLoading && (
                        <div className="terminal-line loading">
                            <span className="response-prefix">[AI]</span>
                            <span className="loading-text">
                                <span className="cursor-blink">▊</span>
                            </span>
                        </div>
                    )}

                    <div ref={terminalEndRef} />
                </div>

                <form onSubmit={handleSubmit} className="terminal-input-line">
                    <span className="prompt">user@kth-gpt:~$</span>
                    <textarea
                        ref={inputRef}
                        value={inputValue}
                        onChange={(e) => {
                            setInputValue(e.target.value);
                            setHistoryIndex(-1);
                            // Auto-resize
                            e.target.style.height = 'auto';
                            e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px'; // Max height approx 5-6 lines
                        }}
                        onKeyDown={handleKeyDown}
                        className="terminal-input"
                        autoComplete="off"
                        spellCheck="false"
                        rows={1}
                    />
                </form>
            </div>
        </div>
    );
}

export default TerminalInterface;
