"""
Vector database service for semantic search and context retrieval.
Handles storing and retrieving knowledge for AI context enhancement.
"""
import chromadb
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    """
    Vector database service using ChromaDB for semantic search and knowledge storage.
    Stores project context, past decisions, and historical data for AI retrieval.
    """
    
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        
        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name=settings.VECTOR_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"Vector service initialized with collection: {settings.VECTOR_COLLECTION_NAME}")

    async def store_context(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        document_type: str = "general"
    ) -> str:
        """
        Store context in the vector database for future retrieval.
        
        Args:
            content: Text content to store
            metadata: Associated metadata (team_id, project_id, etc.)
            document_type: Type of document (standup, backlog, sprint, etc.)
            
        Returns:
            Document ID for the stored content
        """
        try:
            # Generate unique document ID
            doc_id = self._generate_doc_id(content, metadata)
            
            # Prepare metadata with type and timestamp
            full_metadata = {
                "type": document_type,
                "stored_at": datetime.now().isoformat(),
                **metadata
            }
            
            # Store in ChromaDB
            self.collection.add(
                documents=[content],
                metadatas=[full_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Stored {document_type} document with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            raise

    async def get_relevant_context(
        self, 
        query: str, 
        limit: int = 5,
        document_type: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Retrieve relevant context based on semantic similarity.
        
        Args:
            query: Query text for semantic search
            limit: Maximum number of results to return
            document_type: Filter by document type
            metadata_filter: Additional metadata filters
            
        Returns:
            List of relevant context strings
        """
        try:
            # Build where clause for filtering
            where_clause = {}
            if document_type:
                where_clause["type"] = document_type
            if metadata_filter:
                where_clause.update(metadata_filter)
            
            # Perform semantic search
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Extract documents from results
            if results and results['documents']:
                contexts = results['documents'][0]  # First query result
                logger.info(f"Retrieved {len(contexts)} relevant contexts for query")
                return contexts
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []

    async def store_standup_summary(
        self, 
        summary: str, 
        team_id: int, 
        date: datetime,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store standup summary for future reference."""
        metadata = {
            "team_id": team_id,
            "date": date.isoformat(),
            "source": "standup_summary"
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return await self.store_context(summary, metadata, "standup")

    async def store_backlog_insights(
        self, 
        insights: str, 
        project_id: int, 
        item_id: int,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store backlog analysis insights."""
        metadata = {
            "project_id": project_id,
            "item_id": item_id,
            "source": "backlog_analysis"
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return await self.store_context(insights, metadata, "backlog")

    async def store_sprint_decisions(
        self, 
        decisions: str, 
        sprint_id: int, 
        team_id: int,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store sprint planning decisions and reasoning."""
        metadata = {
            "sprint_id": sprint_id,
            "team_id": team_id,
            "source": "sprint_planning"
        }
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return await self.store_context(decisions, metadata, "sprint")

    async def get_team_context(self, team_id: int, limit: int = 10) -> List[str]:
        """Get recent context for a specific team."""
        return await self.get_relevant_context(
            query="team activities decisions blockers",
            limit=limit,
            metadata_filter={"team_id": team_id}
        )

    async def get_project_context(self, project_id: int, limit: int = 10) -> List[str]:
        """Get recent context for a specific project."""
        return await self.get_relevant_context(
            query="project backlog user stories requirements",
            limit=limit,
            metadata_filter={"project_id": project_id}
        )

    async def search_similar_stories(
        self, 
        story_content: str, 
        project_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar user stories for duplicate detection and reference.
        
        Returns list of similar stories with metadata.
        """
        try:
            metadata_filter = {"type": "backlog"}
            if project_id:
                metadata_filter["project_id"] = project_id
            
            results = self.collection.query(
                query_texts=[story_content],
                n_results=limit,
                where=metadata_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results or not results['documents']:
                return []
            
            # Combine documents with metadata and similarity scores
            similar_stories = []
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0
                similarity = 1.0 - distance  # Convert distance to similarity
                
                similar_stories.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity": similarity
                })
            
            return similar_stories
            
        except Exception as e:
            logger.error(f"Failed to search similar stories: {e}")
            return []

    async def cleanup_old_context(self, days_old: int = 90):
        """Remove context older than specified days to manage storage."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Note: ChromaDB doesn't have direct date filtering
            # This would require a more sophisticated approach
            # For now, we'll log the intent
            logger.info(f"Context cleanup requested for items older than {days_old} days")
            
            # In a production system, you might:
            # 1. Query all items
            # 2. Check stored_at timestamps
            # 3. Delete old items
            # 4. This could be done as a background task
            
        except Exception as e:
            logger.error(f"Failed to cleanup old context: {e}")

    def _generate_doc_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate a unique document ID based on content and metadata."""
        # Create a hash of content + key metadata for deduplication
        content_hash = hashlib.md5(content.encode()).hexdigest()
        metadata_keys = sorted(metadata.keys())
        metadata_str = "_".join(f"{k}:{metadata[k]}" for k in metadata_keys)
        metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()
        
        return f"{content_hash}_{metadata_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": settings.VECTOR_COLLECTION_NAME,
                "storage_path": settings.VECTOR_DB_PATH
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}

# Global vector service instance
vector_service = VectorService()