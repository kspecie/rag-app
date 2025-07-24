import { Link } from 'react-router-dom'; 

import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationNavLink,
} from "../components/ui/navigation-menu"

export default function Navigation(){
    return (
    <div className="bg-white shadow-md py-4 px-4"> 
        <NavigationMenu>
            <NavigationMenuList>
            <NavigationMenuItem>
                    <NavigationNavLink asChild>
                        <Link to="/.">About</Link>
                    </NavigationNavLink>
                </NavigationMenuItem>
                <NavigationMenuItem>
                    {/* Use NavigationNavLink and pass asChild to render Link */}
                    <NavigationNavLink asChild>
                        <Link to="/upload">Upload RAG Docs</Link>
                    </NavigationNavLink>
                </NavigationMenuItem>
                <NavigationMenuItem>
                    <NavigationNavLink asChild>
                        <Link to="/summarise">Generate Summary</Link>
                    </NavigationNavLink>
                </NavigationMenuItem>
                {/* tbd - more NavigationMenuItems here */}
            </NavigationMenuList>
        </NavigationMenu>
    </div>
    )
}