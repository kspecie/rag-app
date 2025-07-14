import Navigation from "../sections/navigation"
import TextArea from "../sections/textArea"
import Header from "../components/ui/header"

export default function Home(){
    return (
        <div className="space-y-8">
            <Header />
            <Navigation />
            <TextArea />
        </div>
    )
}