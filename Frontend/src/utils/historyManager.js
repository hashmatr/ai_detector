/**
 * Local Storage Manager for Analysis History
 */

const STORAGE_KEYS = {
    HISTORY: 'ai_detector_history',
    USER_PREFERENCES: 'ai_detector_preferences',
    THEME: 'theme'
};

const MAX_HISTORY_ITEMS = 100;

/**
 * Save analysis to history
 * @param {Object} analysis - Analysis data to save
 */
export const saveToHistory = (analysis) => {
    try {
        const history = getHistory();

        const historyItem = {
            id: generateId(),
            timestamp: new Date().toISOString(),
            type: analysis.type || 'text', // 'text' or 'file'
            fileName: analysis.fileName || null,
            text: analysis.type === 'text' ? analysis.text?.substring(0, 500) : null, // Save first 500 chars
            result: {
                label: analysis.result.label,
                is_ai: analysis.result.is_ai,
                ai_probability: analysis.result.ai_probability,
                human_probability: analysis.result.human_probability,
                word_count: analysis.result.word_count
            }
        };

        // Add to beginning of array
        history.unshift(historyItem);

        // Keep only MAX_HISTORY_ITEMS
        const trimmedHistory = history.slice(0, MAX_HISTORY_ITEMS);

        localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(trimmedHistory));

        return historyItem;
    } catch (error) {
        console.error('Error saving to history:', error);
        return null;
    }
};

/**
 * Get all history items
 * @returns {Array} History items
 */
export const getHistory = () => {
    try {
        const historyJson = localStorage.getItem(STORAGE_KEYS.HISTORY);
        return historyJson ? JSON.parse(historyJson) : [];
    } catch (error) {
        console.error('Error reading history:', error);
        return [];
    }
};

/**
 * Get history item by ID
 * @param {string} id - History item ID
 * @returns {Object|null} History item
 */
export const getHistoryItem = (id) => {
    const history = getHistory();
    return history.find(item => item.id === id) || null;
};

/**
 * Delete history item
 * @param {string} id - History item ID
 */
export const deleteHistoryItem = (id) => {
    try {
        const history = getHistory();
        const filtered = history.filter(item => item.id !== id);
        localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(filtered));
        return true;
    } catch (error) {
        console.error('Error deleting history item:', error);
        return false;
    }
};

/**
 * Clear all history
 */
export const clearHistory = () => {
    try {
        localStorage.removeItem(STORAGE_KEYS.HISTORY);
        return true;
    } catch (error) {
        console.error('Error clearing history:', error);
        return false;
    }
};

/**
 * Get history statistics
 * @returns {Object} Statistics
 */
export const getHistoryStats = () => {
    const history = getHistory();

    const totalAnalyses = history.length;
    const aiDetected = history.filter(item => item.result.is_ai).length;
    const humanDetected = history.filter(item => !item.result.is_ai).length;
    const textAnalyses = history.filter(item => item.type === 'text').length;
    const fileAnalyses = history.filter(item => item.type === 'file').length;

    const avgAiProbability = history.length > 0
        ? history.reduce((sum, item) => sum + item.result.ai_probability, 0) / history.length
        : 0;

    return {
        totalAnalyses,
        aiDetected,
        humanDetected,
        textAnalyses,
        fileAnalyses,
        avgAiProbability,
        aiPercentage: totalAnalyses > 0 ? (aiDetected / totalAnalyses) * 100 : 0,
        humanPercentage: totalAnalyses > 0 ? (humanDetected / totalAnalyses) * 100 : 0
    };
};

/**
 * Search history
 * @param {string} query - Search query
 * @returns {Array} Matching history items
 */
export const searchHistory = (query) => {
    const history = getHistory();
    const lowerQuery = query.toLowerCase();

    return history.filter(item => {
        const fileName = item.fileName?.toLowerCase() || '';
        const text = item.text?.toLowerCase() || '';
        const label = item.result.label.toLowerCase();

        return fileName.includes(lowerQuery) ||
            text.includes(lowerQuery) ||
            label.includes(lowerQuery);
    });
};

/**
 * Filter history by criteria
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered history items
 */
export const filterHistory = (filters) => {
    let history = getHistory();

    if (filters.type) {
        history = history.filter(item => item.type === filters.type);
    }

    if (filters.classification) {
        const isAi = filters.classification === 'ai';
        history = history.filter(item => item.result.is_ai === isAi);
    }

    if (filters.dateFrom) {
        history = history.filter(item => new Date(item.timestamp) >= new Date(filters.dateFrom));
    }

    if (filters.dateTo) {
        history = history.filter(item => new Date(item.timestamp) <= new Date(filters.dateTo));
    }

    if (filters.minProbability !== undefined) {
        history = history.filter(item => item.result.ai_probability >= filters.minProbability);
    }

    return history;
};

/**
 * Export history to JSON
 */
export const exportHistoryToJSON = () => {
    const history = getHistory();
    const dataStr = JSON.stringify(history, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `ai_detector_history_${new Date().getTime()}.json`;
    link.click();

    URL.revokeObjectURL(url);
};

/**
 * Import history from JSON
 * @param {File} file - JSON file to import
 */
export const importHistoryFromJSON = async (file) => {
    try {
        const text = await file.text();
        const importedHistory = JSON.parse(text);

        if (!Array.isArray(importedHistory)) {
            throw new Error('Invalid history format');
        }

        const currentHistory = getHistory();
        const mergedHistory = [...importedHistory, ...currentHistory];

        // Remove duplicates based on timestamp and keep only MAX_HISTORY_ITEMS
        const uniqueHistory = mergedHistory
            .filter((item, index, self) =>
                index === self.findIndex(t => t.timestamp === item.timestamp)
            )
            .slice(0, MAX_HISTORY_ITEMS);

        localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(uniqueHistory));

        return { success: true, imported: importedHistory.length };
    } catch (error) {
        console.error('Error importing history:', error);
        return { success: false, error: error.message };
    }
};

/**
 * Save user preferences
 * @param {Object} preferences - User preferences
 */
export const savePreferences = (preferences) => {
    try {
        localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(preferences));
        return true;
    } catch (error) {
        console.error('Error saving preferences:', error);
        return false;
    }
};

/**
 * Get user preferences
 * @returns {Object} User preferences
 */
export const getPreferences = () => {
    try {
        const prefsJson = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
        return prefsJson ? JSON.parse(prefsJson) : {
            theme: 'dark',
            defaultMode: 'text',
            autoSaveHistory: true,
            showHighlighting: true,
            exportFormat: 'pdf'
        };
    } catch (error) {
        console.error('Error reading preferences:', error);
        return {};
    }
};

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
const generateId = () => {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
