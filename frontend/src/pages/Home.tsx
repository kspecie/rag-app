import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Upload, FileText, Brain, ArrowRight, BookOpen, Sparkles } from 'lucide-react';

export default function Home() {
    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center space-y-4 pt-8">
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    Transform your patient conversations into intelligent summaries in less than 15 seconds.
                </p>
            </div>

            {/* Main Features Grid */}
            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {/* Upload RAG Docs Card */}
                <Card className="h-full">
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-100 rounded-lg">
                                <Upload className="h-6 w-6 text-blue-600" />
                            </div>
                            <div>
                                <CardTitle className="text-xl">Upload RAG Docs</CardTitle>
                                <CardDescription>
                                    Build your knowledge base
                                </CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-gray-600">
                            Upload documents to create a searchable knowledge repository.
                        </p>
                        <div className="pt-4">
                            <Button asChild className="w-full">
                                <Link to="/upload">
                                    Start Uploading Documents
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Generate Summary Card */}
                <Card className="h-full">
                    <CardHeader>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-green-100 rounded-lg">
                                <Sparkles className="h-6 w-6 text-green-600" />
                            </div>
                            <div>
                                <CardTitle className="text-xl">Generate Summary</CardTitle>
                                <CardDescription>
                                    AI-powered summarization
                                </CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <p className="text-gray-600">
                            Transform text or uploaded files into structured H&P clinical summaries.
                        </p>
                        <div className="pt-4">
                            <Button asChild className="w-full">
                                <Link to="/summarise">
                                    Generate Summaries
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* How It Works Section */}
            <Card className="max-w-4xl mx-auto">
                <CardHeader>
                    <CardTitle className="text-2xl text-center">How It Works</CardTitle>
                    <CardDescription className="text-center">
                        Simple steps to get started with your document intelligence workflow
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="text-center space-y-3">
                            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                <span className="text-blue-600 font-bold text-lg">1</span>
                            </div>
                            <h3 className="font-semibold text-gray-900">Upload Documents</h3>
                            <p className="text-sm text-gray-600">
                                Upload your documents to build a comprehensive knowledge base that powers intelligent retrieval.
                            </p>
                        </div>
                        <div className="text-center space-y-3">
                            <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                                <span className="text-green-600 font-bold text-lg">2</span>
                            </div>
                            <h3 className="font-semibold text-gray-900">Generate Summaries</h3>
                            <p className="text-sm text-gray-600">
                                Input text or upload files to generate AI-powered summaries with structured formatting.
                            </p>
                        </div>
                        <div className="text-center space-y-3">
                            <div className="mx-auto w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                                <span className="text-purple-600 font-bold text-lg">3</span>
                            </div>
                            <h3 className="font-semibold text-gray-900">Review & Save</h3>
                            <p className="text-sm text-gray-600">
                                Edit summaries as needed and save them to your database for future reference and analysis.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}