"""
FREE Text Embeddings using Hugging Face
Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging
from app.config import settings
logger = logging.getLogger(__name__)

class EmbeddingsService:
    """
    FREE embeddings service using Hugging Face models
    """
    
    def __init__(self):
        """
        Initialize the embedding model
        Downloads model on first run (one-time, ~90MB)
        """
        logger.info(f"🔄 Loading embedding model: {settings.EMBEDDING_MODEL}")
        
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self.dimension = 384  # all-MiniLM-L6-v2 dimension
            logger.info(f"✅ Embedding model loaded! Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text string
            
        Returns:
            List of floats (384 dimensions)
            
        Example:
            >>> embedder = EmbeddingsService()
            >>> vector = embedder.embed_text("Bitcoin is a cryptocurrency")
            >>> len(vector)
            384
        """
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Convert to list
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (efficient batching)
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing (default: 32)
            
        Returns:
            List of embeddings
            
        Example:
            >>> texts = ["Bitcoin", "Ethereum", "Solana"]
            >>> vectors = embedder.embed_batch(texts)
            >>> len(vectors)
            3
        """
        try:
            # Generate embeddings in batches
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert to list of lists
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"❌ Error generating batch embeddings: {e}")
            raise
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1, higher is more similar)
            
        Example:
            >>> similarity = embedder.get_similarity("Bitcoin", "BTC")
            >>> print(similarity)
            0.85
        """
        try:
            # Generate embeddings
            emb1 = np.array(self.embed_text(text1))
            emb2 = np.array(self.embed_text(text2))
            
            # Calculate cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {e}")
            raise
    
    def find_most_similar(self, query: str, texts: List[str], top_k: int = 3) -> List[dict]:
        """
        Find most similar texts to query
        
        Args:
            query: Query text
            texts: List of texts to compare
            top_k: Number of top results to return
            
        Returns:
            List of dicts with text and similarity score
            
        Example:
            >>> query = "cryptocurrency investment"
            >>> texts = ["Bitcoin trading", "Stock market", "Crypto portfolio"]
            >>> results = embedder.find_most_similar(query, texts, top_k=2)
            >>> print(results[0])
            {'text': 'Bitcoin trading', 'similarity': 0.82}
        """
        try:
            # Generate query embedding
            query_emb = np.array(self.embed_text(query))
            
            # Generate embeddings for all texts
            text_embs = np.array(self.embed_batch(texts))
            
            # Calculate similarities
            similarities = np.dot(text_embs, query_emb) / (
                np.linalg.norm(text_embs, axis=1) * np.linalg.norm(query_emb)
            )
            
            # Get top K indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Build results
            results = [
                {
                    "text": texts[idx],
                    "similarity": float(similarities[idx]),
                    "rank": i + 1
                }
                for i, idx in enumerate(top_indices)
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error finding similar texts: {e}")
            raise
    
    def embed_coin_analysis(self, coin_data: dict) -> List[float]:
        """
        Create embedding from coin analysis data
        Formats coin data into text for embedding
        
        Args:
            coin_data: Dictionary with coin information
            
        Returns:
            Embedding vector
            
        Example:
            >>> coin_data = {
            ...     "symbol": "BTC",
            ...     "name": "Bitcoin",
            ...     "risk_score": 3.2,
            ...     "trend": "bullish"
            ... }
            >>> vector = embedder.embed_coin_analysis(coin_data)
        """
        try:
            # Format coin data into analysis text
            analysis_text = f"""
            {coin_data.get('name', '')} ({coin_data.get('symbol', '')})
            Current Price: ${coin_data.get('price', 0):,.2f}
            24h Change: {coin_data.get('change_24h', 0):.2f}%
            Volume: ${coin_data.get('volume_24h', 0):,.0f}
            Risk Level: {coin_data.get('risk_level', 'unknown')}
            Risk Score: {coin_data.get('risk_score', 0):.2f}/10
            Volatility: {coin_data.get('volatility_score', 0):.2f}
            Liquidity: {coin_data.get('liquidity_score', 0):.2f}
            Trend: {coin_data.get('trend', 'neutral')}
            Market Cap Rank: {coin_data.get('market_cap_rank', 'N/A')}
            Sentiment: {coin_data.get('sentiment', 'neutral')}
            
            Analysis: {coin_data.get('analysis', 'Market analysis for this cryptocurrency.')}
            """
            
            # Generate embedding
            return self.embed_text(analysis_text.strip())
            
        except Exception as e:
            logger.error(f"❌ Error embedding coin analysis: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """
        Get information about the embedding model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": settings.EMBEDDING_MODEL,
            "dimension": self.dimension,
            "max_seq_length": self.model.max_seq_length,
            "cost": "FREE",
            "provider": "Hugging Face"
        }


# Create global instance
embeddings_service = EmbeddingsService()


# HELPER FUNCTIONS 

def embed_text(text: str) -> List[float]:
    """
    Quick function to embed text
    Uses global embeddings_service instance
    """
    return embeddings_service.embed_text(text)


def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Quick function to embed multiple texts
    """
    return embeddings_service.embed_batch(texts)


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Quick function to calculate similarity
    """
    return embeddings_service.get_similarity(text1, text2)


# TESTING 

if __name__ == "__main__":
    # Test embeddings
    print("=" * 60)
    print("Testing FREE Embeddings Service")
    print("=" * 60)
    
    # Initialize
    embedder = EmbeddingsService()
    print(f"\n✅ Model loaded: {embedder.get_model_info()}")
    
    # Test single embedding
    print("\n📝 Test 1: Single text embedding")
    text = "Bitcoin is a decentralized cryptocurrency"
    vector = embedder.embed_text(text)
    print(f"Text: {text}")
    print(f"Vector dimension: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
    
    # Test batch embedding
    print("\n📝 Test 2: Batch embedding")
    texts = ["Bitcoin", "Ethereum", "Solana"]
    vectors = embedder.embed_batch(texts)
    print(f"Texts: {texts}")
    print(f"Vectors generated: {len(vectors)}")
    
    # Test similarity
    print("\n📝 Test 3: Similarity calculation")
    sim = embedder.get_similarity("Bitcoin", "BTC")
    print(f"Similarity between 'Bitcoin' and 'BTC': {sim:.4f}")
    
    # Test coin analysis
    print("\n📝 Test 4: Coin analysis embedding")
    coin_data = {
        "symbol": "BTC",
        "name": "Bitcoin",
        "price": 37890,
        "change_24h": 2.5,
        "volume_24h": 28000000000,
        "risk_score": 3.2,
        "risk_level": "low",
        "trend": "bullish"
    }
    coin_vector = embedder.embed_coin_analysis(coin_data)
    print(f"Coin analysis vector dimension: {len(coin_vector)}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)