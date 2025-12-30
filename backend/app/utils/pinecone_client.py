"""
Pinecone Vector Database Client
FREE tier: 100K vectors, 2M queries/month
For RAG system - semantic search
"""

from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)


class PineconeClient:
    """
    Pinecone vector database client for RAG system
    """
    
    def __init__(self):
        """Initialize Pinecone client"""
        logger.info("🔄 Initializing Pinecone client...")
        
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Get or create index
            self.index_name = settings.PINECONE_INDEX_NAME
            self._ensure_index_exists()
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            logger.info(f"✅ Pinecone initialized! Index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone: {e}")
            raise
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name not in existing_indexes:
                logger.info(f"📝 Creating new index: {self.index_name}")
                
                # Create index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.PINECONE_DIMENSION,
                    metric=settings.PINECONE_METRIC,
                    spec=ServerlessSpec(
                        cloud=settings.PINECONE_CLOUD,
                        region=settings.PINECONE_REGION
                    )
                )
                
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    logger.info("⏳ Waiting for index to be ready...")
                    time.sleep(1)
                
                logger.info(f"✅ Index created: {self.index_name}")
            else:
                logger.info(f"✅ Index already exists: {self.index_name}")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring index exists: {e}")
            raise
    
    def upsert(
        self,
        vectors: List[Dict],
        namespace: str = ""
    ) -> Dict:
        """
        Insert or update vectors
        
        Args:
            vectors: List of vector dictionaries with:
                - id: Unique identifier
                - values: Vector embedding (list of floats)
                - metadata: Additional data (dict)
            namespace: Optional namespace for organizing vectors
            
        Returns:
            Response with upserted count
            
        Example:
            >>> vectors = [{
            ...     "id": "BTC_12345",
            ...     "values": [0.1, 0.2, ...],  # 384 dimensions
            ...     "metadata": {
            ...         "symbol": "BTC",
            ...         "risk_score": 3.2,
            ...         "price": 37890
            ...     }
            ... }]
            >>> client.upsert(vectors)
        """
        try:
            response = self.index.upsert(
                vectors=vectors,
                namespace=namespace
            )
            
            logger.info(f"✅ Upserted {response['upserted_count']} vectors")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error upserting vectors: {e}")
            raise
    
    def query(
        self,
        vector: List[float],
        top_k: int = 5,
        namespace: str = "",
        filter: Optional[Dict] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Query similar vectors
        
        Args:
            vector: Query vector (384 dimensions)
            top_k: Number of results to return
            namespace: Namespace to search in
            filter: Metadata filter (e.g., {"risk_level": "low"})
            include_metadata: Include metadata in results
            
        Returns:
            List of matches with scores and metadata
            
        Example:
            >>> query_vector = embeddings.embed_text("low risk bitcoin")
            >>> results = client.query(query_vector, top_k=3)
            >>> for result in results:
            ...     print(f"{result['metadata']['symbol']}: {result['score']}")
        """
        try:
            response = self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata
            )
            
            matches = response.get('matches', [])
            
            # Format results
            results = []
            for match in matches:
                results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'metadata': match.get('metadata', {})
                })
            
            logger.info(f"📊 Found {len(results)} matches")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying vectors: {e}")
            raise
    
    def fetch(
        self,
        ids: List[str],
        namespace: str = ""
    ) -> Dict:
        """
        Fetch specific vectors by IDs
        
        Args:
            ids: List of vector IDs
            namespace: Namespace
            
        Returns:
            Dictionary of vectors
        """
        try:
            response = self.index.fetch(
                ids=ids,
                namespace=namespace
            )
            
            return response.get('vectors', {})
            
        except Exception as e:
            logger.error(f"❌ Error fetching vectors: {e}")
            raise
    
    def delete(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: str = "",
        filter: Optional[Dict] = None
    ) -> Dict:
        """
        Delete vectors
        
        Args:
            ids: Specific IDs to delete
            delete_all: Delete all vectors (use with caution!)
            namespace: Namespace
            filter: Metadata filter for deletion
            
        Returns:
            Response dictionary
        """
        try:
            if delete_all:
                logger.warning("⚠️ Deleting ALL vectors!")
                response = self.index.delete(delete_all=True, namespace=namespace)
            elif ids:
                response = self.index.delete(ids=ids, namespace=namespace)
            elif filter:
                response = self.index.delete(filter=filter, namespace=namespace)
            else:
                raise ValueError("Must provide ids, filter, or delete_all=True")
            
            logger.info("✅ Vectors deleted")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error deleting vectors: {e}")
            raise
    
    def get_stats(self, namespace: str = "") -> Dict:
        """
        Get index statistics
        
        Returns:
            Statistics including vector count, dimensions, etc.
        """
        try:
            stats = self.index.describe_index_stats()
            
            if namespace:
                ns_stats = stats.get('namespaces', {}).get(namespace, {})
                return ns_stats
            
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'namespaces': stats.get('namespaces', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            raise
    
    def list_namespaces(self) -> List[str]:
        """Get list of all namespaces"""
        try:
            stats = self.index.describe_index_stats()
            return list(stats.get('namespaces', {}).keys())
        except Exception as e:
            logger.error(f"❌ Error listing namespaces: {e}")
            return []


# Create global instance
pinecone_client = PineconeClient()


# ==================== HELPER FUNCTIONS ====================

def upsert_vectors(vectors: List[Dict], namespace: str = "") -> Dict:
    """Quick helper to upsert vectors"""
    return pinecone_client.upsert(vectors, namespace)


def query_vectors(
    vector: List[float],
    top_k: int = 5,
    filter: Optional[Dict] = None
) -> List[Dict]:
    """Quick helper to query vectors"""
    return pinecone_client.query(vector, top_k=top_k, filter=filter)


def get_index_stats() -> Dict:
    """Quick helper to get stats"""
    return pinecone_client.get_stats()


# ==================== TESTING ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Pinecone Client")
    print("=" * 60)
    
    client = PineconeClient()
    
    # Test 1: Get stats
    print("\n📊 Test 1: Index stats")
    stats = client.get_stats()
    print(f"Total vectors: {stats.get('total_vectors', 0)}")
    print(f"Dimension: {stats.get('dimension', 0)}")
    
    # Test 2: Upsert test vector
    print("\n📝 Test 2: Upsert test vector")
    test_vector = {
        "id": "test_btc_001",
        "values": [0.1] * 384,  # Dummy 384-dim vector
        "metadata": {
            "symbol": "BTC",
            "name": "Bitcoin",
            "risk_score": 3.2,
            "test": True
        }
    }
    
    result = client.upsert([test_vector])
    print(f"Upserted: {result.get('upserted_count', 0)} vectors")
    
    # Test 3: Query
    print("\n🔍 Test 3: Query similar vectors")
    query_vector = [0.1] * 384
    results = client.query(query_vector, top_k=3)
    
    for i, res in enumerate(results, 1):
        print(f"{i}. {res['metadata'].get('symbol', 'N/A')} - Score: {res['score']:.4f}")
    
    # Test 4: Delete test vector
    print("\n🗑️  Test 4: Delete test vector")
    client.delete(ids=["test_btc_001"])
    print("Test vector deleted")
    
    # Final stats
    print("\n📊 Final stats:")
    final_stats = client.get_stats()
    print(f"Total vectors: {final_stats.get('total_vectors', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)