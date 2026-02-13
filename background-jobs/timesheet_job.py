import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ingest.timesheet_ingest import ingest_timesheets


def main():
    try:
        print("⏳ Running Timesheet ingestion job...")
        ingest_timesheets()
        print("✅ Timesheets ingestion completed")

    except Exception as e:
        print("❌ Timesheet job failed:", e)


if __name__ == "__main__":
    main()
