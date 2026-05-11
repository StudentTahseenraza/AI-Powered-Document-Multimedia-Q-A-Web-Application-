# backend/app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    client = None
    db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to MongoDB"""
        if self.client is None:
            try:
                self.client = AsyncIOMotorClient(settings.MONGODB_URL)
                self.db = self.client[settings.MONGODB_DB_NAME]
                
                # Test connection
                await self.client.admin.command('ping')
                logger.info("✅ Connected to MongoDB successfully!")
                
                await self.create_indexes()
                
            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {str(e)}")
                raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")
    
    async def create_indexes(self):
        """Create indexes for better performance"""
        try:
            if self.db is not None:
                await self.db.users.create_index("email", unique=True)
                await self.db.users.create_index("created_at")
                await self.db.documents.create_index("user_id")
                await self.db.documents.create_index("created_at")
                await self.db.chunks.create_index("document_id")
                await self.db.chat_history.create_index("user_id")
                await self.db.chat_history.create_index("document_id")
                logger.info("✅ MongoDB indexes created")
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")
    
    def get_db(self):
        """Get database instance"""
        return self.db

# Global instance
mongodb = MongoDB()

async def connect_to_mongo():
    await mongodb.connect()

async def close_mongo_connection():
    await mongodb.close()

def get_db():
    """Dependency to get database"""
    return mongodb.get_db()