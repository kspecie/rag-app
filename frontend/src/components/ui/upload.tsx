import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from "./button";
import { Progress } from "./progress";
import { toast } from "sonner";
import { cn } from "../../lib/utils";


const API_KEY = import.meta.env.VITE_API_KEY; 

interface DocumentUploaderProps {
  onUploadSuccess: (fileInfo: { id: string; filename: string }) => void; 
  onUploadError: (error: string) => void;
  className?: string;
}

export function DocumentUploader({
  onUploadSuccess,
  onUploadError,
  className
}: DocumentUploaderProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    if (acceptedFiles.length > 0) {
      toast.info(`Selected ${acceptedFiles.length} file(s). Ready to upload.`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc', '.docx'],
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxSize: 1024 * 1024 * 5, // 5MB limit per file
  });

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error("Please select file(s) first.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    files.forEach(file => {
        formData.append("files", file);
    });


    try {
      const response = await fetch("http://localhost:8006/api/documents/upload/", {
        method: "POST",
        body: formData,
        headers: {
          'X-API-Key': API_KEY, 
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed.");
      }

      const result = await response.json();
      if (result.uploaded_files && Array.isArray(result.uploaded_files)) {
          result.uploaded_files.forEach((fileDetail: { id: string; filename: string }) => {
              onUploadSuccess({ id: fileDetail.id, filename: fileDetail.filename });
          });
          toast.success(`${result.uploaded_files.length} file(s) processed and added to ChromaDB!`);
      } else {
          toast.success("Files uploaded successfully, but no detailed info returned.");
          files.forEach(file => {
              onUploadSuccess({ id: Date.now().toString() + file.name, filename: file.name });
          });
      }

      setUploadProgress(100);
      setFiles([]); // Clear files after successful upload

    } catch (error: any) {
      toast.error(`Upload error: ${error.message}`);
      onUploadError(error.message);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <Card className={cn("w-full max-w-md", className)}>
      <CardHeader>
        <CardTitle>Document Upload</CardTitle>
        <CardDescription>Drag and drop your document(s) here, or click to select.</CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-gray-400 bg-background'}`}
        >
          <input {...getInputProps()} />
          {files.length === 0 ? (
            isDragActive ? (
              <p>Drop the files here ...</p>
            ) : (
              <p>Drag and drop your document(s) here, or click to select.</p>
            )
          ) : (
            <p className="text-muted-foreground">
              {files.length} file(s) selected. Click "Upload Document" to begin.
            </p>
          )}
        </div>

        {files.length > 0 && (
          <div className="mt-4">
            <p className="font-medium">Selected File{files.length > 1 ? 's' : ''}:</p>
            <ul className="list-disc list-inside text-sm text-muted-foreground">
              {files.map(file => (
                <li key={file.name} className="truncate">{file.name} - {Math.round(file.size / 1024)} KB</li>
              ))}
            </ul>
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setFiles([])} disabled={uploading}>Clear</Button>
              <Button onClick={handleUpload} disabled={uploading}>
                {uploading ? `Uploading...` : "Upload Document"}
              </Button>
            </div>
            {uploading && (
              <div className="mt-2">
                <Progress value={uploadProgress} className="w-full" />
                <p className="text-xs text-muted-foreground text-center mt-1">Processing...</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}