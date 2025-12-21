import React, { useState, useEffect } from 'react';
import GaugeChart from 'react-gauge-chart';
import axios from 'axios';
import History from './components/History';
import BatchProcessing from './components/BatchProcessing';
import { exportToPDF } from './utils/pdfExport';
import { saveToHistory } from './utils/historyManager';
import './components/components.css';
import config from './config';

function AppEnhanced() {
    // Navigation state
    const [activeTab, setActiveTab] = useState('analyzer'); // 'analyzer', 'batch', 'history'

    // Existing states
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [theme, setTheme] = useState('dark');
    const [highlightedText, setHighlightedText] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileName, setFileName] = useState('');
    const [inputMode, setInputMode] = useState('text'); // 'text' or 'file'

    // Load theme from localStorage on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        setTheme(savedTheme);
        document.documentElement.setAttribute('data-theme', savedTheme);
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    };

    // Function to highlight AI-suspected sentences (AGGRESSIVE MODE)
    const highlightAISentences = (inputText, aiProbability) => {
        if (!inputText || aiProbability < 0.3) {
            return inputText;
        }

        // Expanded AI indicator patterns for more comprehensive detection
        const aiIndicators = {
            formalTransitions: [
                'furthermore', 'moreover', 'additionally', 'consequently',
                'therefore', 'thus', 'hence', 'nevertheless', 'nonetheless',
                'subsequently', 'accordingly', 'henceforth', 'likewise',
                'similarly', 'conversely', 'alternatively', 'meanwhile'
            ],
            academicLanguage: [
                'comprehensive', 'multifaceted', 'paramount', 'crucial',
                'essential', 'significant', 'substantial', 'considerable',
                'notable', 'remarkable', 'intricate', 'nuanced', 'pivotal',
                'fundamental', 'integral', 'imperative', 'vital', 'critical'
            ],
            aiVerbs: [
                'delve', 'embark', 'leverage', 'utilize', 'utilise', 'facilitate',
                'implement', 'optimize', 'optimise', 'enhance', 'revolutionize',
                'transform', 'streamline', 'harness', 'employ', 'encompass',
                'demonstrate', 'illustrate', 'exemplify', 'underscore'
            ],
            buzzwords: [
                'innovative', 'cutting-edge', 'state-of-the-art',
                'groundbreaking', 'pioneering', 'revolutionary',
                'transformative', 'unprecedented', 'dynamic', 'robust',
                'seamless', 'holistic', 'synergistic', 'paradigm'
            ],
            commonPhrases: [
                'it is important to note', 'it should be noted',
                'it is worth mentioning', 'it is crucial to understand',
                'in conclusion', 'in summary', 'to summarize',
                'overall', 'ultimately', 'in essence', 'fundamentally',
                'it is evident', 'it is clear', 'as such', 'in other words'
            ],
            formalWords: [
                'various', 'numerous', 'multiple', 'diverse', 'myriad',
                'plethora', 'array', 'range', 'spectrum', 'variety',
                'aspect', 'factor', 'element', 'component', 'dimension'
            ]
        };

        // Split text into sentences
        const sentences = inputText.match(/[^.!?]+[.!?]+/g) || [inputText];

        const highlightedSentences = sentences.map((sentence, index) => {
            const lowerSentence = sentence.toLowerCase();
            let aiScore = 0;

            // Count AI indicators in this sentence
            Object.values(aiIndicators).forEach(indicators => {
                indicators.forEach(indicator => {
                    if (lowerSentence.includes(indicator)) {
                        aiScore += 1;
                    }
                });
            });

            // Check for passive voice (very common in AI text)
            const passivePatterns = [
                /\b(is|are|was|were|been|being)\s+\w+ed\b/gi,
                /\b(can|could|should|would|may|might|must)\s+be\s+\w+ed\b/gi,
                /\b(has|have|had)\s+been\s+\w+ed\b/gi
            ];
            passivePatterns.forEach(pattern => {
                const matches = sentence.match(pattern);
                if (matches) {
                    aiScore += matches.length * 0.5;
                }
            });

            // Check for formal conjunctions at start
            if (/^(Furthermore|Moreover|Additionally|However|Nevertheless|Consequently|Therefore|Thus)/i.test(sentence.trim())) {
                aiScore += 1.5;
            }

            // Check sentence length (AI tends to write longer sentences)
            const wordCount = sentence.trim().split(/\s+/).length;
            if (wordCount > 20) {
                aiScore += 0.5;
            }
            if (wordCount > 30) {
                aiScore += 1;
            }

            // Check for complex punctuation (commas, semicolons)
            const commaCount = (sentence.match(/,/g) || []).length;
            if (commaCount >= 2) {
                aiScore += 0.5;
            }
            if (commaCount >= 4) {
                aiScore += 1;
            }

            // Check for "that" clauses (common in AI)
            const thatCount = (lowerSentence.match(/\bthat\b/g) || []).length;
            if (thatCount >= 1) {
                aiScore += 0.3 * thatCount;
            }

            // Check for "which" clauses
            const whichCount = (lowerSentence.match(/\bwhich\b/g) || []).length;
            if (whichCount >= 1) {
                aiScore += 0.3 * whichCount;
            }

            // AGGRESSIVE THRESHOLDS - Much lower to highlight more sentences
            let threshold;
            if (aiProbability > 0.8) {
                threshold = 0.3;  // Very aggressive - highlight almost everything
            } else if (aiProbability > 0.6) {
                threshold = 0.5;  // Aggressive
            } else if (aiProbability > 0.45) {
                threshold = 1.0;  // Moderate
            } else {
                threshold = 1.5;  // Still fairly sensitive
            }

            if (aiScore >= threshold) {
                return `<span class="ai-sentence-highlight">${sentence}</span>`;
            }

            return sentence;
        }).join('');

        return highlightedSentences;
    };

    const handlePredict = async () => {
        if (!text.trim()) return;

        setLoading(true);
        setError(null);
        setResult(null);
        setHighlightedText('');

        try {
            const response = await axios.post(`${config.API_BASE_URL}/predict`, { text });
            const resultData = response.data;
            setResult(resultData);

            // Generate highlighted text with sentences
            const highlighted = highlightAISentences(text, resultData.ai_probability);
            setHighlightedText(highlighted);

            // Save to history
            saveToHistory({
                type: 'text',
                text: text,
                result: resultData
            });
        } catch (err) {
            console.error(err);
            setError('Failed to analyze text. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            processFile(file);
        }
    };

    const handleFileDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();

        const file = e.dataTransfer.files[0];
        if (file) {
            processFile(file);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const processFile = (file) => {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const validExtensions = ['.pdf', '.docx', '.doc'];

        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
            setError('Please upload a PDF or Word document (.pdf, .docx, .doc)');
            return;
        }

        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            setError('File size must be less than 10MB');
            return;
        }

        setSelectedFile(file);
        setFileName(file.name);
        setError(null);
    };

    const handleFileUpload = async () => {
        if (!selectedFile) return;

        setLoading(true);
        setError(null);
        setResult(null);
        setHighlightedText('');

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const response = await axios.post(`${config.API_BASE_URL}/predict-file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            const resultData = response.data;
            setResult(resultData);

            // Generate highlighted text from extracted text
            if (resultData.extracted_text) {
                const highlighted = highlightAISentences(resultData.extracted_text, resultData.ai_probability);
                setHighlightedText(highlighted);
            }

            // Save to history
            saveToHistory({
                type: 'file',
                fileName: selectedFile.name,
                result: resultData
            });
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || 'Failed to analyze file. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const clearFile = () => {
        setSelectedFile(null);
        setFileName('');
        setError(null);
        setResult(null);
        setHighlightedText('');
    };

    const handleExportPDF = () => {
        if (!result) return;

        const textToExport = inputMode === 'file' && result.extracted_text
            ? result.extracted_text
            : text;

        exportToPDF(result, textToExport, highlightedText, inputMode);
    };

    const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length;

    return (
        <>
            {/* Theme Toggle Button */}
            <div className="theme-toggle">
                <button
                    className="theme-toggle-btn"
                    onClick={toggleTheme}
                    aria-label="Toggle theme"
                >
                    {theme === 'dark' ? '☀' : '☾'}
                </button>
            </div>

            <div className="container">
                {/* Header Section */}
                <div className="header">
                    <h1 className="header-title">AI Content Detector</h1>
                    <p className="header-subtitle">
                        Analyze text and documents to identify AI-generated content with accuracy and clarity.
                    </p>
                </div>

                {/* Navigation Tabs */}
                <div className="nav-tabs">
                    <button
                        className={`nav-tab ${activeTab === 'analyzer' ? 'active' : ''}`}
                        onClick={() => setActiveTab('analyzer')}
                    >
                        <span>Analyzer</span>
                    </button>
                    <button
                        className={`nav-tab ${activeTab === 'batch' ? 'active' : ''}`}
                        onClick={() => setActiveTab('batch')}
                    >
                        <span>Batch Processing</span>
                    </button>
                    <button
                        className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
                        onClick={() => setActiveTab('history')}
                    >
                        <span>History</span>
                    </button>
                </div>

                {/* Analyzer Tab */}
                {activeTab === 'analyzer' && (
                    <div className="main-card">
                        {/* Mode Switcher */}
                        <div className="mode-switcher">
                            <button
                                className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
                                onClick={() => {
                                    setInputMode('text');
                                    clearFile();
                                }}
                            >
                                <span>Text Input</span>
                            </button>
                            <button
                                className={`mode-btn ${inputMode === 'file' ? 'active' : ''}`}
                                onClick={() => {
                                    setInputMode('file');
                                    setText('');
                                    setResult(null);
                                    setHighlightedText('');
                                }}
                            >
                                <span>File Upload</span>
                            </button>
                        </div>

                        {/* Text Input Mode */}
                        {inputMode === 'text' && (
                            <>
                                {/* Input Area */}
                                <div className="input-area">
                                    <div className="textarea-wrapper">
                                        <textarea
                                            placeholder="Paste your text here to analyze whether it's AI-generated or human-written... (minimum 100 words)"
                                            value={text}
                                            onChange={(e) => setText(e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* Controls */}
                                <div className="controls">
                                    <div className="word-count">
                                        <span></span>
                                        <span className="word-count-number">{wordCount}</span>
                                        <span>words</span>
                                    </div>
                                    <button
                                        className="btn-primary"
                                        onClick={handlePredict}
                                        disabled={loading || wordCount < 100}
                                    >
                                        {loading ? (
                                            <>
                                                <div className="spinner"></div>
                                                <span>Analyzing...</span>
                                            </>
                                        ) : (
                                            <>
                                                <span>Analyze Content</span>
                                            </>
                                        )}
                                    </button>
                                </div>

                                {/* Warning Message */}
                                {wordCount > 0 && wordCount < 100 && (
                                    <div className="warning-message">
                                        <span>
                                            Please add at least {100 - wordCount} more word{100 - wordCount !== 1 ? 's' : ''} for accurate analysis.
                                        </span>
                                    </div>
                                )}
                            </>
                        )}

                        {/* File Upload Mode */}
                        {inputMode === 'file' && (
                            <>
                                {/* File Upload Area */}
                                <div className="file-upload-area">
                                    {!selectedFile ? (
                                        <div
                                            className="file-drop-zone"
                                            onDrop={handleFileDrop}
                                            onDragOver={handleDragOver}
                                        >
                                            <div className="file-drop-icon"></div>
                                            <h3>Upload a document to begin analysis</h3>
                                            <p>or</p>
                                            <label className="file-select-btn">
                                                <input
                                                    type="file"
                                                    accept=".pdf,.docx,.doc"
                                                    onChange={handleFileSelect}
                                                    style={{ display: 'none' }}
                                                />
                                                Choose File
                                            </label>
                                            <p className="file-info">Supported formats: PDF, DOCX, TXT</p>
                                        </div>
                                    ) : (
                                        <div className="file-preview">
                                            <div className="file-preview-header">
                                                <div className="file-icon">
                                                    {fileName.endsWith('.pdf') ? 'PDF' : 'DOC'}
                                                </div>
                                                <div className="file-details">
                                                    <div className="file-name">{fileName}</div>
                                                    <div className="file-size">
                                                        {(selectedFile.size / 1024).toFixed(2)} KB
                                                    </div>
                                                </div>
                                                <button
                                                    className="file-remove-btn"
                                                    onClick={clearFile}
                                                    aria-label="Remove file"
                                                >
                                                    Remove
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* File Upload Controls */}
                                {selectedFile && (
                                    <div className="controls">
                                        <div className="file-ready-indicator">

                                            <span>File ready for analysis</span>
                                        </div>
                                        <button
                                            className="btn-primary"
                                            onClick={handleFileUpload}
                                            disabled={loading}
                                        >
                                            {loading ? (
                                                <>
                                                    <div className="spinner"></div>
                                                    <span>Analyzing...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <span>Analyze Content</span>
                                                </>
                                            )}
                                        </button>
                                    </div>
                                )}
                            </>
                        )}

                        {/* Error Message */}
                        {error && (
                            <div className="error-message">

                                <span>{error}</span>
                            </div>
                        )}

                        {/* Results Section */}
                        {result && (
                            <div className="result-section" id="analysis-results">
                                {/* Result Header */}
                                <div className="result-header">
                                    <h2>Analysis Results</h2>
                                    <div className={`result-label ${result.is_ai ? 'ai-text' : 'human-text'}`}>
                                        <span>{result.label}</span>
                                    </div>
                                </div>

                                {/* Export Button */}
                                <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                                    <button onClick={handleExportPDF} className="btn-secondary">
                                        Export as PDF
                                    </button>
                                </div>

                                {/* File Info (if file mode) */}
                                {inputMode === 'file' && result.filename && (
                                    <div className="file-result-info">
                                        <div className="file-result-item">
                                            <span className="file-result-label">File:</span>
                                            <span className="file-result-value">{result.filename}</span>
                                        </div>
                                        <div className="file-result-item">
                                            <span className="file-result-label">Type:</span>
                                            <span className="file-result-value">{result.file_type}</span>
                                        </div>
                                        <div className="file-result-item">
                                            <span className="file-result-label">Words:</span>
                                            <span className="file-result-value">{result.word_count?.toLocaleString()}</span>
                                        </div>
                                    </div>
                                )}

                                {/* Gauge Chart */}
                                <div className="gauge-container">
                                    <GaugeChart
                                        id="gauge-chart"
                                        nrOfLevels={20}
                                        percent={result.ai_probability}
                                        colors={theme === 'dark' ? ["#3CCB7F", "#7C83FF", "#E45C5C"] : ["#2DA66F", "#5A63FF", "#D64545"]}
                                        arcWidth={0.3}
                                        textColor={theme === 'dark' ? '#E6E9FF' : '#1C2433'}
                                        needleColor={theme === 'dark' ? '#B6BCE6' : '#4A5568'}
                                        needleBaseColor={theme === 'dark' ? '#B6BCE6' : '#4A5568'}
                                        animate={true}
                                        animDelay={0}
                                    />
                                </div>

                                {/* Probability Stats */}
                                <div className="probability-stats">
                                    <div className="stat-card">
                                        <div className="stat-label">AI-Generated Probability</div>
                                        <div className="stat-value" style={{ color: 'var(--error)' }}>
                                            {(result.ai_probability * 100).toFixed(1)}%
                                        </div>
                                    </div>
                                    <div className="stat-card">
                                        <div className="stat-label">Human-Written Probability</div>
                                        <div className="stat-value" style={{ color: 'var(--success)' }}>
                                            {(result.human_probability * 100).toFixed(1)}%
                                        </div>
                                    </div>
                                </div>

                                {/* Highlighted Text Section */}
                                {highlightedText && result.ai_probability > 0.3 && (
                                    <div className="highlighted-text-section">
                                        <div className="highlighted-text-header">

                                            <span>AI-Suspected Sentences Highlighted</span>
                                        </div>
                                        <div
                                            className="highlighted-text-content"
                                            dangerouslySetInnerHTML={{ __html: highlightedText }}
                                        />
                                        <div className="highlighted-text-legend">
                                            <span className="legend-item">
                                                <span className="legend-color ai-sentence-demo"></span>
                                                <span>Sentences with AI-like patterns (formal language, buzzwords, complex structure)</span>
                                            </span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}

                {/* Batch Processing Tab */}
                {activeTab === 'batch' && <BatchProcessing />}

                {/* History Tab */}
                {activeTab === 'history' && <History />}
            </div>
        </>
    );
}

export default AppEnhanced;
