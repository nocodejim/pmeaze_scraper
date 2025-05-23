#!/usr/bin/env python3

"""
Simple RAG Tester for Performance Testing

A minimal RAG implementation to test your machine's performance
with a single document/page from the QuickBuild documentation.
"""

import json
import os
import time
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

class SimpleRAGTester:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize with a simple, fast model for testing.
        
        Args:
            model_name: Embedding model to use (CPU-friendly)
        """
        self.model_name = model_name
        self.text_content = ""
        self.embedding_model = None
        self.qa_pipeline = None
        
        print(f"🔧 Initializing Simple RAG Tester")
        print(f"📱 Model: {model_name}")
    
    def load_single_page(self, json_path: str, page_index: int = 0):
        """
        Load a single page from the scraped documentation for testing.
        
        Args:
            json_path: Path to all_content.json
            page_index: Which page to use (default: first page)
        """
        print(f"📄 Loading single page for testing...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            pages = json.load(f)
        
        if not pages:
            raise ValueError("No pages found in JSON file")
        
        if page_index >= len(pages):
            page_index = 0
            print(f"⚠️  Page index too high, using page 0")
        
        page = pages[page_index]
        self.text_content = page['full_text']
        self.page_title = page['title']
        self.page_url = page['url']
        
        print(f"✅ Loaded: {self.page_title}")
        print(f"📏 Content length: {len(self.text_content)} characters")
        print(f"🔗 URL: {self.page_url}")
    
    def setup_models(self):
        """Setup embedding and QA models."""
        print(f"\n🚀 Setting up models...")
        
        # Time the embedding model loading
        start_time = time.time()
        print(f"⏳ Loading embedding model...")
        self.embedding_model = SentenceTransformer(self.model_name)
        embedding_time = time.time() - start_time
        print(f"✅ Embedding model loaded in {embedding_time:.2f} seconds")
        
        # Time the QA model loading  
        start_time = time.time()
        print(f"⏳ Loading QA model...")
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad",
            tokenizer="distilbert-base-cased-distilled-squad"
        )
        qa_time = time.time() - start_time
        print(f"✅ QA model loaded in {qa_time:.2f} seconds")
        
        return embedding_time, qa_time
    
    def test_embedding_speed(self, test_texts: list = None):
        """Test embedding generation speed."""
        if test_texts is None:
            # Use chunks of the loaded text
            chunk_size = 200
            test_texts = [
                self.text_content[i:i+chunk_size] 
                for i in range(0, min(1000, len(self.text_content)), chunk_size)
            ]
        
        print(f"\n🏃 Testing embedding speed with {len(test_texts)} text chunks...")
        
        start_time = time.time()
        embeddings = self.embedding_model.encode(test_texts, show_progress_bar=True)
        embedding_time = time.time() - start_time
        
        print(f"✅ Generated {len(embeddings)} embeddings in {embedding_time:.2f} seconds")
        print(f"📊 Speed: {len(embeddings)/embedding_time:.1f} embeddings/second")
        print(f"📐 Embedding dimension: {embeddings[0].shape[0]}")
        
        return embedding_time, embeddings
    
    def test_qa_speed(self, test_questions: list = None):
        """Test question-answering speed."""
        if test_questions is None:
            test_questions = [
                "What is this page about?",
                "How do I configure this?",
                "What are the main features?",
                "What steps are involved?",
                "How do I get started?"
            ]
        
        print(f"\n❓ Testing QA speed with {len(test_questions)} questions...")
        
        # Limit context for faster processing
        context = self.text_content[:1500] if len(self.text_content) > 1500 else self.text_content
        
        results = []
        total_time = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"  {i}. {question}")
            
            start_time = time.time()
            try:
                result = self.qa_pipeline(question=question, context=context)
                qa_time = time.time() - start_time
                total_time += qa_time
                
                print(f"     ✅ Answer: {result['answer'][:100]}...")
                print(f"     ⏱️  Time: {qa_time:.2f}s, Score: {result['score']:.3f}")
                
                results.append({
                    'question': question,
                    'answer': result['answer'],
                    'score': result['score'],
                    'time': qa_time
                })
            except Exception as e:
                print(f"     ❌ Error: {e}")
                results.append({
                    'question': question,
                    'error': str(e),
                    'time': 0
                })
        
        avg_time = total_time / len(test_questions)
        print(f"\n📊 Average QA time: {avg_time:.2f} seconds per question")
        
        return results
    
    def run_performance_test(self, json_path: str):
        """Run a complete performance test."""
        print("="*60)
        print("🧪 SIMPLE RAG PERFORMANCE TEST")
        print("="*60)
        
        # Load single page
        self.load_single_page(json_path)
        
        # Setup models and time it
        embedding_load_time, qa_load_time = self.setup_models()
        
        # Test embedding speed
        embedding_time, embeddings = self.test_embedding_speed()
        
        # Test QA speed
        qa_results = self.test_qa_speed()
        
        # Summary
        print("\n" + "="*60)
        print("📈 PERFORMANCE SUMMARY")
        print("="*60)
        print(f"🏗️  Model Loading:")
        print(f"   Embedding model: {embedding_load_time:.2f}s")
        print(f"   QA model: {qa_load_time:.2f}s")
        print(f"   Total: {embedding_load_time + qa_load_time:.2f}s")
        
        print(f"\n⚡ Processing Speed:")
        print(f"   Embeddings: {len(embeddings)/embedding_time:.1f} per second")
        print(f"   Questions: {len([r for r in qa_results if 'error' not in r])/sum(r.get('time', 0) for r in qa_results):.1f} per second")
        
        print(f"\n💻 System Recommendations:")
        if embedding_load_time < 25:  # Adjusted for first-time download
            print("   ✅ Good model loading speed")
        else:
            print("   ⚠️  Slow model loading - consider smaller models")
        
        if len(embeddings)/embedding_time > 10:
            print("   ✅ Good embedding speed")
        else:
            print("   ⚠️  Slow embeddings - consider CPU optimization")
        
        avg_qa_time = sum(r.get('time', 0) for r in qa_results) / len(qa_results)
        if avg_qa_time < 0.2:  # Adjusted threshold
            print("   ✅ Good QA speed")
        else:
            print("   ⚠️  Slow QA - consider lighter models")
        
        print(f"\n📝 Note: First run includes model downloads. Subsequent runs will be much faster.")
    
    def interactive_test(self):
        """Interactive mode for manual testing."""
        print("\n🎮 Interactive Test Mode")
        print("Ask questions about the loaded page")
        print("Type 'exit' to quit")
        
        context = self.text_content[:1500] if len(self.text_content) > 1500 else self.text_content
        print(f"📄 Using content from: {self.page_title}")
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['exit', 'quit']:
                    break
                
                if not question:
                    continue
                
                start_time = time.time()
                result = self.qa_pipeline(question=question, context=context)
                qa_time = time.time() - start_time
                
                print(f"💡 Answer: {result['answer']}")
                print(f"📊 Confidence: {result['score']:.3f}")
                print(f"⏱️  Time: {qa_time:.2f} seconds")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple RAG Performance Tester')
    parser.add_argument('--json', default='scraper/output/all_content.json',
                        help='Path to scraped documentation JSON')
    parser.add_argument('--page', type=int, default=0,
                        help='Page index to test with (default: 0)')
    parser.add_argument('--model', default='all-MiniLM-L6-v2',
                        help='Embedding model to use')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode after performance test')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.json):
        print(f"❌ JSON file not found: {args.json}")
        print("Run the scraper first to generate documentation")
        return
    
    try:
        tester = SimpleRAGTester(args.model)
        
        # Run performance test
        tester.run_performance_test(args.json)
        
        # Interactive mode if requested
        if args.interactive:
            tester.interactive_test()
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()