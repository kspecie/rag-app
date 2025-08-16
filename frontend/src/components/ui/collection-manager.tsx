// import React, { useState, useEffect } from 'react';
// import { Button } from './button';
// import {
//   Card,
//   CardHeader,
//   CardTitle,
//   CardDescription,
//   CardContent,
//   CardFooter
// } from './card';
// import { useToast } from './use-toast';
// import { Loader2 } from 'lucide-react';

// interface Collection {
//   name: string;
//   description: string;
//   lastUpdated?: string;
// }

// const collectionsConfig: Omit<Collection, 'lastUpdated'>[] = [
//   {
//     name: "Miriad Knowledge",
//     description: "Contains downloaded data from the Miriad dataset. This is a static knowledge source."
//   },
//   {
//     name: "Nice Knowledge",
//     description: "Contains data pulled from the NICE API. This knowledge source can be periodically updated."
//   },
//   {
//     name: "My Documents",
//     description: "Stores documents you've uploaded. You can delete this collection to clear user-uploaded files."
//   }
// ];

// export const CollectionManager: React.FC = () => {
//   const [loadingCollection, setLoadingCollection] = useState<string | null>(null);
//   const [collections, setCollections] = useState<Collection[]>([]);
//   const { toast } = useToast();

//   // Fetch individual collection data
// const fetchCollectionData = async (collection: Omit<Collection, 'lastUpdated'>): Promise<Collection> => {
//     const existing = collections.find(c => c.name === collection.name);
//     if (existing?.lastUpdated === 'Collection deleted') {
//       return {
//         ...collection,
//         lastUpdated: 'Collection deleted',
//       };
//     }
  
//     try {
//       const response = await fetch(`/api/collections/${encodeURIComponent(collection.name)}`, {
//         headers: {
//           'X-API-Key': import.meta.env.VITE_API_KEY
//         }
//       });
      
//       if (!response.ok) {
//         if (response.status === 404) {
//           return {
//             ...collection,
//             lastUpdated: 'Collection deleted',
//           };
//         }
//         throw new Error(`Failed to fetch info for ${collection.name}`);
//       }
      
//       const data = await response.json();
//       return {
//         ...collection,
//         // lastUpdated: new Date(data.last_updated).toLocaleString(),
//         lastUpdated: data.last_updated
//             ? new Date(data.last_updated).toLocaleString()
//             : "Collection Deleted",
//       };
//     } catch (error) {
//       console.error(`Error fetching ${collection.name}:`, error);
//       return {
//         ...collection,
//         lastUpdated: 'Error fetching date',
//       };
//     }
//   };
  
//   // Fetch all collections data on component mount
//   const fetchAllCollectionsData = async () => {
//     const updatedCollections = await Promise.all(
//       collectionsConfig.map(collection => fetchCollectionData(collection))
//     );
//     setCollections(updatedCollections);
//   };

//   // Use useEffect to fetch data when the component mounts
//   useEffect(() => {
//     fetchAllCollectionsData();
//   }, []);

//   const handleAction = async (action: 'delete' | 'index', collectionName: string) => {
//     setLoadingCollection(collectionName);
//     const endpoint = `/api/collections/${action}`;
    
//     try {
//       const response = await fetch(endpoint, {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//           'X-API-Key': import.meta.env.VITE_API_KEY
//         },
//         body: JSON.stringify({ collection_name: collectionName }),
//       });

//       if (!response.ok) {
//         throw new Error(`Failed to ${action} collection: ${response.statusText}`);
//       }
      
//       const result = await response.json();
      
//       // Fix the action past tense
//       const actionPastTense = action === 'delete' ? 'deleted' : 'updated';
      
//       toast("Success", {
//         description: `${collectionName} collection has been ${actionPastTense} successfully.`,
//       });
      
//       console.log(result.message);

//       // Only refresh data after index (update) operations
//       if (action === 'index') {
//         await fetchAllCollectionsData();
//       } else if (action === 'delete') {
//         console.log("Updating UI after delete for:", collectionName);
//         // For delete, just update the UI to show it's been deleted
//         setCollections(prev => 
//           prev.map(c => c.name === collectionName 
//             ? { ...c, lastUpdated: 'Collection deleted' }
//             : c
//           )
//         );
//       }

//     } catch (error: any) {
//       console.error(`Error during ${action} operation:`, error);
//       const errorMessage = error?.message || error?.toString() || 'Unknown error';
//       toast("Error", {
//         description: `Failed to ${action} ${collectionName}: ${errorMessage}`,
//       });
//     } finally {
//       setLoadingCollection(null);
//     }
//   };



//   return (
//     <div className="grid gap-6 md:grid-cols-3 max-w-4xl w-full">
//       {collections.map((collection) => (
//         <Card key={collection.name} className="flex flex-col">
//           <CardHeader>
//             <CardTitle>{collection.name}</CardTitle>
//             <CardDescription>{collection.description}</CardDescription>
//           </CardHeader>
//           <CardContent className="flex-grow">
//             {collection.lastUpdated && (
//               <p className="text-sm text-gray-500 mt-2">
//                 Last Updated: {collection.lastUpdated}
//               </p>
//             )}
//           </CardContent>
//           <CardFooter className="flex gap-2 justify-center">
//             <Button
//               type="button"
//               onClick={(e) => {
//                 e.preventDefault();
//                 e.stopPropagation();
//                 handleAction('delete', collection.name);
//               }}
//               className="bg-white text-black hover:bg-gray-100 border border-red-500"
//               disabled={loadingCollection === collection.name}
//             >
//               {loadingCollection === collection.name ? (
//                 <>
//                   <Loader2 className="mr-2 h-4 w-4 animate-spin" />
//                   Deleting...
//                 </>
//               ) : "Delete"}
//             </Button>
            
//             {collection.name !== 'My Documents' && (
//               <Button
//                 type="button"
//                 onClick={(e) => {
//                   e.preventDefault();
//                   e.stopPropagation();
//                   handleAction('index', collection.name);
//                 }}
//                 className="bg-[#005EB8] text-white hover:bg-blue-700"
//                 disabled={loadingCollection === collection.name}
//               >
//                 {loadingCollection === collection.name ? (
//                   <>
//                     <Loader2 className="mr-2 h-4 w-4 animate-spin" />
//                     Updating...
//                   </>
//                 ) : "Update"}
//               </Button>
//             )}
//           </CardFooter>
//         </Card>
//       ))}
//     </div>
//   );
// };


import React, { useState, useEffect } from 'react';
import { Button } from './button';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from './card';
import { useToast } from './use-toast';
import { Loader2 } from 'lucide-react';

interface Collection {
  name: string;
  description: string;
  lastUpdated?: string;
}

const collectionsConfig: Omit<Collection, 'lastUpdated'>[] = [
  {
    name: "Miriad Knowledge",
    description: "Contains downloaded data from the Miriad dataset. This is a static knowledge source."
  },
  {
    name: "Nice Knowledge",
    description: "Contains data pulled from the NICE API. This knowledge source can be periodically updated."
  },
  {
    name: "My Documents",
    description: "Stores documents you've uploaded. You can delete this collection to clear user-uploaded files."
  }
];

export const CollectionManager: React.FC = () => {
  const [loadingCollection, setLoadingCollection] = useState<string | null>(null);
  const [collections, setCollections] = useState<Collection[]>([]);
  const { toast } = useToast();

  // Fetch individual collection data
  const fetchCollectionData = async (collection: Omit<Collection, 'lastUpdated'>): Promise<Collection> => {
    const existing = collections.find(c => c.name === collection.name);
    if (existing?.lastUpdated === 'Collection deleted') {
      return {
        ...collection,
        lastUpdated: 'Collection deleted',
      };
    }

    try {
      const response = await fetch(`/api/collections/${encodeURIComponent(collection.name)}`, {
        headers: {
          'X-API-Key': import.meta.env.VITE_API_KEY
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return { ...collection, lastUpdated: 'Collection deleted' };
        }
        throw new Error(`Failed to fetch info for ${collection.name}`);
      }

      const data = await response.json();
      return {
        ...collection,
        lastUpdated: data.last_updated
          ? new Date(data.last_updated).toLocaleString()
          : 'Collection deleted',
      };
    } catch (error) {
      console.error(`Error fetching ${collection.name}:`, error);
      return { ...collection, lastUpdated: 'Error fetching date' };
    }
  };

  // Fetch all collections data
  const fetchAllCollectionsData = async () => {
    const updatedCollections = await Promise.all(
      collectionsConfig.map(collection => fetchCollectionData(collection))
    );
    setCollections(updatedCollections);
  };

  useEffect(() => {
    fetchAllCollectionsData();
  }, []);

  const handleAction = async (action: 'delete' | 'index', collectionName: string) => {
    setLoadingCollection(collectionName);
    const endpoint = `/api/collections/${action}`;

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': import.meta.env.VITE_API_KEY
        },
        body: JSON.stringify({ collection_name: collectionName }),
      });

      if (!response.ok) {
        throw new Error(`Failed to ${action} collection: ${response.statusText}`);
      }

      const result = await response.json();

      const actionPastTense = action === 'delete' ? 'deleted' : 'updated';
      toast("Success", {
        description: `${collectionName} collection has been ${actionPastTense} successfully.`,
      });

      console.log(result.message);

      if (action === 'index') {
        await fetchAllCollectionsData();
      } else if (action === 'delete') {
        setCollections(prev =>
          prev.map(c =>
            c.name === collectionName ? { ...c, lastUpdated: 'Collection deleted' } : c
          )
        );
      }

    } catch (error: any) {
      console.error(`Error during ${action} operation:`, error);
      const errorMessage = error?.message || error?.toString() || 'Unknown error';
      toast("Error", {
        description: `Failed to ${action} ${collectionName}: ${errorMessage}`,
      });
    } finally {
      setLoadingCollection(null);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-3 max-w-4xl w-full">
      {collections.map(collection => (
        <Card key={collection.name} className="flex flex-col">
          <CardHeader>
            <CardTitle>{collection.name}</CardTitle>
            <CardDescription>{collection.description}</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            {collection.lastUpdated && (
              <p className="text-sm text-gray-500 mt-2">
                Last Updated: {collection.lastUpdated}
              </p>
            )}
          </CardContent>
          <CardFooter className="flex gap-2 justify-center">
            <Button
              type="button"
              onClick={e => {
                e.preventDefault();
                e.stopPropagation();
                handleAction('delete', collection.name);
              }}
              className="bg-white text-black hover:bg-gray-100 border border-red-500"
              disabled={loadingCollection === collection.name}
            >
              {loadingCollection === collection.name ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : "Delete"}
            </Button>

            {collection.name !== 'My Documents' && (
              <Button
                type="button"
                onClick={e => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleAction('index', collection.name);
                }}
                className="bg-[#005EB8] text-white hover:bg-blue-700"
                disabled={loadingCollection === collection.name}
              >
                {loadingCollection === collection.name ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : "Update"}
              </Button>
            )}
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};
