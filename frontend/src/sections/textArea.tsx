import { useState } from "react";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";


export default function TextArea (){
    const [isEditable, setIsEditable] = useState(false);
    const [value, setValue] = useState("Generated templated output goes here");

    return (
        <div className="flex gap-6">
            <div className="flex-1 p-4 flex flex-col gap-4">
                <Textarea className="border-[#005EB8] bg-[#E8EDEE] text-black w-full"/>
                <div className="flex justify-end gap-2">
                    <Button   className="text-[#005EB8]" variant="outline" size="lg">Delete</Button>
                    <Button className="bg-[#005EB8] text-[#E8EDEE]" variant="outline" size="lg">Summarize!</Button>
                </div>
            </div>
           <div className="flex-1 p-4 flex flex-col gap-4">
                <Textarea 
                    className="border-[#005EB8] bg-[#E8EDEE] text-black w-full"
                    readOnly={!isEditable}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}/>
                <div className="flex justify-end gap-2">
                    <Button 
                        className="text-[#005EB8]"
                        variant="outline" 
                        size="lg"
                        onClick={() => setIsEditable(!isEditable)}>
                            {isEditable ? "Lock" : "Edit"}
                    </Button>
                    <Button className="bg-[#005EB8] text-[#E8EDEE]" variant="outline" size="lg">Save</Button>
                </div>
           </div>
        </div>
    )
}