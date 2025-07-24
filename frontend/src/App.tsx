import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css'; //  global CSS

import HomePage from "./pages/Home"; 
import UploadPage from "./pages/Upload"; 
import SummarisePage from "./pages/Summarise";
import Header from "./components/ui/header"
import Navigation from './sections/navigation'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
       <Header />
       <Navigation />

        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/summarise" element={<SummarisePage />} />

            {/* A catch-all route for 404 Not Found pages */}
            <Route path="*" element={
              <div className="text-center p-8">
                <h2 className="text-2xl font-semibold">404 - Page Not Found</h2>
                <p>Sorry, the page you are looking for does not exist.</p>
                <Link to="/" className="text-blue-600 hover:underline mt-4 block">Go to Home</Link>
              </div>
            } />
          </Routes>
        </main>

        {/* footer */}
        <footer className="bg-gray-200 p-4 text-center text-gray-600 text-sm">
          &copy; {new Date().getFullYear()} My RAG App
        </footer>
      </div>
    </Router>
  );
}

export default App;