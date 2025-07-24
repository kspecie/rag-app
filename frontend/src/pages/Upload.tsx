import React, { useState } from 'react';
import { DocumentUploader } from "../components/ui/upload";
import { Toaster } from 'sonner';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from '../components/ui/table';

interface UploadedFile {
    id: string;
    title: string;
    uploadDate: string;
}

const UploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const handleUploadSuccess = (fileInfo: any) => {
    console.log("File uploaded successfully to backend:", fileInfo);
    console.log("1. File info received by UploadPage for adding to table:", fileInfo);

    const newFile: UploadedFile = {
      id: fileInfo.id || new Date().getTime().toString(),
      title: fileInfo.filename || 'Unknown File',
      uploadDate: new Date().toLocaleDateString(),
    };

    setUploadedFiles(prevFiles => {
      const newState = [...prevFiles, newFile];
      console.log("2. New uploadedFiles state after adding:", newState);
      return newState;
    });
  };

  const handleUploadError = (error: string) => {
    console.error("File upload failed:", error);
  };

  return (
    // --- MODIFIED OUTERMOST CONTAINER ---
    // Change `flex justify-center items-start` to `flex flex-col items-center`
    // to make its children (h1, DocumentUploader, and Table) stack vertically.
    // Also, added `max-w-4xl` to this main content container to constrain its overall width.
    <div className="flex flex-col items-center w-full min-h-[calc(100vh-theme(spacing.24))] py-8 px-4 max-w-4xl mx-auto">
      {/* The h1, DocumentUploader, and the table section will now naturally stack */}
      <h1 className="text-3xl font-bold mb-8">Add new files to your knowledge source</h1>

      {/* DocumentUploader */}
      <DocumentUploader
        className="max-w-xl" // This controls the uploader's width itself
        onUploadSuccess={handleUploadSuccess}
        onUploadError={handleUploadError}
      />

      {/* Table Section - it will render below the DocumentUploader due to flex-col */}
      {uploadedFiles.length > 0 && (
        <div className="mt-12 w-full"> {/* mt-12 creates space between uploader and table */}
          <h2 className="text-2xl font-bold mb-4 text-center">Uploaded Documents</h2>
          <Table>
                <TableHeader>
                  <TableRow>
                    {/* Explicitly left-align the Title header */}
                    <TableHead className="text-left">Title</TableHead>
                    {/* Explicitly left-align the Upload Date header */}
                    <TableHead className="text-left">Upload Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {uploadedFiles.map((file) => (
                    <TableRow key={file.id}>
                      {/* Explicitly left-align the Title cell content */}
                      <TableCell className="text-left">{file.title}</TableCell>
                      {/* Explicitly left-align the Upload Date cell content */}
                      <TableCell className="text-left">{file.uploadDate}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
        </div>
      )}

      <Toaster />
    </div>
  );
};

export default UploadPage;