#!/usr/bin/env python3
"""
Script to test web search functionality with custom parameters.
Usage: python test_web_search.py --query "your search query" --results 5
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.youtube_tracker.web_search import WebSearcher

# Configure logging
def setup_logging(log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger('web_search_test')
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def format_result(result):
    """Format a single search result for display"""
    return f"""
URL: {result['url']}
Title: {result['title']}
Snippet: {result['snippet']}
Context Length: {len(result['context'])} characters
Context Preview: {result['context'][:200]}...
{'='*80}
"""

def main():
    parser = argparse.ArgumentParser(description='Test web search functionality')
    parser.add_argument('--query', required=True, help='Search query to test')
    parser.add_argument('--results', type=int, default=5, help='Number of results to fetch (default: 5)')
    parser.add_argument('--log-file', help='Log file path (optional)')
    parser.add_argument('--output', help='Save results to JSON file (optional)')
    
    args = parser.parse_args()
    
    # Setup logging
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    default_log_file = log_dir / f'web_search_test_{timestamp}.log'
    
    logger = setup_logging(args.log_file or default_log_file)
    
    try:
        logger.info(f"Starting web search test with query: {args.query}")
        logger.info(f"Requesting {args.results} results")
        
        # Initialize and run search
        searcher = WebSearcher()
        results = searcher.search(args.query, args.results)
        
        # Log results
        logger.info(f"Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            logger.info(f"\nResult {i}:{format_result(result)}")
        
        # Save to JSON if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(exist_ok=True)
            
            output_data = {
                'query': args.query,
                'timestamp': timestamp,
                'num_results_requested': args.results,
                'num_results_found': len(results),
                'results': results
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error during web search test: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
