import React, { useState, useRef } from 'react'; // Keep runtime values here
import type { ChangeEvent } from 'react'; // Import types using 'type' keyword
import { Toaster, toast } from 'sonner';
import { Button } from '../components/ui/button'; // Assuming you have this Button component
import { Textarea } from '../components/ui/textarea'; // Assuming you have this Textarea component
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'; // Assuming Card components

// Optional: You might want a simple file input component or adapt DocumentUploader later
// For now, we'll use a basic HTML file input with FileReader.

const SummarizePage: React.FC = () => {
  const [inputText, setInputText] = useState<string>('');
  const [summaryOutput, setSummaryOutput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const outputRef = useRef<HTMLDivElement>(null); // Ref for the contenteditable div

  const API_KEY = import.meta.env.VITE_API_KEY; // Your API Key for backend calls

  // --- Input Handling ---

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast.error("File is too large (max 5MB).");
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        const textContent = e.target?.result as string;
        setInputText(textContent);
        toast.success(`File "${file.name}" loaded successfully.`);
      };
      reader.onerror = () => {
        toast.error("Failed to read file.");
      };
      reader.readAsText(file); // Read the file content as text
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
  };

  // --- Summarization Logic ---

  const handleSummarize = async () => {
    if (!inputText.trim()) {
      toast.error("Please provide text or upload a file for summarization.");
      return;
    }
    console.log("Sending text to backend:", inputText); // ADD THIS LINE
    console.log("Sending JSON body:", JSON.stringify({ text: inputText })); // ADD THIS LINE

    setLoading(true);
    setSummaryOutput(''); // Clear previous summary

    try {
      const response = await fetch("http://localhost:8000/summaries/generate/", { // Assuming your summarize endpoint
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ text: inputText }), // Send the input text to the backend
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Summarization failed.");
      }

      const result = await response.json();
      setSummaryOutput(result.summary); // Assuming backend returns { summary: "..." }
      toast.success("Summary generated successfully!");

    } catch (error: any) {
      console.error("Summarization error:", error);
      toast.error(`Summarization error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // --- Output Editing & Saving ---

  const handleSaveSummary = () => {
    // Get the current content from the editable div
    const currentSummary = outputRef.current?.innerText || ''; // Use innerText to get plain text

    if (!currentSummary.trim()) {
      toast.error("Summary is empty. Nothing to save.");
      return;
    }

    // --- Implement your saving logic here ---
    // You could save to local storage, or send to a backend endpoint.
    // For now, let's just log it and show a toast.

    console.log("Saving summary:", currentSummary);
    toast.success("Summary saved (check console for now)!");

    // Example of sending to a backend save endpoint (you'll need to create this)
    /*
    fetch("http://localhost:8000/save-summary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
      },
      body: JSON.stringify({ summary: currentSummary }),
    })
    .then(res => res.json())
    .then(data => toast.success(data.message || "Summary saved!"))
    .catch(err => toast.error("Failed to save summary."));
    */
  };

  const handleOutputEdit = () => {
    // This function is useful if you need to update summaryOutput state
    // continuously as user types in contenteditable div, or just on save.
    // For now, we'll only grab current content on Save.
  };


  return (
    <div className="flex flex-col items-center w-full min-h-[calc(100vh-theme(spacing.24))] py-8 px-4 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Summarize Transcriptions</h1>

      {/* Main Container for Input and Output */}
      <div className="flex flex-col md:flex-row gap-8 w-full">
        {/* Input Section */}
        <Card className="flex-1 min-w-[300px]">
          <CardHeader>
            <CardTitle>Input Transcription</CardTitle>
          </CardHeader>
          <CardContent>
            {/* File Input */}
            <label htmlFor="transcription-file" className="block text-sm font-medium text-gray-700 mb-2">
              Upload Transcription File (.txt, .json, etc.)
            </label>
            <input
              id="transcription-file"
              type="file"
              accept=".txt,.json,.md,.docx" // Add .docx if your backend handles it or if you parse it on frontend
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
            />

            <div className="my-4 text-center text-gray-500">
              OR
            </div>

            {/* Textarea for Direct Input */}
            <label htmlFor="transcription-text" className="block text-sm font-medium text-gray-700 mb-2">
              Paste Transcription Text
            </label>
            <Textarea
              id="transcription-text"
              placeholder="Paste your conversation transcription here..."
              value={inputText}
              onChange={handleTextareaChange}
              rows={15}
              className="w-full resize-y min-h-[200px]"
            />

            <Button onClick={handleSummarize} disabled={loading} className="mt-4 w-full">
              {loading ? "Summarizing..." : "Summarize"}
            </Button>
          </CardContent>
        </Card>

        {/* Output Section */}
        <Card className="flex-1 min-w-[300px]">
          <CardHeader>
            <CardTitle>Templated Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              ref={outputRef}
              contentEditable="true" // Makes the div editable
              onBlur={handleOutputEdit} // Capture changes when div loses focus (optional, you can also just read on save)
              className="w-full p-4 border rounded-md min-h-[300px] max-h-[500px] overflow-y-auto focus:outline-none focus:ring-2 focus:ring-primary-500 resize-y"
              dangerouslySetInnerHTML={{ __html: summaryOutput || "<p class='text-gray-500'>Your generated summary will appear here. You can edit it directly.</p>" }}
              // Using dangerouslySetInnerHTML to render potential HTML from backend (if summary is HTML)
              // Or if it's plain text, you can just set innerText directly on mount.
              // For simple plain text, it's often better to manage the innerText/textContent
              // directly or use a state-based approach rather than dangerouslySetInnerHTML unless needed for rich text.
              // For plain text, you might do:
              // onInput={(e) => setSummaryOutput(e.currentTarget.innerText)} if you want continuous updates.
            />
            <Button onClick={handleSaveSummary} disabled={!summaryOutput.trim()} className="mt-4 w-full">
              Save Summary
            </Button>
          </CardContent>
        </Card>
      </div>

      <Toaster />
    </div>
  );
};

export default SummarizePage;