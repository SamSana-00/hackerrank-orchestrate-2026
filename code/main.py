import os
import pandas as pd
from dotenv import load_dotenv
from corpus import load_corpus
from agents import process_ticket, create_client

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")
TICKETS_PATH = os.path.join(BASE_DIR, "support_tickets", "support_tickets.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "support_tickets", "output.csv")
LOG_PATH = os.path.join(BASE_DIR, "support_tickets", "log.txt")

def main():
    print("🚀 Starting Multi-Domain Support Triage Agent")
    print("="*60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: No Gemini API key found! Check your .env file")
        return

    client = create_client()
    print("✅ Gemini AI client ready!")

    print("\n📚 Loading support corpus...")
    corpus = load_corpus(DATA_PATH)
    print("✅ All documents loaded!")

    print("\n📋 Loading support tickets...")
    df = pd.read_csv(TICKETS_PATH)
    print(f"✅ Found {len(df)} tickets to process!")

    print("\n🤖 Starting ticket processing...")
    print("="*60)

    results = []

    with open(LOG_PATH, "w", encoding="utf-8") as log_file:
        log_file.write("SUPPORT TRIAGE AGENT - CHAT TRANSCRIPT\n")
        log_file.write("="*60 + "\n")

        for index, row in df.iterrows():
            issue = str(row.get("Issue", ""))
            subject = str(row.get("Subject", ""))
            company = str(row.get("Company", "None"))

            try:
                result = process_ticket(
                    client=client,
                    corpus=corpus,
                    issue=issue,
                    subject=subject,
                    company=company,
                    log_file=log_file
                )
                results.append(result)

            except Exception as e:
                print(f"   ⚠️ Error on ticket {index}: {e}")
                results.append({
                    "status": "escalated",
                    "product_area": "general_support",
                    "response": "Unable to process. Escalating to human agent.",
                    "justification": f"Processing error: {str(e)}",
                    "request_type": "product_issue"
                })

            print(f"   Progress: {index+1}/{len(df)} tickets done")

    print("\n💾 Saving results...")
    results_df = pd.DataFrame(results)

    df["Response"] = results_df["response"]
    df["Product Area"] = results_df["product_area"]
    df["Status"] = results_df["status"].str.capitalize()
    df["Request Type"] = results_df["request_type"]
    df["Justification"] = results_df["justification"]

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Results saved to: {OUTPUT_PATH}")
    print(f"✅ Log saved to: {LOG_PATH}")
    print("\n🎉 ALL DONE! Your solution is ready to submit!")

if __name__ == "__main__":
    main()