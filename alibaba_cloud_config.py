"""
Alibaba Cloud Model Studio Configuration for Crypto Trading Platform

This module provides configuration and utilities for integrating with Alibaba Cloud's
DashScope models for our cryptocurrency trading platform.
"""

import os
from dotenv import load_dotenv
import dashscope
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

class AlibabaCloudConfig:
    """Configuration class for Alibaba Cloud Model Studio integration."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.region = os.getenv('ALIBABA_CLOUD_REGION', 'us-west-1')
        
        # Set the API key for dashscope
        if self.api_key:
            dashscope.api_key = self.api_key
        else:
            print("⚠️  Warning: DASHSCOPE_API_KEY not found in environment variables")
    
    # Recommended models for crypto trading platform
    RECOMMENDED_MODELS = {
        'primary_advisor': {
            'model': 'qwen-plus',
            'description': 'Best for AI investment advisor - balanced performance, cost, and capabilities',
            'use_case': 'Investment recommendations, risk analysis, portfolio optimization',
            'context_length': 131072,
            'cost_per_million_tokens': {'input': 0.4, 'output': 1.2},
            'features': ['thinking_mode', 'multilingual', 'agent_capability']
        },
        
        'sentiment_analysis': {
            'model': 'qwen-flash',
            'description': 'Fast and cost-effective for sentiment analysis of news/social media',
            'use_case': 'Processing large volumes of news articles, social media posts',
            'context_length': 1000000,
            'cost_per_million_tokens': {'input': 0.05, 'output': 0.4},
            'features': ['fast_processing', 'cost_effective', 'large_context']
        },
        
        'market_analysis': {
            'model': 'qwen-max',
            'description': 'Most powerful for complex market analysis and predictions',
            'use_case': 'Deep market analysis, complex trading strategies, risk assessment',
            'context_length': 32768,
            'cost_per_million_tokens': {'input': 1.6, 'output': 6.4},
            'features': ['highest_capability', 'complex_reasoning']
        },
        
        'text_embedding': {
            'model': 'text-embedding-v4',
            'description': 'For semantic search and similarity analysis of financial documents',
            'use_case': 'Document similarity, news clustering, semantic search',
            'vector_dimensions': 1024,
            'cost_per_million_tokens': {'input': 0.072},
            'features': ['multilingual', 'high_quality_embeddings']
        }
    }
    
    def get_model_config(self, use_case: str) -> Dict:
        """Get recommended model configuration for specific use case."""
        return self.RECOMMENDED_MODELS.get(use_case, {})
    
    def estimate_cost(self, use_case: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate cost for using a specific model."""
        config = self.get_model_config(use_case)
        if not config:
            return 0.0
        
        costs = config.get('cost_per_million_tokens', {})
        input_cost = (input_tokens / 1_000_000) * costs.get('input', 0)
        output_cost = (output_tokens / 1_000_000) * costs.get('output', 0)
        
        return input_cost + output_cost
    
    def print_recommendations(self):
        """Print model recommendations for the crypto trading platform."""
        print("🤖 Alibaba Cloud Model Recommendations for Crypto Trading Platform")
        print("=" * 80)
        
        for use_case, config in self.RECOMMENDED_MODELS.items():
            print(f"\n📊 {use_case.replace('_', ' ').title()}:")
            print(f"   Model: {config['model']}")
            print(f"   Description: {config['description']}")
            print(f"   Use Case: {config['use_case']}")
            
            if 'context_length' in config:
                print(f"   Context Length: {config['context_length']:,} tokens")
            
            costs = config.get('cost_per_million_tokens', {})
            if costs:
                print(f"   Cost: ${costs.get('input', 0)}/M input, ${costs.get('output', 0)}/M output")
            
            features = config.get('features', [])
            if features:
                print(f"   Features: {', '.join(features)}")

# Global configuration instance
alibaba_config = AlibabaCloudConfig()

def test_connection():
    """Test connection to Alibaba Cloud DashScope."""
    try:
        # Simple test call
        from dashscope import Generation
        
        response = Generation.call(
            model='qwen-flash',
            prompt='Hello, this is a test connection.',
            max_tokens=10
        )
        
        if response.status_code == 200:
            print("✅ Successfully connected to Alibaba Cloud DashScope!")
            return True
        else:
            print(f"❌ Connection failed: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Print recommendations when run directly
    alibaba_config.print_recommendations()
    print("\n" + "=" * 80)
    print("💡 Recommendation Summary for Your Crypto Trading Platform:")
    print("   • Use qwen-plus for main AI investment advisor")
    print("   • Use qwen-flash for sentiment analysis (cost-effective)")
    print("   • Use qwen-max for complex market analysis")
    print("   • Use text-embedding-v4 for document similarity")
    print("\n🔧 Next steps:")
    print("   1. Add your DASHSCOPE_API_KEY to .env file")
    print("   2. Test connection with: python alibaba_cloud_config.py")
    print("   3. Start implementing AI features in your trading platform!")
