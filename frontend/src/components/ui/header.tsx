import intelLogo from '../../assets/intelLogo.svg'; 
import nhsLogo from '../../assets/nhsLogo.svg';

export default function Header(){
    return (
    
        <div className="flex items-center justify-between h-24 p-4 bg-white shadow-md border-2">
            {/* Container for the two logos on the left side */}
            <div className="flex items-center space-x-4">
                {/* Intel Logo (SVG) */}
                <img src={intelLogo} alt="Intel Logo" className="h-16 w-auto" />
                {/* NHS Logo (SVG) */}
                <img src={nhsLogo} alt="NHS Logo" className="h-16 w-auto" />
            </div>
            {/* Application Name on the right side */}
            <h1 className="text-3xl font-bold text-gray-800">Clinical Summary Generator</h1>
        </div>
    )
}