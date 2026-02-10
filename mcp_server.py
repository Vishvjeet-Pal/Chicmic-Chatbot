# # mcp_server.py
# from fastmcp import FastMCP
# from sqlalchemy.future import select
# from database import SessionLocal
# from models import FAQ, Policy

# mcp = FastMCP("Company Assistant")

# @mcp.tool()
# async def search_faq(keyword: str) -> str:
#     """Search for frequently asked questions by a keyword."""
#     async with AsyncSessionLocal() as session:
#         query = select(FAQ).where(FAQ.question.contains(keyword))
#         result = await session.execute(query)
#         faqs = result.scalars().all()
        
#         if not faqs:
#             return "No matching FAQs found."
#         return "\n".join([f"Q: {f.question} | A: {f.answer}" for f in faqs])

# @mcp.tool()
# async def get_policy_by_category(category: str) -> str:
#     """Retrieve all university policies within a specific category (e.g., 'Academic', 'Hostel')."""
#     async with AsyncSessionLocal() as session:
#         query = select(Policy).where(Policy.category == category)
#         result = await session.execute(query)
#         policies = result.scalars().all()
        
#         if not policies:
#             return f"No policies found in category: {category}"
#         return "\n".join([f"Title: {p.title}\nDesc: {p.description}" for p in policies])



# mcp_server.py
from fastmcp import FastMCP
from sqlalchemy import select
from database import SessionLocal
from models.faq import FAQ
from models.policy import Policy

mcp = FastMCP("Company Assistant")


@mcp.tool()
def search_faq(keyword: str) -> str:
    """Search for frequently asked questions by a keyword."""
    session = SessionLocal()
    try:
        query = select(FAQ).where(FAQ.question.contains(keyword))
        result = session.execute(query)
        faqs = result.scalars().all()

        if not faqs:
            return "No matching FAQs found."

        return "\n".join([f"Q: {f.question} | A: {f.answer}" for f in faqs])

    finally:
        session.close()


@mcp.tool()
def get_policy_by_category(category: str) -> str:
    """Retrieve policies by category."""
    session = SessionLocal()
    try:
        query = select(Policy).where(Policy.category == category)
        result = session.execute(query)
        policies = result.scalars().all()

        if not policies:
            return f"No policies found in category: {category}"

        return "\n".join([
            f"Title: {p.title}\nDesc: {p.description}"
            for p in policies
        ])

    finally:
        session.close()
