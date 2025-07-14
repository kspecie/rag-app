import { NavigationMenu, NavigationMenuList, NavigationMenuLink, NavigationMenuContent, NavigationMenuItem, NavigationMenuTrigger } from "../components/ui/navigation-menu"

export default function Navigation(){
    return (
    <div>
        <NavigationMenu>   
        <NavigationMenuList>
        <NavigationMenuItem>
            <NavigationMenuTrigger>Upload</NavigationMenuTrigger>
                <NavigationMenuContent>
                    <NavigationMenuLink href="#">Upload Item 1</NavigationMenuLink>
                    <NavigationMenuLink href="#">Upload Item 2</NavigationMenuLink>
                </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
            <NavigationMenuTrigger>Test</NavigationMenuTrigger>
                <NavigationMenuContent>
                    <NavigationMenuLink href="#">Test Item 1</NavigationMenuLink>
                    <NavigationMenuLink href="#">Test Item 2</NavigationMenuLink>
                </NavigationMenuContent>
        </NavigationMenuItem>
        </NavigationMenuList>
        </NavigationMenu>
    </div>
    )
}