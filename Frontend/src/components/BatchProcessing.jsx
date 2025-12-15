import React, { useState, useRef } from 'react';
import { processBatchFiles, validateBatchFiles, exportBatchResultsToCSV } from '../utils/batchProcessing';

const BatchProcessing = () => {
    const [files, setFiles] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [progress, setProgress] = useState(null);
    const [results, setResults] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const selectedFiles = e.target.files;
        if (selectedFiles.length > 0) {
            const validation = validateBatchFiles(selectedFiles);

            if (!validation.valid && validation.error) {
                alert(validation.error);
                return;
            }

            if (validation.invalidFiles.length > 0) {
                const invalidList = validation.invalidFiles
                    .map(f => `${f.file}: ${f.reason}`)
                    .join('\n');
                alert(`Some files were excluded:\n\n${invalidList}`);
            }

            setFiles(validation.validFiles);
            setResults(null);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();

        const droppedFiles = e.dataTransfer.files;
        if (droppedFiles.length > 0) {
            const validation = validateBatchFiles(droppedFiles);

            if (!validation.valid && validation.error) {
                alert(validation.error);
                return;
            }

            if (validation.invalidFiles.length > 0) {
                const invalidList = validation.invalidFiles
                    .map(f => `${f.file}: ${f.reason}`)
                    .join('\n');
                alert(`Some files were excluded:\n\n${invalidList}`);
            }

            setFiles(validation.validFiles);
            setResults(null);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleProcess = async () => {
        if (files.length === 0) return;

        setProcessing(true);
        setProgress({ current: 0, total: files.length, status: 'starting' });
        setResults(null);

        await processBatchFiles(
            files,
            // Progress callback
            (progressData) => {
                setProgress(progressData);
            },
            // Complete callback
            (completionData) => {
                setProcessing(false);
                setResults(completionData);
                setProgress(null);
            },
            // Error callback
            (error) => {
                console.error('Batch processing error:', error);
                setProcessing(false);
            }
        );
    };

    const handleClear = () => {
        setFiles([]);
        setResults(null);
        setProgress(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleExportCSV = () => {
        if (results && results.results.length > 0) {
            exportBatchResultsToCSV(results.results);
        }
    };

    const removeFile = (index) => {
        const newFiles = files.filter((_, i) => i !== index);
        setFiles(newFiles);
    };

    return (
        <div className="batch-container">
            {/* Header */}
            <div className="batch-header">
                <h2 className="batch-title">Batch File Processing</h2>
                <p className="batch-subtitle">
                    Process multiple documents at once (up to 20 files)
                </p>
            </div>

            {/* File Upload Area */}
            {!processing && !results && (
                <div
                    className="batch-drop-zone"
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                >
                    <div className="batch-drop-icon">↑</div>
                    <h3>Drop multiple files here</h3>
                    <p>or</p>
                    <label className="batch-select-btn">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.docx,.doc"
                            multiple
                            onChange={handleFileSelect}
                            style={{ display: 'none' }}
                        />
                        Choose Files
                    </label>
                    <p className="batch-info">
                        Supported: PDF, DOCX, DOC • Max 10MB per file • Up to 20 files
                    </p>
                </div>
            )}

            {/* Selected Files List */}
            {files.length > 0 && !processing && !results && (
                <div className="batch-files-section">
                    <div className="batch-files-header">
                        <h3>Selected Files ({files.length})</h3>
                        <button onClick={handleClear} className="btn-secondary">
                            Clear All
                        </button>
                    </div>
                    <div className="batch-files-list">
                        {files.map((file, index) => (
                            <div key={index} className="batch-file-item">
                                <div className="batch-file-icon">
                                    {file.name.endsWith('.pdf') ? '📕' : '📘'}
                                </div>
                                <div className="batch-file-details">
                                    <div className="batch-file-name">{file.name}</div>
                                    <div className="batch-file-size">
                                        {(file.size / 1024).toFixed(2)} KB
                                    </div>
                                </div>
                                <button
                                    onClick={() => removeFile(index)}
                                    className="batch-file-remove"
                                    aria-label="Remove file"
                                >
                                    ✕
                                </button>
                            </div>
                        ))}
                    </div>
                    <div className="batch-actions">
                        <button
                            onClick={handleProcess}
                            className="btn-primary batch-process-btn"
                        >
                            Process All Files
                        </button>
                    </div>
                </div>
            )}

            {/* Progress Display */}
            {processing && progress && (
                <div className="batch-progress-section">
                    <h3>Processing Files...</h3>
                    <div className="progress-bar-container">
                        <div
                            className="progress-bar"
                            style={{ width: `${(progress.current / progress.total) * 100}%` }}
                        />
                    </div>
                    <div className="progress-info">
                        <span>
                            {progress.current} of {progress.total} files processed
                        </span>
                        {progress.fileName && (
                            <span className="current-file">
                                Current: {progress.fileName}
                            </span>
                        )}
                    </div>
                    {progress.processed !== undefined && (
                        <div className="progress-stats">
                            <span className="success-count">
                                ✓ {progress.processed} successful
                            </span>
                            {progress.errors > 0 && (
                                <span className="error-count">
                                    ✗ {progress.errors} failed
                                </span>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Results Display */}
            {results && (
                <div className="batch-results-section">
                    <div className="batch-results-header">
                        <h3>Batch Processing Complete</h3>
                        <div className="batch-results-actions">
                            <button onClick={handleExportCSV} className="btn-primary">
                                Export to CSV
                            </button>
                            <button onClick={handleClear} className="btn-secondary">
                                Process More Files
                            </button>
                        </div>
                    </div>

                    {/* Summary Stats */}
                    <div className="batch-summary">
                        <div className="summary-card">
                            <div className="summary-label">Total Files</div>
                            <div className="summary-value">{results.total}</div>
                        </div>
                        <div className="summary-card success">
                            <div className="summary-label">Successful</div>
                            <div className="summary-value">{results.successful}</div>
                        </div>
                        <div className="summary-card error">
                            <div className="summary-label">Failed</div>
                            <div className="summary-value">{results.failed}</div>
                        </div>
                    </div>

                    {/* Results Table */}
                    <div className="batch-results-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>Classification</th>
                                    <th>AI Probability</th>
                                    <th>Human Probability</th>
                                    <th>Words</th>
                                </tr>
                            </thead>
                            <tbody>
                                {results.results.map((item, index) => (
                                    <tr key={index}>
                                        <td className="file-name-cell">{item.file}</td>
                                        <td>
                                            <span className={`result-badge ${item.result.is_ai ? 'ai' : 'human'}`}>
                                                {item.result.is_ai ? '🤖' : '✍️'} {item.result.label}
                                            </span>
                                        </td>
                                        <td className="probability-cell ai">
                                            {(item.result.ai_probability * 100).toFixed(1)}%
                                        </td>
                                        <td className="probability-cell human">
                                            {(item.result.human_probability * 100).toFixed(1)}%
                                        </td>
                                        <td>{item.result.word_count?.toLocaleString() || 'N/A'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Errors List */}
                    {results.errors.length > 0 && (
                        <div className="batch-errors">
                            <h4>Failed Files</h4>
                            <div className="errors-list">
                                {results.errors.map((error, index) => (
                                    <div key={index} className="error-item">
                                        <strong>{error.file}</strong>: {error.error}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default BatchProcessing;
