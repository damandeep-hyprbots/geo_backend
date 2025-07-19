#!/usr/bin/env python3
"""
Simple test script for the Enhanced GEO Agent
Tests the agentic framework that optimizes HTML in a single step
"""

import os
from dotenv import load_dotenv
from geo_agent_enhanced import EnhancedGEOAgent, display_optimization_results, save_optimization_results

# Load environment variables
load_dotenv()


def test_enhanced_agent():
    """Test the enhanced GEO agent with single-step HTML optimization"""
    print("\n" + "="*60)
    print("TESTING ENHANCED GEO AGENT - SINGLE STEP OPTIMIZATION")
    print("="*60)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return None
    
    if not os.getenv("JINA_API_KEY"):
        print("❌ JINA_API_KEY not found in environment variables")
        return None
    
    # Initialize the enhanced agent
    agent = EnhancedGEOAgent()
    
    # Test parameters
    website_url = "https://www.hyperbots.com"
    target_keyword = "finance"
    improvement_threshold = 0.000001
    
    print(f"Website: {website_url}")
    print(f"Target Keyword: {target_keyword}")
    print(f"Improvement Threshold: {improvement_threshold}")
    print()
    
    try:
        # Run optimization
        print("🔄 Starting single-step HTML optimization...")
        results = agent.optimize_website(
            website_url=website_url,
            target_keyword=target_keyword,
            improvement_threshold=improvement_threshold
        )
        
        # Display results
        display_optimization_results(results)
        
        # Save results
        save_optimization_results(results, "test_single_step_results.json")
        
        # Show HTML info
        print(f"\n📄 OPTIMIZED HTML INFO:")
        print("-" * 30)
        print(f"HTML length: {len(results['optimized_html'])} characters")
        print(f"HTML preview: {results['optimized_html'][:200]}...")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in enhanced agent test: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run the test"""
    print("🚀 Enhanced GEO Agent Test - Single Step Optimization")
    print("Testing iterative website optimization with full HTML modification in one step")
    
    # Run test
    results = test_enhanced_agent()
    
    # Summary
    if results:
        print(f"\n🎯 TEST SUMMARY:")
        print(f"Initial Score: {results['initial_score']:.4f}")
        print(f"Final Score: {results['final_score']:.4f}")
        print(f"Total Improvement: {results['improvement']:.4f}")
        print(f"Steps Attempted: {results['optimization_summary']['total_steps']}")
        print(f"Successful Optimizations: {len(results['optimization_history'])}")
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed!")
    
    print("Check test_single_step_results.json for detailed results.")


if __name__ == "__main__":
    main() 