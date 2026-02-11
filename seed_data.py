from sqlalchemy.orm import Session
from database import AsyncSessionLocal, engine_sync, Base, SessionLocal
from models.policy import Policy
from models.login import Login
from models.personal_info import PersonalInfo
# Ensure tables are created
Base.metadata.create_all(bind=engine_sync)

def seed_data():
    db: Session = SessionLocal()
    try:
        # 1. Add Policies
        policies = [
            Policy(title="Referral Policy", category="referral", description="To refer a potential employee, an employee shall email the detail of the position applied for and submit to HR along with the resume of the candidate. Employees shall be eligible for a referral award only when the referred candidate has not applied to the organization through direct channels and has not given an interview in the last one year. For each referral hiring, the organization shall pay the referral incentive as per the Schedule 1 published by HR via email for open positions from time to time. The referral incentive payout shall be uniform, irrespective of the role/level of the referee. The referral incentive payment shall happen only when the newly hired employee has worked at least 90 days in the organization and his/her probation is confirmed. If more than one employee refers to the same candidate, the first referee shall receive the referral incentive."),
            Policy(title="Leave Policy", category="leave", description="Confirmed employees can take 16 days leave per annum. Trainees/Consultants can take 1 leave per month."),
            Policy(title="Travel Policy", category="Finance", description="Reimbursement rules for business trips."),
            Policy(title="Casual/Sick Leave", category="leave", description="Sick Leave policy of employee: 7 days per year on a use-or-lose basis. Unused leaves lapse at the end of the year with no carry forward, encashment, or payout upon separation from employment."),

Policy(title="Earned Leave", category="leave", description="9 days paid leave per year. Leave must be availed or encashed by the end of the calendar year. Company encourages employees to take time off instead of opting for payouts."),

Policy(title="Company Holidays", category="leave", description="10 official company holidays observed annually in addition to Casual, Sick, and Earned Leave. Holidays are declared at the beginning of each year as per Government of India holiday calendar."),

Policy(title="Compensatory Leave", category="leave", description="Granted when an employee works at least 8 hours on a holiday. Approval from Team Lead/PM is required via ERP within one week. Work must be recorded using an approved tracker and submitted through ERP. Leave is granted at management discretion."),

Policy(title="Leave Calculation Process", category="leave", description="Leave year runs from January 1 to December 31. Leave is credited annually and calculated on a pro-rata basis for employees joining or leaving mid-year. Excess leave taken beyond entitlement must be repaid to the company. Sandwich policy applies where weekends and holidays between leaves are counted as leave. One weekend waiver per year is allowed for confirmed employees. 5+2 rule applies when leave is taken for a full workweek."),

Policy(title="Leave During Probation", category="leave", description="If an employee leaves before completing six months (180 days of presence), earned leaves taken will be deducted from the final settlement. Leave is not encashable or adjustable against notice period during probation."),

Policy(title="Leave for Members on Training", category="leave", description="Employees on training are entitled to 1 leave per month. Leave cannot be carried forward or encashed. Any extra leave taken will extend the confirmation date by the same duration."),

Policy(title="Leave Application Process", category="leave", description="All leave must be applied and approved through ERP only. Immediate Supervisor/Manager recommends leave. Leave of 4 or more days requires Director/Founder or reporting manager approval. Unapproved absence is treated as Leave Without Pay. Employees must follow office hours and maintain personal leave records."),

Policy(title="Maternity Leave", category="leave", description="Confirmed female employees are eligible for maternity leave as per the Maternity Benefit Act 1961 and applicable amendments. This benefit is not available during probation."),

Policy(title="Leave Encashment Policy", category="leave", description="Only unused Earned Leave balance is encashable at the end of the calendar year or at separation. Encashment is calculated based on basic salary and prorated if salary changes during the year.")

        ]
        
        # 2. Add FAQs
        # faqs = [
        #     FAQ(question="How do I reset my password?", answer="Go to settings and click 'Reset Password'."),
        #     FAQ(question="What are office hours?", answer="9 AM to 6 PM, Monday to Friday.")
        # ]

        login_credentials_faqs = [
            Login(category="credentials", question="How do I access the company email?", answer="Use your employee ID and default password to log in at mail.company.com."),
            Login(category="credentials", question="What if I forget my ERP password?", answer="Click on 'Forgot Password' on the ERP login page and follow the instructions to reset it.")
        ]

        personal_info_faqs = [
            PersonalInfo(question="How can I access my personal and official information in the ERP system?", answer="To access your personal and official information, go to the 'My Profile' section in the ERP system. This section allows you to view and manage your details.", category="personal_info"),

            PersonalInfo(question="How do I edit my personal information in the ERP system?", answer="You can edit your personal information by clicking on the 'Edit' button within the 'My Profile' section. This allows you to update details such as your personal email address, contact number, temporary and permanent address, and emergency contact information.", category="personal_info"),

            PersonalInfo(question="What personal information can I edit in the 'My Profile' section?", answer="In the 'My Profile' section, you can edit the following details: Personal Email Address, Contact Number, Temporary Address, Permanent Address, and Emergency Contact Information.", category="personal_info")

        ]

        # Use add_all to insert multiple objects at once
        db.add_all(policies)
        db.add_all(login_credentials_faqs)
        db.add_all(personal_info_faqs)
        
        # Commit to save changes to the database
        db.commit()
        print("Data successfully inserted!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback() # Undo changes if something goes wrong
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()