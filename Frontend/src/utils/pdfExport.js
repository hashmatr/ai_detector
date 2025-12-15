import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

/**
 * Export analysis results as PDF
 * @param {Object} result - Analysis result data
 * @param {string} text - Original text analyzed
 * @param {string} highlightedText - HTML highlighted text
 * @param {string} mode - 'text' or 'file'
 */
export const exportToPDF = async (result, text, highlightedText, mode = 'text') => {
    try {
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 20;
        const contentWidth = pageWidth - 2 * margin;
        let yPosition = margin;

        // Helper function to add text with word wrap
        const addText = (text, fontSize, isBold = false, color = [0, 0, 0]) => {
            pdf.setFontSize(fontSize);
            pdf.setFont('helvetica', isBold ? 'bold' : 'normal');
            pdf.setTextColor(...color);
            const lines = pdf.splitTextToSize(text, contentWidth);

            lines.forEach(line => {
                if (yPosition > pageHeight - margin) {
                    pdf.addPage();
                    yPosition = margin;
                }
                pdf.text(line, margin, yPosition);
                yPosition += fontSize * 0.5;
            });
            yPosition += 5;
        };

        // Header
        addText('AI Content Detector - Analysis Report', 20, true, [90, 99, 255]);
        addText(`Generated: ${new Date().toLocaleString()}`, 10, false, [100, 100, 100]);
        yPosition += 5;

        // Add line separator
        pdf.setDrawColor(200, 200, 200);
        pdf.line(margin, yPosition, pageWidth - margin, yPosition);
        yPosition += 10;

        // File Information (if file mode)
        if (mode === 'file' && result.filename) {
            addText('Document Information', 14, true);
            addText(`File: ${result.filename}`, 11);
            addText(`Type: ${result.file_type}`, 11);
            addText(`Word Count: ${result.word_count?.toLocaleString() || 'N/A'}`, 11);
            yPosition += 5;
        }

        // Analysis Results
        addText('Analysis Results', 14, true);

        // Classification
        const classification = result.is_ai ? 'AI-Generated Content' : 'Human-Written Content';
        const classColor = result.is_ai ? [228, 92, 92] : [60, 203, 127];
        addText(`Classification: ${classification}`, 12, true, classColor);

        // Probabilities
        addText(`AI-Generated Probability: ${(result.ai_probability * 100).toFixed(1)}%`, 11, false, [228, 92, 92]);
        addText(`Human-Written Probability: ${(result.human_probability * 100).toFixed(1)}%`, 11, false, [60, 203, 127]);
        yPosition += 5;

        // Confidence Level
        let confidence = 'Low';
        if (result.ai_probability > 0.7 || result.human_probability > 0.7) confidence = 'High';
        else if (result.ai_probability > 0.5 || result.human_probability > 0.5) confidence = 'Medium';
        addText(`Confidence Level: ${confidence}`, 11, true);
        yPosition += 10;

        // Add line separator
        pdf.line(margin, yPosition, pageWidth - margin, yPosition);
        yPosition += 10;

        // Original Text
        addText('Analyzed Text', 14, true);
        const textToShow = mode === 'file' && result.extracted_text
            ? result.extracted_text.substring(0, 2000) + (result.extracted_text.length > 2000 ? '...' : '')
            : text.substring(0, 2000) + (text.length > 2000 ? '...' : '');

        addText(textToShow, 10);
        yPosition += 10;

        // Analysis Notes
        addText('Analysis Notes', 14, true);
        addText('This analysis is based on linguistic patterns, predictability, and structural indicators.', 10);
        addText('Results should be used as a guide and not as definitive proof.', 10);

        // Footer
        const footerY = pageHeight - 15;
        pdf.setFontSize(8);
        pdf.setTextColor(150, 150, 150);
        pdf.text('AI Content Detector - Professional Analysis Tool', pageWidth / 2, footerY, { align: 'center' });

        // Save PDF
        const fileName = mode === 'file' && result.filename
            ? `${result.filename.split('.')[0]}_analysis.pdf`
            : `ai_analysis_${new Date().getTime()}.pdf`;

        pdf.save(fileName);
        return { success: true, fileName };
    } catch (error) {
        console.error('PDF Export Error:', error);
        return { success: false, error: error.message };
    }
};

/**
 * Export with visual chart (using html2canvas)
 * @param {string} elementId - ID of the element to capture
 * @param {Object} result - Analysis result data
 */
export const exportWithChart = async (elementId, result) => {
    try {
        const element = document.getElementById(elementId);
        if (!element) {
            throw new Error('Element not found');
        }

        const canvas = await html2canvas(element, {
            scale: 2,
            backgroundColor: '#ffffff',
            logging: false,
        });

        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const imgWidth = pageWidth - 40;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        pdf.addImage(imgData, 'PNG', 20, 20, imgWidth, imgHeight);

        const fileName = `ai_analysis_chart_${new Date().getTime()}.pdf`;
        pdf.save(fileName);

        return { success: true, fileName };
    } catch (error) {
        console.error('Chart Export Error:', error);
        return { success: false, error: error.message };
    }
};
