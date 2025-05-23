#!/usr/bin/env python3

"""
QuickBuild Documentation RAG Agent

A complete RAG (Retrieval-Augmented Generation) system for QuickBuild documentation.
Uses CPU-friendly models that work well on AMD/Intel systems.
"""

import json
import os
import argparse
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

class QuickBuildRAG:
    def __init__(self, json_path: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG system with scraped QuickBuild documentation.
        
        Args:
            json_path: Path to the all_content.json file
            model_name: Sentence transformer model (CPU-friendly)
        """
        self.json_path = json_path
        self.model_name = model_name
        self.documents = []
        self.embeddings = None
        self.index = None
        self.embedding_model = None
        self.qa_pipeline = None
        
        print(f"Initializing QuickBuild RAG system...")
        print(f"Using embedding model: {model_name}")
        
        # Load and process documents
        self._load_documents()
        self._create_embeddings()
        self._setup_qa_pipeline()
        
        print(f"RAG system ready! Loaded {len(self.documents)} document sections.")
    
    def _load_documents(self):
        """Load and process documents from the scraped JSON."""
        print("Loading documents from JSON...")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            pages = json.load(f)
        
        self.documents = []
        
        for page in pages:
            # Process each section as a separate document
            if page['sections']:
                for section in page['sections']:
                    if section['content'].strip():
                        doc = {
                            'content': section['content'],
                            'title': page['title'],
                            'section_header': section['header'],
                            'url': page['url'],
                            'breadcrumb': ' > '.join(page['breadcrumb']),
                            'full_context': f"Page: {page['title']}\nSection: {section['header']}\nContent: {section['content']}"
                        }
                        self.documents.append(doc)
            else:
                # If no sections, use the full page
                if page['full_text'].strip():
                    doc = {
                        'content': page['full_text'],
                        'title': page['title'],
                        'section_header': 'Full Page',
                        'url': page['url'],
                        'breadcrumb': ' > '.join(page['breadcrumb']),
                        'full_context': f"Page: {page['title']}\nContent: {page['full_text']}"
                    }
                    self.documents.append(doc)
        
        print(f"Processed {len(self.documents)} document sections")
    
    def _create_embeddings(self):
        """Create embeddings for all documents using CPU-friendly model."""
        print("Creating embeddings (this may take a moment)...")
        
        # Load sentence transformer model (works well on CPU)
        self.embedding_model = SentenceTransformer(self.model_name)
        
        # Extract text for embedding
        texts = [doc['content'] for doc in self.documents]
        
        # Create embeddings
        self.embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index for fast similarity search
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        print(f"Created {len(self.embeddings)} embeddings with dimension {dimension}")
    
    def _setup_qa_pipeline(self):
        """Setup the question-answering pipeline."""
        print("Setting up QA pipeline...")
        
        # Use a CPU-friendly QA model
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad",
            tokenizer="distilbert-base-cased-distilled-squad"
        )
        
        print("QA pipeline ready")
    
    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve the most relevant documents for a query.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with scores
        """
        # Encode the query
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search for similar documents
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Return relevant documents with scores
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            doc = self.documents[idx].copy()
            doc['relevance_score'] = float(score)
            doc['rank'] = i + 1
            results.append(doc)
        
        return results
    
    def generate_answer(self, query: str, context_docs: List[Dict]) -> Dict:
        """
        Generate an answer using the QA pipeline and retrieved documents.
        
        Args:
            query: User's question
            context_docs: Retrieved relevant documents
            
        Returns:
            Dictionary with answer and metadata
        """
        # Combine contexts from top documents
        combined_context = "\n\n".join([
            f"Section: {doc['section_header']}\n{doc['content']}"
            for doc in context_docs
        ])
        
        # Limit context length for the model
        max_context_length = 2000
        if len(combined_context) > max_context_length:
            combined_context = combined_context[:max_context_length] + "..."
        
        try:
            # Use QA pipeline to generate answer
            result = self.qa_pipeline(question=query, context=combined_context)
            
            return {
                'answer': result['answer'],
                'confidence': result['score'],
                'sources': [
                    {
                        'title': doc['title'],
                        'section': doc['section_header'],
                        'url': doc['url'],
                        'relevance': doc['relevance_score']
                    }
                    for doc in context_docs
                ],
                'context_used': combined_context[:500] + "..." if len(combined_context) > 500 else combined_context
            }
        except Exception as e:
            return {
                'answer': f"I couldn't generate a specific answer, but here's what I found in the documentation: {context_docs[0]['content'][:300]}...",
                'confidence': 0.5,
                'sources': [
                    {
                        'title': doc['title'],
                        'section': doc['section_header'],
                        'url': doc['url'],
                        'relevance': doc['relevance_score']
                    }
                    for doc in context_docs
                ],
                'error': str(e)
            }
    
    def ask(self, question: str, top_k: int = 3) -> Dict:
        """
        Ask a question and get an answer with sources.
        
        Args:
            question: The question to ask
            top_k: Number of relevant documents to consider
            
        Returns:
            Complete answer with sources and metadata
        """
        print(f"\nQuestion: {question}")
        print("-" * 50)
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_docs(question, top_k)
        
        if not relevant_docs:
            return {
                'answer': "I couldn't find relevant information in the QuickBuild documentation.",
                'confidence': 0.0,
                'sources': []
            }
        
        # Step 2: Generate answer
        result = self.generate_answer(question, relevant_docs)
        
        return result
    
    def interactive_mode(self):
        """Run in interactive mode for continuous questions."""
        print("\n" + "="*60)
        print("QuickBuild Documentation Assistant")
        print("Ask questions about QuickBuild configuration and usage.")
        print("Type 'exit' to quit, 'help' for examples.")
        print("="*60)
        
        example_questions = [
            "How do I add a step to an existing configuration?",
            "What are the different types of build triggers?",
            "How do I set up email notifications?",
            "What is the difference between build configurations and build steps?"
        ]
        
        while True:
            try:
                question = input("\n🤖 Ask me about QuickBuild: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if question.lower() == 'help':
                    print("\nExample questions you can ask:")
                    for i, q in enumerate(example_questions, 1):
                        print(f"{i}. {q}")
                    continue
                
                if not question:
                    continue
                
                # Get answer
                result = self.ask(question)
                
                # Display answer
                print(f"\n💡 Answer: {result['answer']}")
                print(f"\n📊 Confidence: {result['confidence']:.2f}")
                
                print(f"\n📚 Sources:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['title']} - {source['section']}")
                    print(f"     URL: {source['url']}")
                    print(f"     Relevance: {source['relevance']:.3f}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='QuickBuild Documentation RAG Assistant')
    parser.add_argument('--json', default='scraper/output/all_content.json',
                        help='Path to the scraped documentation JSON file')
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                        help='Sentence transformer model to use')
    parser.add_argument('--question', type=str,
                        help='Ask a single question (non-interactive mode)')
    parser.add_argument('--top-k', type=int, default=3,
                        help='Number of relevant documents to retrieve')
    
    args = parser.parse_args()
    
    # Check if JSON file exists
    if not os.path.exists(args.json):
        print(f"Error: JSON file not found at {args.json}")
        print("Please run the scraper first to generate the documentation.")
        return
    
    try:
        # Initialize RAG system
        rag = QuickBuildRAG(args.json, args.model)
        
        if args.question:
            # Single question mode
            result = rag.ask(args.question, args.top_k)
            
            print(f"Question: {args.question}")
            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print("\nSources:")
            for source in result['sources']:
                print(f"  - {source['title']} ({source['section']})")
        else:
            # Interactive mode
            rag.interactive_mode()
            
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install sentence-transformers faiss-cpu transformers torch")


if __name__ == "__main__":
    main()
