import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, FileText, CheckCircle, Upload, X } from 'lucide-react';
import { EvaluationRequest } from '../types/evaluation';

interface EvaluationFormProps {
  onSubmit: (request: EvaluationRequest) => void;
  isLoading: boolean;
}

const EvaluationForm: React.FC<EvaluationFormProps> = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState<EvaluationRequest>({
    model: ['gpt-4o-mini'],
    eval_metrices: ['Accuracy', 'Hallucination', 'Authoritativeness', 'Usefulness'],
    user_query: '',
    ai_response: '',
    chunk_1: '',
    chunk_2: '',
    chunk_3: '',
    chunk_4: '',
    chunk_5: '',
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [csvRecords, setCsvRecords] = useState<any[]>([]);
  const [selectedRecordIndex, setSelectedRecordIndex] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const metrics = [
    { id: 'Accuracy', label: 'Accuracy', description: 'Factual correctness and absence of errors' },
    { id: 'Hallucination', label: 'Hallucination', description: 'Detection of fabricated information' },
    { id: 'Authoritativeness', label: 'Authoritativeness', description: 'Quality and relevance of citations' },
    { id: 'Usefulness', label: 'Usefulness', description: 'Overall quality and practical value' },
  ];

  const handleInputChange = (field: keyof EvaluationRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleMetricToggle = (metric: string) => {
    const currentMetrics = formData.eval_metrices;
    const newMetrics = currentMetrics.includes(metric as any)
      ? currentMetrics.filter(m => m !== metric)
      : [...currentMetrics, metric as any];
    
    handleInputChange('eval_metrices', newMetrics);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['text/plain', 'application/pdf', 'text/csv', 'application/json'];
    if (!allowedTypes.includes(file.type)) {
      setErrors(prev => ({ ...prev, file: 'Please upload a valid file (TXT, PDF, CSV, or JSON)' }));
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setErrors(prev => ({ ...prev, file: 'File size must be less than 10MB' }));
      return;
    }

    setIsUploading(true);
    setUploadedFile(file);
    setErrors(prev => ({ ...prev, file: '' }));

    try {
      // Extract text content from file
      const content = await extractFileContent(file);
      
      // Parse CSV content and populate appropriate fields
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        parseCSVContent(content);
      } else {
        // For non-CSV files, populate AI Response field with the file content
        handleInputChange('ai_response', content);
        
        // If user query is empty, suggest a default
        if (!formData.user_query.trim()) {
          handleInputChange('user_query', `Please evaluate the content from ${file.name}`);
        }
      }
    } catch (error) {
      console.error('Error processing file:', error);
      setErrors(prev => ({ ...prev, file: 'Error processing file. Please try again.' }));
      setUploadedFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  const parseCSVContent = (content: string) => {
    try {
      const lines = content.trim().split('\n');
      if (lines.length < 2) {
        throw new Error('CSV must have at least a header row and one data row');
      }

      // Parse CSV with proper handling of quoted fields
      const parseCSVRow = (row: string): string[] => {
        const result: string[] = [];
        let current = '';
        let inQuotes = false;
        let i = 0;
        
        while (i < row.length) {
          const char = row[i];
          
          if (char === '"') {
            if (inQuotes && row[i + 1] === '"') {
              // Escaped quote
              current += '"';
              i += 2;
            } else {
              // Toggle quote state
              inQuotes = !inQuotes;
              i++;
            }
          } else if (char === ',' && !inQuotes) {
            // End of field
            result.push(current.trim());
            current = '';
            i++;
          } else {
            current += char;
            i++;
          }
        }
        
        // Add the last field
        result.push(current.trim());
        return result;
      };

      // Parse header row
      const headers = parseCSVRow(lines[0]);
      
      // Parse all data rows
      const dataRows = lines.slice(1).map(line => parseCSVRow(line));
      
      console.log('CSV Headers:', headers);
      console.log('CSV Data Rows:', dataRows);
      
      // Map CSV columns to form fields
      const fieldMapping: { [key: string]: string } = {
        'user_query': 'user_query',
        'ai_response': 'ai_response',
        'chunk_1': 'chunk_1',
        'chunk_2': 'chunk_2',
        'chunk_3': 'chunk_3',
        'chunk_4': 'chunk_4',
        'chunk_5': 'chunk_5'
      };

      // Convert data rows to objects with field mappings
      const records = dataRows.map(row => {
        const record: any = {};
        headers.forEach((header, index) => {
          const fieldName = fieldMapping[header];
          if (fieldName && row[index]) {
            record[fieldName] = row[index];
          }
        });
        return record;
      });

      // Store all records
      setCsvRecords(records);
      setSelectedRecordIndex(0);

      // Populate form with first record
      populateFormWithRecord(records[0]);

    } catch (error) {
      console.error('Error parsing CSV:', error);
      // Fallback: put content in AI Response field
      handleInputChange('ai_response', content);
      if (!formData.user_query.trim()) {
        handleInputChange('user_query', 'Please evaluate the content from the uploaded file');
      }
    }
  };

  const populateFormWithRecord = (record: any) => {
    // Track if user_query was found in record
    let userQueryFound = false;

    // Populate form fields based on record data
    Object.keys(record).forEach(fieldName => {
      if (record[fieldName]) {
        console.log(`Setting ${fieldName} to:`, record[fieldName]);
        handleInputChange(fieldName as keyof EvaluationRequest, record[fieldName]);
        
        // Track if user_query was populated
        if (fieldName === 'user_query') {
          userQueryFound = true;
        }
      }
    });

    // If no user_query was found in record, set a default
    if (!userQueryFound) {
      handleInputChange('user_query', 'Please evaluate the AI response');
    }
  };

  const handleRecordSelection = (index: number) => {
    setSelectedRecordIndex(index);
    if (csvRecords[index]) {
      populateFormWithRecord(csvRecords[index]);
    }
  };

  const extractFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        const content = e.target?.result as string;
        resolve(content);
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };
      
      if (file.type === 'text/plain' || file.type === 'text/csv' || file.type === 'application/json') {
        reader.readAsText(file);
      } else if (file.type === 'application/pdf') {
        // For PDF files, we'll need a PDF parser library
        // For now, we'll show an error message
        reject(new Error('PDF parsing not yet implemented. Please use a text file.'));
      } else {
        reader.readAsText(file);
      }
    });
  };

  const removeUploadedFile = () => {
    setUploadedFile(null);
    setCsvRecords([]);
    setSelectedRecordIndex(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    setErrors(prev => ({ ...prev, file: '' }));
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.user_query.trim()) {
      newErrors.user_query = 'User query is required';
    }

    if (!formData.ai_response.trim()) {
      newErrors.ai_response = 'AI response is required';
    }

    if (formData.eval_metrices.length === 0) {
      newErrors.eval_metrices = 'At least one metric must be selected';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      // Include uploaded file data if available
      const requestData: EvaluationRequest = {
        ...formData,
        uploaded_file: uploadedFile ? {
          name: uploadedFile.name,
          content: formData.ai_response, // The content is already in ai_response
          type: uploadedFile.type,
          size: uploadedFile.size
        } : undefined
      };
      onSubmit(requestData);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      className="card max-w-4xl mx-auto"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="flex items-center space-x-3 mb-6">
        <div className="flex items-center justify-center w-10 h-10 bg-nvidia-green rounded-lg">
          <FileText className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-100">Evaluation Request</h2>
          <p className="text-gray-400">Submit your AI response for multi-agent evaluation</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Metrics Selection */}
        <motion.div variants={itemVariants}>
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Select Evaluation Metrics
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {metrics.map((metric) => (
              <motion.div
                key={metric.id}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                  formData.eval_metrices.includes(metric.id as any)
                    ? 'border-nvidia-green bg-nvidia-green/10'
                    : 'border-gray-700 bg-dark-tertiary hover:border-gray-600'
                }`}
                onClick={() => handleMetricToggle(metric.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                    formData.eval_metrices.includes(metric.id as any)
                      ? 'border-nvidia-green bg-nvidia-green'
                      : 'border-gray-500'
                  }`}>
                    {formData.eval_metrices.includes(metric.id as any) && (
                      <CheckCircle className="w-3 h-3 text-white" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-gray-100">{metric.label}</div>
                    <div className="text-sm text-gray-400">{metric.description}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
          {errors.eval_metrices && (
            <p className="text-red-400 text-sm mt-2">{errors.eval_metrices}</p>
          )}
        </motion.div>

        {/* File Upload Section */}
        <motion.div variants={itemVariants}>
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Upload File (Optional)
          </label>
          <div className="space-y-3">
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf,.csv,.json"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            {/* Upload button */}
            <motion.button
              type="button"
              onClick={triggerFileUpload}
              disabled={isUploading}
              className="w-full p-4 border-2 border-dashed border-gray-600 rounded-lg bg-dark-tertiary hover:border-nvidia-green hover:bg-nvidia-green/5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
            >
              <div className="flex flex-col items-center space-y-2">
                {isUploading ? (
                  <>
                    <div className="w-8 h-8 border-2 border-nvidia-green border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-300">Processing file...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-8 h-8 text-gray-400" />
                    <div className="text-center">
                      <span className="text-gray-300 font-medium">Click to upload a file</span>
                      <p className="text-sm text-gray-500 mt-1">
                        Supports TXT, PDF, CSV, and JSON files (max 10MB)
                      </p>
                    </div>
                  </>
                )}
              </div>
            </motion.button>

            {/* Uploaded file display */}
            {uploadedFile && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 bg-nvidia-green/10 border border-nvidia-green/30 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-nvidia-green" />
                    <div>
                      <p className="text-sm font-medium text-gray-200">{uploadedFile.name}</p>
                      <p className="text-xs text-gray-400">
                        {(uploadedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={removeUploadedFile}
                    className="p-1 hover:bg-red-500/20 rounded transition-colors"
                  >
                    <X className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              </motion.div>
            )}

            {/* Record Selection for CSV files with multiple records */}
            {csvRecords.length > 1 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg"
              >
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Select Record to Evaluate ({csvRecords.length} records found)
                </label>
                <select
                  value={selectedRecordIndex}
                  onChange={(e) => handleRecordSelection(parseInt(e.target.value))}
                  className="w-full p-2 bg-dark-tertiary border border-gray-600 rounded-lg text-gray-100 focus:border-nvidia-green focus:outline-none"
                >
                  {csvRecords.map((record, index) => (
                    <option key={index} value={index}>
                      Record {index + 1}
                      {record.user_query ? ` - ${record.user_query.substring(0, 50)}${record.user_query.length > 50 ? '...' : ''}` : ''}
                    </option>
                  ))}
                </select>
              </motion.div>
            )}

            {/* File upload error */}
            {errors.file && (
              <p className="text-red-400 text-sm">{errors.file}</p>
            )}
          </div>
        </motion.div>

        {/* User Query */}
        <motion.div variants={itemVariants}>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            User Query
          </label>
          <textarea
            className={`input-field w-full h-24 resize-none ${errors.user_query ? 'border-red-500' : ''}`}
            placeholder="Enter the original user query..."
            value={formData.user_query}
            onChange={(e) => handleInputChange('user_query', e.target.value)}
          />
          {errors.user_query && (
            <p className="text-red-400 text-sm mt-1">{errors.user_query}</p>
          )}
        </motion.div>

        {/* AI Response */}
        <motion.div variants={itemVariants}>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            AI Response
          </label>
          <textarea
            className={`input-field w-full h-32 resize-none ${errors.ai_response ? 'border-red-500' : ''}`}
            placeholder="Enter the AI-generated response to evaluate..."
            value={formData.ai_response}
            onChange={(e) => handleInputChange('ai_response', e.target.value)}
          />
          {errors.ai_response && (
            <p className="text-red-400 text-sm mt-1">{errors.ai_response}</p>
          )}
        </motion.div>

        {/* Context Chunks */}
        <motion.div variants={itemVariants}>
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Context Chunks (Optional)
          </label>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((num) => (
              <div key={num}>
                <label className="block text-xs text-gray-400 mb-1">
                  Chunk {num}
                </label>
                <textarea
                  className="input-field w-full h-20 resize-none text-sm"
                  placeholder={`Context chunk ${num}...`}
                  value={formData[`chunk_${num}` as keyof EvaluationRequest] as string}
                  onChange={(e) => handleInputChange(`chunk_${num}` as keyof EvaluationRequest, e.target.value)}
                />
              </div>
            ))}
          </div>
        </motion.div>

        {/* Submit Button */}
        <motion.div variants={itemVariants} className="pt-4">
          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Evaluating...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Start Evaluation</span>
              </>
            )}
          </button>
        </motion.div>
      </form>
    </motion.div>
  );
};

export default EvaluationForm;
