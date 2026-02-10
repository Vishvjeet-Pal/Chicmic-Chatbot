# mcp_server.py
from mcp.server.fastmcp import FastMCP
from sqlalchemy.future import select
from database import AsyncSessionLocal
from models import FAQ, Policy

mcp = FastMCP("Company Assistant")

@mcp.tool()
async def search_faq(keyword: str) -> str:
    """Search for frequently asked questions by a keyword."""
    async with AsyncSessionLocal() as session:
        query = select(FAQ).where(FAQ.question.contains(keyword))
        result = await session.execute(query)
        faqs = result.scalars().all()
        
        if not faqs:
            return "No matching FAQs found."
        return "\n".join([f"Q: {f.question} | A: {f.answer}" for f in faqs])

@mcp.tool()
async def get_policy_by_category(category: str) -> str:
    """Retrieve all university policies within a specific category (e.g., 'Academic', 'Hostel')."""
    async with AsyncSessionLocal() as session:
        query = select(Policy).where(Policy.category == category)
        result = await session.execute(query)
        policies = result.scalars().all()
        
        if not policies:
            return f"No policies found in category: {category}"
        return "\n".join([f"Title: {p.title}\nDesc: {p.description}" for p in policies])