import axios from 'axios';
import config from '../config';

/**
 * Process multiple files in batch
 * @param {File[]} files - Array of files to process
 * @param {Function} onProgress - Progress callback
 * @param {Function} onComplete - Completion callback
 * @param {Function} onError - Error callback
 */
export const processBatchFiles = async (files, onProgress, onComplete, onError) => {
    const results = [];
    const errors = [];
    let processed = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];

        try {
            // Update progress
            onProgress({
                current: i + 1,
                total: files.length,
                fileName: file.name,
                status: 'processing'
            });

            // Process file
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(`${config.API_BASE_URL}/predict-file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            results.push({
                file: file.name,
                size: file.size,
                result: response.data,
                status: 'success',
                timestamp: new Date().toISOString()
            });

            processed++;

            // Update progress
            onProgress({
                current: i + 1,
                total: files.length,
                fileName: file.name,
                status: 'completed',
                processed,
                errors: errors.length
            });

        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);

            errors.push({
                file: file.name,
                error: error.response?.data?.error || error.message,
                timestamp: new Date().toISOString()
            });

            // Update progress with error
            onProgress({
                current: i + 1,
                total: files.length,
                fileName: file.name,
                status: 'error',
                processed,
                errors: errors.length
            });
        }

        // Small delay to prevent overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Call completion callback
    onComplete({
        results,
        errors,
        total: files.length,
        successful: results.length,
        failed: errors.length,
        timestamp: new Date().toISOString()
    });
};

/**
 * Export batch results to CSV
 * @param {Array} results - Batch processing results
 */
export const exportBatchResultsToCSV = (results) => {
    const headers = ['File Name', 'File Size (KB)', 'Classification', 'AI Probability', 'Human Probability', 'Word Count', 'Timestamp'];

    const rows = results.map(item => [
        item.file,
        (item.size / 1024).toFixed(2),
        item.result.label,
        (item.result.ai_probability * 100).toFixed(1) + '%',
        (item.result.human_probability * 100).toFixed(1) + '%',
        item.result.word_count || 'N/A',
        new Date(item.timestamp).toLocaleString()
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `batch_analysis_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

/**
 * Validate files for batch processing
 * @param {FileList} fileList - Files to validate
 * @returns {Object} Validation result
 */
export const validateBatchFiles = (fileList) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
    const validExtensions = ['.pdf', '.docx', '.doc'];
    const maxFileSize = 10 * 1024 * 1024; // 10MB
    const maxFiles = 20; // Maximum 20 files at once

    const files = Array.from(fileList);
    const validFiles = [];
    const invalidFiles = [];

    if (files.length > maxFiles) {
        return {
            valid: false,
            error: `Maximum ${maxFiles} files allowed. You selected ${files.length} files.`,
            validFiles: [],
            invalidFiles: files
        };
    }

    files.forEach(file => {
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        const isValidType = validTypes.includes(file.type) || validExtensions.includes(fileExtension);
        const isValidSize = file.size <= maxFileSize;

        if (isValidType && isValidSize) {
            validFiles.push(file);
        } else {
            invalidFiles.push({
                file: file.name,
                reason: !isValidType ? 'Invalid file type' : 'File too large (max 10MB)'
            });
        }
    });

    return {
        valid: validFiles.length > 0,
        validFiles,
        invalidFiles,
        totalValid: validFiles.length,
        totalInvalid: invalidFiles.length
    };
};
