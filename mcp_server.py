from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
import os
import httpx
from vector_data import vector_store
from datetime import datetime, timedelta, timezone
from tools.attendance import register_attendance
from tools.holidays import register_holidays
from tools.project_details import register_project
from tools.punch_in_out import register_punch_tool
from tools.referral_policy import register_referral
from tools.search_policy import register_search_policy
from tools.time_spent import register_time_spent
from tools.timesheet import register_timesheet
from tools.tracker_details import register_tracker_details
from tools.user_leaves import register_user_leaves
from tools.user_profile import register_user_profile
from tools.trainee_course import register_trainee_course
from tools.event_history import register_event_history
from tools.leave_application import register_leave_application


mcp = FastMCP("Company Assistant")

register_user_profile(mcp)
register_attendance(mcp)
register_holidays(mcp,vector_store)
register_punch_tool(mcp)
register_referral(mcp,vector_store)
register_search_policy(mcp,vector_store)
register_project(mcp)
register_time_spent(mcp)
register_timesheet(mcp)
register_tracker_details(mcp)
register_user_leaves(mcp)
register_trainee_course(mcp)
register_event_history(mcp)
register_leave_application(mcp)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
               

if __name__ == "__main__":
    mcp.run(transport="stdio")