# backend/app/routers/documents.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.services.vector_store import vector_store

router = APIRouter()

@router.get("/")
async def get_user_documents(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get all documents for current user"""
    
    cursor = db.documents.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1)
    
    documents = await cursor.to_list(None)
    
    # Convert ObjectId to string
    for doc in documents:
        doc["id"] = doc["_id"]
        del doc["_id"]
    
    return documents

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get specific document"""
    
    document = await db.documents.find_one({
        "_id": document_id,
        "user_id": current_user["id"]
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document["id"] = document["_id"]
    del document["_id"]
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """Delete document"""
    
    document = await db.documents.find_one({
        "_id": document_id,
        "user_id": current_user["id"]
    })
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector store
    await vector_store.delete_document(document_id, db)
    
    # Delete chunks
    await db.chunks.delete_many({"document_id": document_id})
    
    # Delete document
    await db.documents.delete_one({"_id": document_id})
    
    return {"message": "Document deleted successfully"}