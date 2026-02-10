from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Policy, FAQ  # Assuming your models are in models.py

# Ensure tables are created
# Base.metadata.create_all(bind=engine)

def seed_data():
    db: Session = SessionLocal()
    try:
        # 1. Add Policies
        policies = [
            Policy(title="Referral Policy", category="referral", description="To refer a potential employee, an employee shall email the detail of the position applied for and submit to HR along with the resume of the candidate. Employees shall be eligible for a referral award only when the referred candidate has not applied to the organization through direct channels and has not given an interview in the last one year. For each referral hiring, the organization shall pay the referral incentive as per the Schedule 1 published by HR via email for open positions from time to time. The referral incentive payout shall be uniform, irrespective of the role/level of the referee. The referral incentive payment shall happen only when the newly hired employee has worked at least 90 days in the organization and his/her probation is confirmed. If more than one employee refers to the same candidate, the first referee shall receive the referral incentive."),
            Policy(title="Leave Policy", category="leave", description="Confirmed employees can take 16 days leave per annum. Trainees/Consultants can take 1 leave per month."),
            Policy(title="Travel Policy", category="Finance", description="Reimbursement rules for business trips.")
        ]
        
        # 2. Add FAQs
        faqs = [
            FAQ(question="How do I reset my password?", answer="Go to settings and click 'Reset Password'."),
            FAQ(question="What are office hours?", answer="9 AM to 6 PM, Monday to Friday.")
        ]

        # Use add_all to insert multiple objects at once
        db.add_all(policies)
        db.add_all(faqs)
        
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