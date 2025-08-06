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

// //rag-app/frontend/src/pages/Upload.tsx
// import React, { useState } from 'react';
// import { DocumentUploader } from "../components/ui/upload";
// import { Toaster } from 'sonner';
// import {
//   Table,
//   TableBody,
//   TableCell,
//   TableHead,
//   TableHeader,
//   TableRow,
// } from '../components/ui/table';

// interface UploadedFile {
//   id: string;
//   title: string;
//   uploadDate: string;
// }

// const UploadPage: React.FC = () => {
//   const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
//   const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

//   // Handle successful upload
//   const handleUploadSuccess = (fileInfo: any) => {
//     const newFile: UploadedFile = {
//       id: fileInfo.id || new Date().getTime().toString(),
//       title: fileInfo.filename || 'Unknown File',
//       uploadDate: new Date().toLocaleDateString(),
//     };
//     setUploadedFiles(prev => [...prev, newFile]);
//   };

//   // Toggle selection for a given file id
//   const toggleSelection = (id: string) => {
//     setSelectedIds(prev => {
//       const newSet = new Set(prev);
//       if (newSet.has(id)) {
//         newSet.delete(id);
//       } else {
//         newSet.add(id);
//       }
//       return newSet;
//     });
//   };

//   const API_KEY = import.meta.env.VITE_API_KEY;
//   // Delete selected documents
//   const handleDeleteSelected = async () => {
//     if (selectedIds.size === 0) return alert("Select documents to delete.");

//     // Call backend API to delete documents by IDs
//     try {
//       const response = await fetch('http://localhost:8006/documents/delete/', {
//         method: 'DELETE',
//         headers: {
//           'Content-Type': 'application/json',
//           'X-API-Key': API_KEY
//         },
//         body: JSON.stringify({ ids: Array.from(selectedIds) }),
//       });
//       if (!response.ok) throw new Error('Delete failed');

//       // Remove deleted files from frontend state
//       setUploadedFiles(prev => prev.filter(file => !selectedIds.has(file.id)));
//       setSelectedIds(new Set());
//       alert('Selected documents deleted successfully.');
//     } catch (error) {
//       alert(`Error deleting documents: ${error.message}`);
//     }
//   };

//   return (
//     <div className="flex flex-col items-center w-full min-h-[calc(100vh-theme(spacing.24))] py-8 px-4 max-w-4xl mx-auto">
//       <h1 className="text-3xl font-bold mb-8">Add new files to your knowledge source</h1>

//       <DocumentUploader
//         className="max-w-xl"
//         onUploadSuccess={handleUploadSuccess}
//         onUploadError={(err) => console.error("Upload failed:", err)}
//       />

//       {uploadedFiles.length > 0 && (
//         <div className="mt-12 w-full">
//           <h2 className="text-2xl font-bold mb-4 text-center">Uploaded Documents</h2>
//           <button
//             className="mb-4 px-4 py-2 bg-red-600 text-white rounded"
//             onClick={handleDeleteSelected}
//             disabled={selectedIds.size === 0}
//           >
//             Delete Selected
//           </button>
//           <Table>
//             <TableHeader>
//               <TableRow>
//                 <TableHead></TableHead> {/* For checkbox */}
//                 <TableHead className="text-left">Title</TableHead>
//                 <TableHead className="text-left">Upload Date</TableHead>
//               </TableRow>
//             </TableHeader>
//             <TableBody>
//               {uploadedFiles.map((file) => (
//                 <TableRow key={file.id}>
//                   <TableCell>
//                     <input
//                       type="checkbox"
//                       checked={selectedIds.has(file.id)}
//                       onChange={() => toggleSelection(file.id)}
//                     />
//                   </TableCell>
//                   <TableCell className="text-left">{file.title}</TableCell>
//                   <TableCell className="text-left">{file.uploadDate}</TableCell>
//                 </TableRow>
//               ))}
//             </TableBody>
//           </Table>
//         </div>
//       )}

//       <Toaster />
//     </div>
//   );
// };

// export default UploadPage;


// import React, { useState, useEffect } from 'react';
// import { DocumentUploader } from "../components/ui/upload";
// import { Toaster } from 'sonner';
// import {
//   Table,
//   TableBody,
//   TableCell,
//   TableHead,
//   TableHeader,
//   TableRow,
// } from '../components/ui/table';

// interface UploadedFile {
//   id: string;
//   title: string;
//   chunk_count: number;
//   uploadDate: string;
// }

// const UploadPage: React.FC = () => {
//   const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
//   const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
//   const [loading, setLoading] = useState(false);

//   const API_KEY = import.meta.env.VITE_API_KEY;
//   const API_BASE_URL = 'http://localhost:8006';

//   // Load documents from backend on component mount
//   useEffect(() => {
//     // Only load documents on initial mount if you want to show previously uploaded docs
//     // Comment this out if you want to start fresh each time
//     // loadDocuments();
//   }, []);

//   const loadDocuments = async () => {
//     try {
//       setLoading(true);
//       const response = await fetch(`${API_BASE_URL}/documents/list/`, {
//         headers: {
//           'X-API-Key': API_KEY
//         }
//       });
      
//       if (!response.ok) {
//         throw new Error('Failed to load documents');
//       }
      
//       const data = await response.json();
//       setUploadedFiles(data.documents || []);
//     } catch (error) {
//       console.error('Error loading documents:', error);
//       alert(`Error loading documents: ${error.message}`);
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Handle successful upload
//   const handleUploadSuccess = (fileInfo: any) => {
//     console.log('Upload successful:', fileInfo);
    
//     // Create new file entry with current date (like your original code)
//     const newFile: UploadedFile = {
//       id: fileInfo.filename || fileInfo.name || new Date().getTime().toString(),
//       title: fileInfo.filename || fileInfo.name || 'Unknown File',
//       uploadDate: new Date().toLocaleDateString(),
//       chunk_count: 0 // We don't know chunk count from upload, will be updated when we load from backend
//     };
    
//     // Add to frontend state immediately
//     setUploadedFiles(prev => [...prev, newFile]);
    
//     // Optionally reload from backend to get accurate chunk counts
//     // Comment this out if you want to keep it simple
//     // loadDocuments();
//   };

//   // Toggle selection for a given file id
//   const toggleSelection = (id: string) => {
//     setSelectedIds(prev => {
//       const newSet = new Set(prev);
//       if (newSet.has(id)) {
//         newSet.delete(id);
//       } else {
//         newSet.add(id);
//       }
//       return newSet;
//     });
//   };

//   // Select all documents
//   const handleSelectAll = () => {
//     if (selectedIds.size === uploadedFiles.length) {
//       // If all are selected, deselect all
//       setSelectedIds(new Set());
//     } else {
//       // Select all
//       setSelectedIds(new Set(uploadedFiles.map(file => file.id)));
//     }
//   };

//   // Delete selected documents
//   const handleDeleteSelected = async () => {
//     if (selectedIds.size === 0) {
//       alert("Please select documents to delete.");
//       return;
//     }

//     if (!confirm(`Are you sure you want to delete ${selectedIds.size} document(s)?`)) {
//       return;
//     }

//     try {
//       setLoading(true);
//       const response = await fetch(`${API_BASE_URL}/documents/delete/`, {
//         method: 'DELETE',
//         headers: {
//           'Content-Type': 'application/json',
//           'X-API-Key': API_KEY
//         },
//         body: JSON.stringify({ ids: Array.from(selectedIds) }),
//       });
      
//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Delete failed');
//       }

//       const result = await response.json();
//       alert(result.message || 'Documents deleted successfully');
      
//       // Reload documents and clear selection
//       await loadDocuments();
//       setSelectedIds(new Set());
      
//     } catch (error) {
//       console.error('Delete error:', error);
//       alert(`Error deleting documents: ${error.message}`);
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Delete all documents
//   const handleDeleteAll = async () => {
//     if (uploadedFiles.length === 0) {
//       alert("No documents to delete.");
//       return;
//     }

//     if (!confirm("Are you sure you want to delete ALL documents? This cannot be undone.")) {
//       return;
//     }

//     try {
//       setLoading(true);
//       const response = await fetch(`${API_BASE_URL}/documents/delete-all/`, {
//         method: 'DELETE',
//         headers: {
//           'X-API-Key': API_KEY
//         }
//       });
      
//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Delete all failed');
//       }

//       const result = await response.json();
//       alert(result.message || 'All documents deleted successfully');
      
//       // Clear local state
//       setUploadedFiles([]);
//       setSelectedIds(new Set());
      
//     } catch (error) {
//       console.error('Delete all error:', error);
//       alert(`Error deleting all documents: ${error.message}`);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="flex flex-col items-center w-full min-h-[calc(100vh-theme(spacing.24))] py-8 px-4 max-w-4xl mx-auto">
//       <h1 className="text-3xl font-bold mb-8">Add new files to your knowledge source</h1>

//       <DocumentUploader
//         className="max-w-xl"
//         onUploadSuccess={handleUploadSuccess}
//         onUploadError={(err) => console.error("Upload failed:", err)}
//       />

//       {loading && (
//         <div className="mt-4 text-center">
//           <p>Loading...</p>
//         </div>
//       )}

//       {uploadedFiles.length > 0 && (
//         <div className="mt-12 w-full">
//           <h2 className="text-2xl font-bold mb-4 text-center">Uploaded Documents</h2>
          
//           <div className="mb-4 flex gap-2 flex-wrap">
//             <button
//               className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
//               onClick={handleSelectAll}
//               disabled={loading}
//             >
//               {selectedIds.size === uploadedFiles.length ? 'Deselect All' : 'Select All'}
//             </button>
            
//             <button
//               className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
//               onClick={handleDeleteSelected}
//               disabled={selectedIds.size === 0 || loading}
//             >
//               Delete Selected ({selectedIds.size})
//             </button>
            
//             <button
//               className="px-4 py-2 bg-red-800 text-white rounded hover:bg-red-900 disabled:opacity-50"
//               onClick={handleDeleteAll}
//               disabled={loading}
//             >
//               Delete All
//             </button>
//           </div>

//           <Table>
//             <TableHeader>
//               <TableRow>
//                 <TableHead className="w-12">
//                   <input
//                     type="checkbox"
//                     checked={uploadedFiles.length > 0 && selectedIds.size === uploadedFiles.length}
//                     onChange={handleSelectAll}
//                     disabled={loading}
//                   />
//                 </TableHead>
//                 <TableHead className="text-left">Title</TableHead>
//                 <TableHead className="text-left">Upload Date</TableHead>
//                 <TableHead className="text-left">Chunks</TableHead>
//               </TableRow>
//             </TableHeader>
//             <TableBody>
//               {uploadedFiles.map((file) => (
//                 <TableRow key={file.id}>
//                   <TableCell>
//                     <input
//                       type="checkbox"
//                       checked={selectedIds.has(file.id)}
//                       onChange={() => toggleSelection(file.id)}
//                       disabled={loading}
//                     />
//                   </TableCell>
//                   <TableCell className="text-left">{file.title}</TableCell>
//                   <TableCell className="text-left">{file.uploadDate}</TableCell>
//                   <TableCell className="text-left">{file.chunk_count} chunks</TableCell>
//                 </TableRow>
//               ))}
//             </TableBody>
//           </Table>
//         </div>
//       )}

//       <Toaster />
//     </div>
//   );
// };

// export default UploadPage;