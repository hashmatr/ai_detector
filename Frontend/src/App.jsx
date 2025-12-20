import React, { useState, useEffect } from 'react'
import GaugeChart from 'react-gauge-chart'
import axios from 'axios'
import config from './config'

function App() {
    const [text, setText] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [theme, setTheme] = useState('dark')
    const [highlightedText, setHighlightedText] = useState('')
    const [selectedFile, setSelectedFile] = useState(null)
    const [fileName, setFileName] = useState('')
    const [inputMode, setInputMode] = useState('text') // 'text' or 'file'
    const [detectionMode, setDetectionMode] = useState('ml') // 'ml' or 'hybrid'

    // Load theme from localStorage on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'dark'
        setTheme(savedTheme)
        document.documentElement.setAttribute('data-theme', savedTheme)
    }, [])

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark'
        setTheme(newTheme)
        localStorage.setItem('theme', newTheme)
        document.documentElement.setAttribute('data-theme', newTheme)
    }

    // Function to highlight AI-suspected sentences
    const highlightAISentences = (inputText, aiProbability) => {
        if (!inputText || aiProbability < 0.3) {
            return inputText
        }

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
            ]
        }

        const sentences = inputText.match(/[^.!?]+[.!?]+/g) || [inputText]

        const highlightedSentences = sentences.map((sentence) => {
            const lowerSentence = sentence.toLowerCase()
            let aiScore = 0

            Object.values(aiIndicators).forEach(indicators => {
                indicators.forEach(indicator => {
                    if (lowerSentence.includes(indicator)) {
                        aiScore += 1
                    }
                })
            })

            const passivePatterns = [
                /\b(is|are|was|were|been|being)\s+\w+ed\b/gi,
                /\b(can|could|should|would|may|might|must)\s+be\s+\w+ed\b/gi
            ]
            passivePatterns.forEach(pattern => {
                const matches = sentence.match(pattern)
                if (matches) aiScore += matches.length * 0.5
            })

            if (/^(Furthermore|Moreover|Additionally|However|Nevertheless|Consequently|Therefore|Thus)/i.test(sentence.trim())) {
                aiScore += 1.5
            }

            const wordCount = sentence.trim().split(/\s+/).length
            if (wordCount > 20) aiScore += 0.5
            if (wordCount > 30) aiScore += 1

            let threshold = aiProbability > 0.8 ? 0.3 : aiProbability > 0.6 ? 0.5 : aiProbability > 0.45 ? 1.0 : 1.5

            if (aiScore >= threshold) {
                return `<span class="ai-sentence-highlight">${sentence}</span>`
            }
            return sentence
        }).join('')

        return highlightedSentences
    }

    const handlePredict = async () => {
        if (!text.trim()) return

        setLoading(true)
        setError(null)
        setResult(null)
        setHighlightedText('')

        try {
            const endpoint = detectionMode === 'hybrid' ? '/predict-hybrid' : '/predict-ml'
            const response = await axios.post(`${config.API_BASE_URL}${endpoint}`, { text })
            const resultData = response.data
            setResult(resultData)

            const highlighted = highlightAISentences(text, resultData.ai_probability)
            setHighlightedText(highlighted)
        } catch (err) {
            console.error(err)
            setError(err.response?.data?.error || 'Failed to analyze text. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    const handleFileSelect = (e) => {
        const file = e.target.files[0]
        if (file) processFile(file)
    }

    const handleFileDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        const file = e.dataTransfer.files[0]
        if (file) processFile(file)
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        e.stopPropagation()
    }

    const processFile = (file) => {
        const validExtensions = ['.pdf', '.docx', '.doc']
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase()

        if (!validExtensions.includes(fileExtension)) {
            setError('Please upload a PDF or Word document')
            return
        }

        if (file.size > 10 * 1024 * 1024) {
            setError('File size must be less than 10MB')
            return
        }

        setSelectedFile(file)
        setFileName(file.name)
        setError(null)
    }

    const handleFileUpload = async () => {
        if (!selectedFile) return

        setLoading(true)
        setError(null)
        setResult(null)
        setHighlightedText('')

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)
            formData.append('mode', detectionMode)

            const response = await axios.post(`${config.API_BASE_URL}/predict-file`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            const resultData = response.data
            setResult(resultData)

            if (resultData.extracted_text) {
                const highlighted = highlightAISentences(resultData.extracted_text, resultData.ai_probability)
                setHighlightedText(highlighted)
            }
        } catch (err) {
            console.error(err)
            setError(err.response?.data?.error || 'Failed to analyze file.')
        } finally {
            setLoading(false)
        }
    }

    const clearFile = () => {
        setSelectedFile(null)
        setFileName('')
        setError(null)
        setResult(null)
        setHighlightedText('')
    }

    const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length

    return (
        <>
            {/* Theme Toggle */}
            <div className="theme-toggle">
                <button className="theme-toggle-btn" onClick={toggleTheme} aria-label="Toggle theme">
                    {theme === 'dark' ? '☀' : '☾'}
                </button>
            </div>

            <div className="container">
                {/* Header */}
                <div className="header">
                    <h1 className="header-title">AI Content Detector</h1>
                    <p className="header-subtitle">
                        Analyze text and documents to identify AI-generated content with accuracy and clarity.
                    </p>
                </div>

                {/* Main Card */}
                <div className="main-card">
                    {/* Detection Mode Selector */}
                    <div className="detection-mode-selector">
                        <div className="mode-label">Detection Mode:</div>
                        <div className="detection-modes">
                            <button
                                className={`detection-mode-btn ${detectionMode === 'ml' ? 'active' : ''}`}
                                onClick={() => setDetectionMode('ml')}
                            >
                                <span className="mode-icon">🔬</span>
                                <span className="mode-title">Pure ML</span>
                                <span className="mode-desc">SVM + AdaBoost + Random Forest</span>
                            </button>
                            <button
                                className={`detection-mode-btn ${detectionMode === 'hybrid' ? 'active' : ''}`}
                                onClick={() => setDetectionMode('hybrid')}
                            >
                                <span className="mode-icon">🤖</span>
                                <span className="mode-title">Hybrid ML+DL</span>
                                <span className="mode-desc">RoBERTa + ML Ensemble</span>
                            </button>
                        </div>
                    </div>

                    {/* Mode Switcher (Text/File) */}
                    <div className="mode-switcher">
                        <button
                            className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
                            onClick={() => { setInputMode('text'); clearFile() }}
                        >
                            <span>Text Input</span>
                        </button>
                        <button
                            className={`mode-btn ${inputMode === 'file' ? 'active' : ''}`}
                            onClick={() => { setInputMode('file'); setText(''); setResult(null); setHighlightedText('') }}
                        >
                            <span>File Upload</span>
                        </button>
                    </div>

                    {/* Text Input Mode */}
                    {inputMode === 'text' && (
                        <>
                            <div className="input-area">
                                <div className="textarea-wrapper">
                                    <textarea
                                        placeholder="Paste your text here to analyze whether it's AI-generated or human-written... (minimum 100 words)"
                                        value={text}
                                        onChange={(e) => setText(e.target.value)}
                                    />
                                </div>
                            </div>

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
                                        <span>Analyze Content</span>
                                    )}
                                </button>
                            </div>

                            {wordCount > 0 && wordCount < 100 && (
                                <div className="warning-message">
                                    <span>⚠</span>
                                    <span>Please add at least {100 - wordCount} more word{100 - wordCount !== 1 ? 's' : ''} for accurate analysis.</span>
                                </div>
                            )}
                        </>
                    )}

                    {/* File Upload Mode */}
                    {inputMode === 'file' && (
                        <>
                            <div className="file-upload-area">
                                {!selectedFile ? (
                                    <div
                                        className="file-drop-zone"
                                        onDrop={handleFileDrop}
                                        onDragOver={handleDragOver}
                                    >
                                        <div className="file-drop-icon">↑</div>
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
                                        <p className="file-info">Supported formats: PDF, DOCX</p>
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
                                                ✕
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {selectedFile && (
                                <div className="controls">
                                    <div className="file-ready-indicator">
                                        <span>✔</span>
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
                                            <span>Analyze Content</span>
                                        )}
                                    </button>
                                </div>
                            )}
                        </>
                    )}

                    {/* Error Message */}
                    {error && (
                        <div className="error-message">
                            <span>×</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Results Section */}
                    {result && (
                        <div className="result-section">
                            <div className="result-header">
                                <h2>Analysis Results</h2>
                                <div className={`result-label ${result.is_ai ? 'ai-text' : 'human-text'}`}>
                                    <span>{result.label}</span>
                                </div>
                            </div>

                            {/* Mode Indicator */}
                            <div className="mode-indicator">
                                <span className={`mode-badge ${result.mode === 'hybrid' ? 'hybrid' : 'ml'}`}>
                                    {result.mode === 'hybrid' ? '🤖 Hybrid ML+DL' : '🔬 Pure ML'}
                                </span>
                            </div>

                            {/* File Info */}
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

                            {/* Model Breakdown */}
                            {result.breakdown && (
                                <div className="model-breakdown">
                                    <h3>Model Breakdown</h3>
                                    <div className="breakdown-grid">
                                        {result.mode === 'hybrid' && result.breakdown.roberta_prob !== undefined && (
                                            <>
                                                <div className="breakdown-item">
                                                    <span className="breakdown-label">🤖 RoBERTa</span>
                                                    <span className="breakdown-value">{(result.breakdown.roberta_prob * 100).toFixed(1)}%</span>
                                                </div>
                                                <div className="breakdown-item">
                                                    <span className="breakdown-label">🔬 ML Ensemble</span>
                                                    <span className="breakdown-value">{(result.breakdown.ml_prob * 100).toFixed(1)}%</span>
                                                </div>
                                            </>
                                        )}
                                        {result.mode !== 'hybrid' && (
                                            <>
                                                {result.breakdown.SVM !== undefined && (
                                                    <div className="breakdown-item">
                                                        <span className="breakdown-label">SVM</span>
                                                        <span className="breakdown-value">{(result.breakdown.SVM * 100).toFixed(1)}%</span>
                                                    </div>
                                                )}
                                                {result.breakdown.AdaBoost !== undefined && (
                                                    <div className="breakdown-item">
                                                        <span className="breakdown-label">AdaBoost</span>
                                                        <span className="breakdown-value">{(result.breakdown.AdaBoost * 100).toFixed(1)}%</span>
                                                    </div>
                                                )}
                                                {result.breakdown.RandomForest !== undefined && (
                                                    <div className="breakdown-item">
                                                        <span className="breakdown-label">Random Forest</span>
                                                        <span className="breakdown-value">{(result.breakdown.RandomForest * 100).toFixed(1)}%</span>
                                                    </div>
                                                )}
                                            </>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Highlighted Text */}
                            {highlightedText && result.ai_probability > 0.3 && (
                                <div className="highlighted-text-section">
                                    <div className="highlighted-text-header">
                                        <span>ⓘ</span>
                                        <span>AI-Suspected Sentences Highlighted</span>
                                    </div>
                                    <div
                                        className="highlighted-text-content"
                                        dangerouslySetInnerHTML={{ __html: highlightedText }}
                                    />
                                    <div className="highlighted-text-legend">
                                        <span className="legend-item">
                                            <span className="legend-color ai-sentence-demo"></span>
                                            <span>Sentences with AI-like patterns</span>
                                        </span>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </>
    )
}

export default App
