import React, { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import { Toaster, toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { UploadCloud, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const SummarizePage: React.FC = () => {
  const [inputText, setInputText] = useState<string>('');
  const [displayedText, setDisplayedText] = useState<string>('');
  const [fileName, setFileName] = useState<string | null>(null);
  const [summaryOutput, setSummaryOutput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [isDragOver, setIsDragOver] = useState<boolean>(false); 

  const outputRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_KEY = import.meta.env.VITE_API_KEY;
  const TRUNCATION_LENGTH = 1000;

  // --- Core File Processing Logic  ---
  const processFile = (file: File | null) => {
    if (!file) {
      setFileName(null);
      setInputText('');
      setDisplayedText('');
      return;
    }

    // Check file type 
    const allowedTypes = ['text/plain', 'application/json', 'text/markdown'];
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.md')) { 
        toast.error("Unsupported file type. Please upload a .txt, .json, or .md file.");
        setFileName(null);
        setInputText('');
        setDisplayedText('');
        return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      toast.error("File is too large (max 5MB).");
      setFileName(null);
      setInputText('');
      setDisplayedText('');
      return;
    }

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      const textContent = e.target?.result as string;
      setInputText(textContent);
      setDisplayedText(
        textContent.length > TRUNCATION_LENGTH
          ? textContent.substring(0, TRUNCATION_LENGTH) + '\n\n... [Full transcription loaded, showing first ' + TRUNCATION_LENGTH + ' characters] ...'
          : textContent
      );
      toast.success(`File "${file.name}" loaded successfully.`);
    };
    reader.onerror = () => {
      toast.error("Failed to read file.");
      setFileName(null);
      setInputText('');
      setDisplayedText('');
    };
    reader.readAsText(file);
  };

  // --- Event Handlers for File Input ---
  const handleFileInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    processFile(event.target.files?.[0] || null);
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const fullText = e.target.value;
    setInputText(fullText);
    setDisplayedText(
      fullText.length > TRUNCATION_LENGTH
        ? fullText.substring(0, TRUNCATION_LENGTH) + '\n\n... [Full text, showing first ' + TRUNCATION_LENGTH + ' characters] ...'
        : fullText
    );
  };

  // --- Event Handlers for Drag and Drop ---
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); 
    e.stopPropagation(); 
    setIsDragOver(true); // Add visual cue
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false); // Remove visual cue
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); 
    e.stopPropagation(); 
    setIsDragOver(false); // Remove visual cue

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]); // Process the first dropped file
      e.dataTransfer.clearData(); // Clear data to prevent re-processing on subsequent drops
    }
  };

  // --- Summarization Logic ---
  const handleSummarize = async () => {
    if (!inputText.trim()) {
      toast.error("Please provide text or upload a file for summarization.");
      return;
    }

    setLoading(true);
    setSummaryOutput('');

    try {
      const response = await fetch("http://localhost:8000/summaries/generate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail ? JSON.stringify(errorData.detail) : "Summarization failed for an unknown reason.");
      }

      const result = await response.json();
      setSummaryOutput(result.summary);
      toast.success("Summary generated successfully!");

    } catch (error: any) {
      console.error("Summarization error:", error);
      toast.error(`Summarization error: ${error.message || "Please check console for details."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center w-full min-h-[calc(100vh-theme(spacing.24))] py-8 px-4 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Summarize Transcriptions</h1>

      {/* Main Container for Input and Output Cards*/}
      <div className="flex flex-col gap-8 w-full">

        {/* --- Input Section Card --- */}
        <Card className="flex-1 min-w-[300px]">
          <CardHeader>
            <CardTitle>Input Transcription</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Custom File Input Area with Drag & Drop Handlers */}
            <div
              className={`flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors duration-200 ${
                isDragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => fileInputRef.current?.click()} 
              onDragOver={handleDragOver}  
              onDragLeave={handleDragLeave} 
              onDrop={handleDrop}           
            >
              <UploadCloud className="w-12 h-12 text-gray-400 mb-3" />
              <p className="text-sm text-gray-600 mb-1">
                Drag and drop a file here, or click to browse
              </p>
              <p className="text-xs text-gray-500">
                Supported formats: TXT, JSON, MD (Max 5MB)
              </p>
              {fileName && (
                <div className="mt-2 flex items-center text-sm text-primary-600 font-medium">
                  <FileText className="w-4 h-4 mr-1" /> {fileName}
                </div>
              )}
              {/* Hidden native file input element */}
              <input
                id="transcription-file-hidden"
                type="file"
                ref={fileInputRef}
                accept=".txt,.json,.md"
                onChange={handleFileInputChange} 
                className="hidden"
              />
            </div>

            <div className="my-4 text-center text-gray-500">
              OR
            </div>

            {/* Textarea for Direct Input / Truncated Display */}
            <label htmlFor="transcription-text" className="block text-sm font-medium text-gray-700 mb-2">
              Paste Transcription Text
            </label>
            <Textarea
              id="transcription-text"
              placeholder="Paste your conversation transcription here..."
              value={displayedText}
              onChange={handleTextareaChange}
              rows={15}
              className="w-full resize-y min-h-[200px]"
            />

            {/* Summarize Button */}
            <Button onClick={handleSummarize} disabled={loading} className="mt-4 w-full">
              {loading ? "Summarizing..." : "Summarize"}
            </Button>
          </CardContent>
        </Card>

        {/* --- Output Section Card --- */}
        <Card className="flex-1 min-w-[300px]">
          <CardHeader>
            <CardTitle>Templated Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              className="w-full p-4 border rounded-md min-h-[500px] max-h-[1000px] overflow-y-auto focus:outline-none focus:ring-2 focus:ring-primary-500 resize-y text-left"
            >
              {summaryOutput ? (
                <ReactMarkdown>{summaryOutput}</ReactMarkdown>
              ) : (
                <p className='text-gray-500'>Your generated summary will appear here.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Toaster />
    </div>
  );
};

export default SummarizePage;





