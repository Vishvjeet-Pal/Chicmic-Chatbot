from mcp.server.fastmcp import FastMCP
from langchain_ollama import OllamaEmbeddings
from vector_data import vector_store
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
from tools.expense import register_expense_tool
from tools.learningRD import register_learning_tool
from tools.meeting_task import register_meeting_tool
from tools.it_task import register_it_task_tool
from tools.presentation import register_presentation_tool
from tools.late_come import register_late_arrival_requests
from tools.manual_hours import register_manual_hour_requests
from tools.my_late_come import register_my_late_come_requests
from tools.employee_timesheet import register_timesheet_summary_tool
from tools.my_estimate_task import register_estimate_task
from tools.employee_manual import register_manual_hours_request_tool
from tools.sales_partener import register_sales_partner_tool
from tools.my_it_assets import register_user_assets
from tools.it_assets import register_asset_list
from tools.awards import register_award_list
from tools.recruitment_status import register_recruitment_report
from tools.screening_request import register_screening_request
from tools.all_users import register_organisation_users
from tools.human_resources import register_manage_resource
from tools.manage_roles import register_management_roles
from tools.management_designation import register_management_designations
from tools.management_permission import register_management_permission
from tools.management_skill import register_management_skills
from tools.project_approval import register_approval_project_list
from tools.upwork_list import register_management_upwork_ids
from tools.wfh_employees import register_wfh_list
from tools.relexation import register_relaxation_sheet
from tools.campus_placement import register_campus_placement_list
from tools.training_approved_course import register_training_course
from tools.trainee_list import register_training_trainee_list
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
register_expense_tool(mcp)
register_learning_tool(mcp)
register_meeting_tool(mcp)
register_it_task_tool(mcp)
register_presentation_tool(mcp)
register_late_arrival_requests(mcp)
register_manual_hour_requests(mcp)
register_my_late_come_requests(mcp)
register_timesheet_summary_tool(mcp)
register_estimate_task(mcp)
register_manual_hours_request_tool(mcp)
register_sales_partner_tool(mcp)
register_user_assets(mcp)
register_asset_list(mcp)
register_award_list(mcp)
register_recruitment_report(mcp)
register_screening_request(mcp)
register_wfh_list(mcp)
register_relaxation_sheet(mcp)
register_campus_placement_list(mcp)
register_training_course(mcp)
register_training_trainee_list(mcp)
register_organisation_users(mcp)
register_manage_resource(mcp)
register_management_roles(mcp)
register_management_designations(mcp)
register_management_skills(mcp)
register_management_permission(mcp)
register_approval_project_list(mcp)
register_management_upwork_ids(mcp)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
               

if __name__ == "__main__":
    mcp.run(transport="stdio")