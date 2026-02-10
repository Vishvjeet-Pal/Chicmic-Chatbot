# index_data.py
import asyncio
from database import AsyncSessionLocal
from models import FAQ, Policy
from sqlalchemy.future import select
from langchain_core.documents import Document
from mcp_server import vector_store

async def index_all():
    async with AsyncSessionLocal() as session:
        # Index FAQs
        faqs = (await session.execute(select(FAQ))).scalars().all()
        faq_docs = [
            Document(
                page_content=f.answer, 
                metadata={"type": "faq", "question": f.question}
            ) for f in faqs
        ]
        
        # Index Policies
        policies = (await session.execute(select(Policy))).scalars().all()
        policy_docs = [
            Document(
                page_content=p.description, 
                metadata={"type": "policy", "title": p.title, "category": p.category}
            ) for p in policies
        ]
        
        # Add to Chroma
        if faq_docs or policy_docs:
            vector_store.add_documents(faq_docs + policy_docs)
            print("Successfully indexed all data to Vector Store!")

if __name__ == "__main__":
    asyncio.run(index_all())