"""
Vector Database Service for RAG (Retrieval-Augmented Generation)

This service manages the vector database for storing and retrieving contextual information
to enhance AI responses with project-specific knowledge.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorDBService:
    """Vector database service for contextual AI memory."""
    
    def __init__(self):
        """Initialize ChromaDB and sentence transformer."""
        self.client = None
        self.collection = None
        self.embedder = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector database and embedder."""
        try:
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="scrum_knowledge",
                metadata={"description": "AI Scrum Master knowledge base"}
            )
            
            # Initialize sentence transformer for embeddings
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Vector database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    def add_document(self, 
                    content: str, 
                    doc_type: str, 
                    metadata: Dict[str, Any] = None) -> str:
        """
        Add a document to the vector database.
        
        Args:
            content: The text content to store
            doc_type: Type of document (standup, ticket, retrospective, etc.)
            metadata: Additional metadata about the document
            
        Returns:
            Document ID
        """
        try:
            # Create chunks from the content
            texts = self.text_splitter.split_text(content)
            
            doc_id = f"{doc_type}_{datetime.now().isoformat()}"
            
            for i, text in enumerate(texts):
                chunk_id = f"{doc_id}_chunk_{i}"
                
                # Create embeddings
                embedding = self.embedder.encode(text).tolist()
                
                # Prepare metadata
                chunk_metadata = {
                    "doc_type": doc_type,
                    "chunk_index": i,
                    "timestamp": datetime.now().isoformat(),
                    "content_preview": text[:100] + "..." if len(text) > 100 else text
                }
                
                if metadata:
                    chunk_metadata.update(metadata)
                
                # Add to collection
                self.collection.add(
                    documents=[text],
                    embeddings=[embedding],
                    metadatas=[chunk_metadata],
                    ids=[chunk_id]
                )
            
            logger.info(f"Added document {doc_id} with {len(texts)} chunks")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    def search_similar(self, 
                      query: str, 
                      n_results: int = 5,
                      doc_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            doc_types: Filter by document types
            
        Returns:
            List of similar documents with metadata
        """
        try:
            # Create query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Prepare where clause for filtering
            where_clause = None
            if doc_types:
                where_clause = {"doc_type": {"$in": doc_types}}
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                    })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    def add_standup_summary(self, summary: str, date: str, team_id: str = None):
        """Add a standup summary to the knowledge base."""
        metadata = {
            "date": date,
            "team_id": team_id or "default"
        }
        return self.add_document(summary, "standup", metadata)
    
    def add_ticket_context(self, ticket_id: str, title: str, description: str, 
                          status: str = None, priority: str = None):
        """Add ticket information to the knowledge base."""
        content = f"Ticket {ticket_id}: {title}\n\nDescription: {description}"
        metadata = {
            "ticket_id": ticket_id,
            "title": title,
            "status": status,
            "priority": priority
        }
        return self.add_document(content, "ticket", metadata)
    
    def add_retrospective_notes(self, notes: str, sprint_id: str = None):
        """Add retrospective notes to the knowledge base."""
        metadata = {
            "sprint_id": sprint_id
        }
        return self.add_document(notes, "retrospective", metadata)
    
    def add_project_documentation(self, content: str, doc_name: str, doc_type: str = "documentation"):
        """Add project documentation to the knowledge base."""
        metadata = {
            "document_name": doc_name,
            "document_type": doc_type
        }
        return self.add_document(content, "documentation", metadata)
    
    def get_context_for_standup(self, query: str = None) -> str:
        """Get relevant context for standup generation."""
        search_query = query or "standup blockers progress"
        
        # Search for relevant standup history and ticket context
        results = self.search_similar(
            search_query, 
            n_results=5, 
            doc_types=["standup", "ticket"]
        )
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            if result['similarity'] > 0.7:  # Only include highly relevant results
                content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                context_parts.append(f"- {content_preview}")
        
        if context_parts:
            return "Previous context:\n" + "\n".join(context_parts)
        
        return ""
    
    def get_context_for_planning(self, backlog_items: List[str] = None) -> str:
        """Get relevant context for sprint planning."""
        search_query = "sprint planning velocity capacity estimation"
        
        results = self.search_similar(
            search_query, 
            n_results=5, 
            doc_types=["retrospective", "ticket", "standup"]
        )
        
        if not results:
            return ""
        
        context_parts = []
        for result in results:
            if result['similarity'] > 0.6:
                context_parts.append(result['content'][:150] + "...")
        
        if context_parts:
            return "Historical context:\n" + "\n".join(context_parts)
        
        return ""
    
    def get_backlog_context(self, ticket_title: str, description: str) -> str:
        """Get context for backlog item analysis."""
        search_query = f"{ticket_title} {description}"
        
        results = self.search_similar(
            search_query, 
            n_results=3, 
            doc_types=["ticket", "documentation"]
        )
        
        context_parts = []
        for result in results:
            if result['similarity'] > 0.5:
                metadata = result.get('metadata', {})
                if metadata.get('ticket_id'):
                    context_parts.append(f"Similar ticket {metadata['ticket_id']}: {result['content'][:100]}...")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the vector database."""
        try:
            count = self.collection.count()
            return {
                "status": "healthy",
                "document_count": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global instance
vector_db = VectorDBService()