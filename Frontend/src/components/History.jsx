import React, { useState, useEffect } from 'react';
import {
    getHistory,
    deleteHistoryItem,
    clearHistory,
    getHistoryStats,
    searchHistory,
    filterHistory,
    exportHistoryToJSON
} from '../utils/historyManager';

const History = ({ onSelectItem }) => {
    const [history, setHistory] = useState([]);
    const [stats, setStats] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({});
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        loadHistory();
        loadStats();
    }, []);

    const loadHistory = () => {
        const historyData = getHistory();
        setHistory(historyData);
    };

    const loadStats = () => {
        const statsData = getHistoryStats();
        setStats(statsData);
    };

    const handleSearch = (query) => {
        setSearchQuery(query);
        if (query.trim()) {
            const results = searchHistory(query);
            setHistory(results);
        } else {
            loadHistory();
        }
    };

    const handleFilter = (newFilters) => {
        setFilters(newFilters);
        const filtered = filterHistory(newFilters);
        setHistory(filtered);
    };

    const handleDelete = (id) => {
        if (window.confirm('Are you sure you want to delete this item?')) {
            deleteHistoryItem(id);
            loadHistory();
            loadStats();
        }
    };

    const handleClearAll = () => {
        if (window.confirm('Are you sure you want to clear all history? This cannot be undone.')) {
            clearHistory();
            loadHistory();
            loadStats();
        }
    };

    const handleExport = () => {
        exportHistoryToJSON();
    };

    const formatDate = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    return (
        <div className="history-container">
            {/* Header */}
            <div className="history-header">
                <h2 className="history-title">Analysis History</h2>
                <div className="history-actions">
                    <button onClick={handleExport} className="btn-secondary">
                        Export
                    </button>
                    <button onClick={handleClearAll} className="btn-danger">
                        Clear All
                    </button>
                </div>
            </div>

            {/* Statistics */}
            {stats && (
                <div className="history-stats">
                    <div className="stat-card">
                        <div className="stat-label">Total Analyses</div>
                        <div className="stat-value">{stats.totalAnalyses}</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">AI Detected</div>
                        <div className="stat-value" style={{ color: 'var(--error)' }}>
                            {stats.aiDetected}
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Human Written</div>
                        <div className="stat-value" style={{ color: 'var(--success)' }}>
                            {stats.humanDetected}
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Avg AI Probability</div>
                        <div className="stat-value">
                            {(stats.avgAiProbability * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            )}

            {/* Search and Filter */}
            <div className="history-controls">
                <div className="search-box">
                    <span className="search-icon">⌕</span>
                    <input
                        type="text"
                        placeholder="Search history..."
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                        className="search-input"
                    />
                </div>
                <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="btn-secondary"
                >
                    {showFilters ? '× Hide Filters' : 'Filters'}
                </button>
            </div>

            {/* Filter Panel */}
            {showFilters && (
                <div className="filter-panel">
                    <div className="filter-group">
                        <label>Type:</label>
                        <select onChange={(e) => handleFilter({ ...filters, type: e.target.value })}>
                            <option value="">All</option>
                            <option value="text">Text</option>
                            <option value="file">File</option>
                        </select>
                    </div>
                    <div className="filter-group">
                        <label>Classification:</label>
                        <select onChange={(e) => handleFilter({ ...filters, classification: e.target.value })}>
                            <option value="">All</option>
                            <option value="ai">AI-Generated</option>
                            <option value="human">Human-Written</option>
                        </select>
                    </div>
                    <button onClick={() => { setFilters({}); loadHistory(); }} className="btn-secondary">
                        Clear Filters
                    </button>
                </div>
            )}

            {/* History List */}
            <div className="history-list">
                {history.length === 0 ? (
                    <div className="empty-state">
                        <span className="empty-icon"></span>
                        <p>No analysis history yet</p>
                        <p className="empty-subtitle">Your analyses will appear here</p>
                    </div>
                ) : (
                    history.map((item) => (
                        <div key={item.id} className="history-item">
                            <div className="history-item-header">
                                <div className="history-item-info">
                                    <span className="history-type-badge">
                                        {item.type === 'file' ? 'File' : 'Text'} {item.type}
                                    </span>
                                    <span className="history-date">{formatDate(item.timestamp)}</span>
                                </div>
                                <button
                                    onClick={() => handleDelete(item.id)}
                                    className="delete-btn"
                                    aria-label="Delete"
                                >
                                    ✕
                                </button>
                            </div>

                            <div className="history-item-content">
                                {item.fileName && (
                                    <div className="history-filename">
                                        <strong>File:</strong> {item.fileName}
                                    </div>
                                )}
                                {item.text && (
                                    <div className="history-text-preview">
                                        {item.text}...
                                    </div>
                                )}
                            </div>

                            <div className="history-item-result">
                                <div className={`result-badge ${item.result.is_ai ? 'ai' : 'human'}`}>
                                    {item.result.is_ai ? 'AI' : 'Human'} {item.result.label}
                                </div>
                                <div className="probability-display">
                                    <span className="prob-label">AI:</span>
                                    <span className="prob-value" style={{ color: 'var(--error)' }}>
                                        {(item.result.ai_probability * 100).toFixed(1)}%
                                    </span>
                                    <span className="prob-separator">|</span>
                                    <span className="prob-label">Human:</span>
                                    <span className="prob-value" style={{ color: 'var(--success)' }}>
                                        {(item.result.human_probability * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>

                            {onSelectItem && (
                                <button
                                    onClick={() => onSelectItem(item)}
                                    className="view-details-btn"
                                >
                                    View Details →
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default History;
