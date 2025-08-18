import React, { useEffect, useState } from 'react';
import { DocumentUploader } from "../components/ui/upload";
import { Toaster, toast } from 'sonner';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '../components/ui/table';
import { Button } from '../components/ui/button'


interface UploadedFile {
    id: string;
    title: string;
    uploadDate: string;
}

interface DataCollection {
    id: string;
    name: string;
    lastUpdated?: string
}

const UploadPage: React.FC = () => {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [lastUpdated, setLastUpdated] = useState<string | null>(null);
    const [otherCollections, setOtherCollections] = useState<DataCollection[]>([
        { id: 'miriad', name: 'Miriad Knowledge' },
        { id: 'nice', name: 'NICE Knowledge' },
    ]);

    const API_BASE = "http://localhost:8006/documents"; //FastAPI URL
    const COLLECTIONS_API = `http://localhost:8006/collections`;

    //fetch docs on page load
    useEffect(() => {
        fetch(API_BASE, {
            headers: {
                "X-API-Key": import.meta.env.VITE_API_KEY
            }
        })
            .then(res => res.json())
            .then(data => {
                console.log("Fetched docs:", data);
                const formattedFiles = data.map((doc: any) => ({
                    id: doc.id,
                    title: doc.title,
                    uploadDate: doc.upload_date
                        ? new Date(doc.upload_date).toLocaleDateString()
                        : "Unknown",
                }));
                setUploadedFiles(formattedFiles);
            })
            .catch(err => console.error("error fetching docs from chromabdb:", err));
    }, []);

    useEffect(() => {
      const fetchCollectionMetadata = async () => {
          try {
              const res = await fetch(COLLECTIONS_API, {
                  headers: {
                      "X-API-Key": import.meta.env.VITE_API_KEY
                  }
              });
              if (!res.ok) throw new Error("Failed to fetch collections");
  
              const data = await res.json();
              console.log("Fetched collections:", data);
  
              // Map last_updated info into otherCollections
              setOtherCollections(prevCollections =>
                  prevCollections.map(col => ({
                      ...col,
                      lastUpdated: data[col.id]?.last_updated
                          ? new Date(data[col.id].last_updated).toLocaleDateString()
                          : "Unknown"
                  }))
              );
          } catch (err) {
              console.error("Error fetching collection metadata:", err);
          }
      };
  
      fetchCollectionMetadata();
  }, []);
  

    const handleUploadSuccess = (fileInfo: any) => {
        const newFile: UploadedFile = {
            id: fileInfo.id || new Date().getTime().toString(),
            title: fileInfo.filename || 'Unknown File',
            uploadDate: new Date(fileInfo.upload_date || Date.now()).toLocaleDateString(),
        };
        setUploadedFiles(prevFiles => [...prevFiles, newFile]);
    };

    const handleUploadError = (error: string) => {
        console.error("File upload failed:", error);
        toast.error("File upload failed");
    };

    const handleDeleteCollectionUser = async () => {
        if (!window.confirm("Are you sure you want to delete ALL documents? This cannot be undone.")) return;
        try {
            const res = await fetch(API_BASE + "/collections/user", {
                method: "DELETE",
                headers: {
                    "X-API-Key": import.meta.env.VITE_API_KEY
                }
            });
            if (res.ok) {
                toast.success("Collection deleted successfully");
                setUploadedFiles([]);
            } else {
                const err = await res.json();
                toast.error(err.detail || "Failed to delete collection");
            }
        } catch (e) {
            toast.error("Error deleting collection");
        }
    };

const handleDeleteCollectionByName = async (collectionId: string) => {
  if (!window.confirm(`Are you sure you want to delete the ${collectionId} collection? This cannot be undone.`)) return;
  const endpoint = `${API_BASE}/collections/${collectionId}`;

  try {
    const res = await fetch(endpoint, {
      method: "DELETE",
      headers: {
        "X-API-Key": import.meta.env.VITE_API_KEY
      }
    });
    if (res.ok) {
      toast.success(`${collectionId} collection deleted successfully`);
      // You might want to trigger a refresh for the other collections too
    } else {
      const err = await res.json();
      toast.error(err.detail || `Failed to delete ${collectionId} collection`);
    }
  } catch (e) {
    toast.error(`Error deleting ${collectionId} collection`);
  }
};

const handleUpdateCollectionByName = async (collectionId: string) => {
  const collectionEndpoints: Record<string, string> = {
    nice: "update_nice",
    miriad: "update_miriad",
  };
  const endpointSuffix = collectionEndpoints[collectionId];
  if (!endpointSuffix) {
    toast.error(`No update endpoint defined for collection ${collectionId}`);
    return;
  }

  const endpoint = `${COLLECTIONS_API}/${endpointSuffix}`;
  
  // show loading toast
  const loadingToastId = toast.loading(`Updating ${collectionId} collection...This can take several minutes`);

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": import.meta.env.VITE_API_KEY
      }
    });
    if (res.ok){
      toast.success(`${collectionId} collection uploaded successfully`, { id: loadingToastId })
    } else {
      const err = await res.json();
      toast.error(err.detail || `Failed to upload ${collectionId} collection`, { id: loadingToastId })
    }
  } catch (e) {
    toast.error(`Error updating ${collectionId} collection`, { id: loadingToastId })
  }
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

            {/*Delete button*/}
            {uploadedFiles.length > 0 && (
                <div className="mt-6 flex justify-center">
                    <Button
                        variant="destructive"
                        className="bg-white border border-red-600 text-red-600 hover:bg-red-50"
                        onClick={handleDeleteCollectionUser}>
                        Delete All User Documents
                    </Button>
                </div>
            )}

            {/* Table Section */}
            {uploadedFiles.length > 0 && (
                <div className="mt-12 w-full">
                    <h2 className="text-2xl font-bold mb-4 text-center">Uploaded User Documents</h2>
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

            {/* Other Data Collections Section */}
            <div className="mt-12 w-full flex flex-col items-center">
                <h2 className="text-2xl font-bold mb-4 text-center">Other Data Collections</h2>
                <div className="flex flex-row gap-4 w-full items-center">
                    {otherCollections.map(collection => (
                        <div
                            key={collection.id}
                            className="p-4 rounded-lg shadow-md bg-white w-full max-w-md flex flex-col items-center"
                        >
                            <h3 className="font-bold text-lg mb-4">{collection.name}</h3>
                            <p className="text-sm text-gray-600 mb-4">
                                  Last Updated: {collection.lastUpdated || "Unknown"}
                              </p>
                            <div className="flex justify-center gap-4">
                                <Button
                                    className="bg-white border border-red-600 text-red-600 hover:bg-red-50"
                                    onClick={() => handleDeleteCollectionByName(collection.id)}
                                >
                                    Delete
                                </Button>
                                <Button
                                    className="bg-[#005EB8] text-white hover:bg-blue-700"
                                    onClick={() => handleUpdateCollectionByName(collection.id)}
                                >
                                    Update
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>


            <Toaster />
        </div>
    );
};

export default UploadPage;