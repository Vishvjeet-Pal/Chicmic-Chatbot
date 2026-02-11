# index_data.py
import asyncio
from database import AsyncSessionLocal
from models.policy import Policy
from models.login import Login
from models.personal_info import PersonalInfo
from sqlalchemy.future import select
from langchain_core.documents import Document
from mcp_server import vector_store

async def index_all():
    async with AsyncSessionLocal() as session:
        # Index FAQs
        personal_info_faqs = (await session.execute(select(PersonalInfo))).scalars().all()
        personal_faq_docs = [
            Document(
                page_content=f.answer, 
                metadata={"type":"personal_info","category": f.category, "question": f.question}
            ) for f in personal_info_faqs
        ]
        
        login_credentials_faqs = (await session.execute(select(Login))).scalars().all()
        login_faq_docs = [
            Document(
                page_content=f.answer, 
                metadata={"type":"login","category": f.category, "question": f.question}
            ) for f in login_credentials_faqs
        ]
        

        # Index Policies
        policies = (await session.execute(select(Policy))).scalars().all()
        policy_docs = [
            Document(
                page_content=p.description, 
                metadata={"type": "policy", "title": p.title, "category": p.category}
            ) for p in policies
        ]
        for p in policies:
            print(f"Title: {p.title}, Description: {p.description}, Category: {p.category}")
        # Add to Chroma

        if personal_faq_docs or policy_docs or login_faq_docs:
            vector_store.add_documents(login_faq_docs+personal_faq_docs + policy_docs)
            print(f"Indexed {len(login_faq_docs)} login FAQs, {len(personal_faq_docs)} personal info FAQs, and {len(policy_docs)} policies to Vector Store.")
            print("Successfully indexed all data to Vector Store!")

if __name__ == "__main__":
    asyncio.run(index_all())