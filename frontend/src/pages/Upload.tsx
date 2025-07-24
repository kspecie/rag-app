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

    <div className="flex flex-col items-center w-full min-h-[calc(100vh-theme(spacing.24))] py-8 px-4 max-w-4xl mx-auto">
    
      <h1 className="text-3xl font-bold mb-8">Add new files to your knowledge source</h1>

      {/* DocumentUploader */}
      <DocumentUploader
        className="max-w-xl"
        onUploadSuccess={handleUploadSuccess}
        onUploadError={handleUploadError}
      />

      {/* Table Section */}
      {uploadedFiles.length > 0 && (
        <div className="mt-12 w-full"> 
          <h2 className="text-2xl font-bold mb-4 text-center">Uploaded Documents</h2>
          <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-left">Title</TableHead>
                    <TableHead className="text-left">Upload Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {uploadedFiles.map((file) => (
                    <TableRow key={file.id}>
                      <TableCell className="text-left">{file.title}</TableCell>
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