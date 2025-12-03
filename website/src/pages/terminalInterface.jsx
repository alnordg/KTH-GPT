import { useState, useRef, useEffect } from 'react';
import { processCommand, COMMANDS, THEMES } from '../utils/commands';
import Typewriter from '../components/Typewriter';
import AsciiAnimation from '../components/AsciiAnimation';
import { BRAINROT_ANIMATIONS } from '../utils/animations';
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
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('kth-gpt-theme') || 'default';
    });
    const [isBrainrot, setIsBrainrot] = useState(false);
    const [animationIndex, setAnimationIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(false);
    const [tabSearchPrefix, setTabSearchPrefix] = useState(null);
    const [suggestion, setSuggestion] = useState('');
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

    // Auto-resize input when value changes
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto';
            inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 150) + 'px';
        }
    }, [inputValue]);

    // Cycle brainrot animations
    useEffect(() => {
        let interval;
        if (isBrainrot) {
            interval = setInterval(() => {
                setAnimationIndex(prev => (prev + 1) % BRAINROT_ANIMATIONS.length);
            }, 5000);
        }
        return () => clearInterval(interval);
    }, [isBrainrot]);

    // Save theme to localStorage
    useEffect(() => {
        localStorage.setItem('kth-gpt-theme', theme);
    }, [theme]);

    // Calculate suggestion for ghost text
    useEffect(() => {
        const input = inputValue.toLowerCase();
        if (!input) {
            setSuggestion('');
            return;
        }

        // Check for theme argument
        if (input.startsWith('theme ')) {
            const argPrefix = input.slice(6);
            if (!argPrefix) {
                setSuggestion(THEMES[0]);
                return;
            }
            const matches = THEMES.filter(t => t.startsWith(argPrefix));
            if (matches.length > 0) {
                const match = matches[0];
                if (match.startsWith(argPrefix)) {
                    setSuggestion(match.slice(argPrefix.length));
                } else {
                    setSuggestion('');
                }
            } else {
                setSuggestion('');
            }
            return;
        }

        // Check for command
        const matches = Object.keys(COMMANDS).filter(cmd => cmd.startsWith(input));
        if (matches.length > 0) {
            const match = matches[0];
            setSuggestion(match.slice(input.length));
        } else {
            setSuggestion('');
        }
    }, [inputValue]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const trimmedInput = inputValue.trim();
        if (!trimmedInput || isLoading) return;

        // Process local commands
        const commandResult = processCommand(trimmedInput);
        if (commandResult) {
            if (commandResult.type === 'clear') {
                setHistory(INITIAL_HISTORY);
                setInputValue('');
                setHistoryIndex(-1);
                return;
            }

            if (commandResult.type === 'theme') {
                setTheme(commandResult.theme);
                setHistory(prev => [...prev,
                { type: 'command', text: trimmedInput },
                { type: 'system', text: `Theme changed to ${commandResult.theme}` }
                ]);
                setInputValue('');
                setHistoryIndex(-1);
                return;
            }

            if (commandResult.type === 'response') {
                setHistory(prev => [...prev,
                { type: 'command', text: trimmedInput },
                { type: 'command-response', text: commandResult.text, link: commandResult.link }
                ]);
                setInputValue('');
                setHistoryIndex(-1);
                return;
            }

            if (commandResult.type === 'brainrot') {
                const newBrainrotState = !isBrainrot;
                setIsBrainrot(newBrainrotState);

                setHistory(prev => [...prev,
                { type: 'command', text: trimmedInput },
                { type: 'system', text: newBrainrotState ? 'INITIATING BRAINROT PROTOCOL...' : 'Brainrot deactivated.' }
                ]);
                setInputValue('');
                setHistoryIndex(-1);
                return;
            }

            if (commandResult.type === 'copy') {
                const lastResponse = [...history].reverse().find(h => h.type === 'response');

                if (lastResponse) {
                    try {
                        await navigator.clipboard.writeText(lastResponse.text);
                        setHistory(prev => [...prev,
                        { type: 'command', text: trimmedInput },
                        { type: 'system', text: 'Copied last response to clipboard.' }
                        ]);
                    } catch (err) {
                        setHistory(prev => [...prev,
                        { type: 'command', text: trimmedInput },
                        { type: 'system', text: 'Failed to copy to clipboard.' }
                        ]);
                    }
                } else {
                    setHistory(prev => [...prev,
                    { type: 'command', text: trimmedInput },
                    { type: 'system', text: 'No response found to copy.' }
                    ]);
                }
                setInputValue('');
                setHistoryIndex(-1);
                return;
            }
        }

        // Add user command to history
        const userCommand = {
            type: 'command',
            text: inputValue
        };

        setHistory(prev => [...prev, userCommand]);
        setInputValue('');
        setHistoryIndex(-1);
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
            const { selectionStart, value } = e.target;
            const lines = value.split('\n');
            let currentLine = 0;
            let charCount = 0;
            for (let i = 0; i < lines.length; i++) {
                charCount += lines[i].length + 1;
                if (charCount > selectionStart) {
                    currentLine = i;
                    break;
                }
            }

            const isFirstLine = currentLine === 0;

            if (isFirstLine && (inputValue === '' || historyIndex !== -1)) {
                e.preventDefault();
                const commands = history.filter(h => h.type === 'command').map(h => h.text);
                if (commands.length === 0) return;

                const newIndex = historyIndex === -1 ? commands.length - 1 : Math.max(0, historyIndex - 1);
                setHistoryIndex(newIndex);
                setInputValue(commands[newIndex]);

                setTimeout(() => {
                    if (inputRef.current) {
                        inputRef.current.selectionStart = inputRef.current.value.length;
                        inputRef.current.selectionEnd = inputRef.current.value.length;
                    }
                }, 0);
            }
        } else if (e.key === 'ArrowDown') {
            const { selectionStart, value } = e.target;
            const lines = value.split('\n');
            let currentLine = 0;
            let charCount = 0;
            for (let i = 0; i < lines.length; i++) {
                charCount += lines[i].length + 1;
                if (charCount > selectionStart) {
                    currentLine = i;
                    break;
                }
            }

            const isLastLine = currentLine === lines.length - 1;

            if (isLastLine && historyIndex !== -1) {
                e.preventDefault();
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
        } else if (e.key === 'Tab') {
            e.preventDefault();

            // Determine the prefix to search for (either current input or stored prefix)
            const currentInput = inputValue;
            const searchPrefix = tabSearchPrefix !== null ? tabSearchPrefix : currentInput;

            // If we haven't stored a prefix yet, store it now
            if (tabSearchPrefix === null) {
                setTabSearchPrefix(currentInput);
            }

            // Check if we are completing a theme argument
            if (searchPrefix.startsWith('theme ')) {
                const argPrefix = searchPrefix.slice(6).toLowerCase();
                const matches = THEMES.filter(t => t.startsWith(argPrefix));

                if (matches.length > 0) {
                    // Find current match in the list to cycle to next
                    const currentArg = currentInput.slice(6).toLowerCase();
                    const currentIndex = matches.indexOf(currentArg);

                    // If current arg is in matches, pick next, otherwise pick first
                    const nextIndex = currentIndex !== -1 ? (currentIndex + 1) % matches.length : 0;
                    setInputValue('theme ' + matches[nextIndex]);
                }
                return;
            }

            // Otherwise, completing a command
            const cmdPrefix = searchPrefix.toLowerCase();
            if (!cmdPrefix) return;

            const matches = Object.keys(COMMANDS).filter(cmd => cmd.startsWith(cmdPrefix));

            if (matches.length > 0) {
                const currentCmd = currentInput.trim().toLowerCase();
                // Check if current input matches one of the candidates (ignoring trailing space for args)
                const currentIndex = matches.findIndex(m =>
                    currentCmd === m || currentCmd === m + ' '
                );

                const nextIndex = currentIndex !== -1 ? (currentIndex + 1) % matches.length : 0;
                const match = matches[nextIndex];

                const needsSpace = COMMANDS[match].allowArgs;
                setInputValue(match + (needsSpace ? ' ' : ''));
            }
        }
    };

    return (
        <div className={`terminal-container ${theme}`}>
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
                        {isBrainrot && (
                            <AsciiAnimation
                                className="terminal-logo"
                                speed={100}
                                frames={BRAINROT_ANIMATIONS[animationIndex]}
                            />
                        )}
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
                                    <span className="response-prefix">[AI] </span>
                                    <span className="response-text">
                                        <Typewriter text={entry.text} onUpdate={scrollToBottom} />
                                    </span>
                                </>
                            )}
                            {entry.type === 'command-response' && (
                                <>
                                    <span className="response-prefix">[SYSTEM] </span>
                                    <span className="response-text">
                                        {entry.link ? (
                                            <>
                                                GitHub: <a
                                                    href={entry.link}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="terminal-link"
                                                >
                                                    {entry.link}
                                                </a>
                                                <br />
                                                Created by: Alno & Guma
                                            </>
                                        ) : entry.text}
                                    </span>
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
                    <div className="input-wrapper">
                        {suggestion && (
                            <div className="terminal-ghost">
                                {inputValue}<span className="ghost-suggestion">{suggestion}</span>
                            </div>
                        )}
                        <textarea
                            ref={inputRef}
                            value={inputValue}
                            onChange={(e) => {
                                setInputValue(e.target.value);
                                setHistoryIndex(-1);
                                setTabSearchPrefix(null);
                            }}
                            onKeyDown={handleKeyDown}
                            onClick={() => inputRef.current?.focus()}
                            className="terminal-input"
                            autoComplete="off"
                            spellCheck="false"
                            rows={1}
                        />
                    </div>
                </form>
            </div>
        </div>
    );
}

export default TerminalInterface;
