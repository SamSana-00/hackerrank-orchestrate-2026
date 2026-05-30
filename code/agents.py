import google.generativeai as genai
import os
import time
from corpus import find_relevant_docs

def create_client():
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    return model

def router_agent(client, issue, subject, company):
    prompt = f"""You are a support ticket router. Analyze this support ticket and determine:
1. Which company it belongs to (HackerRank, Claude, or Visa)
2. What type of request it is

Ticket Subject: {subject}
Ticket Issue: {issue}
Company provided: {company}

Rules:
- If company is provided and not "None", use that company
- If company is "None", figure it out from the issue content
- If the issue is completely irrelevant or nonsense, mark it as "invalid"

Respond in EXACTLY this format (no extra text):
COMPANY: [HackerRank/Claude/Visa/None]
REQUEST_TYPE: [product_issue/feature_request/bug/invalid]
PRODUCT_AREA: [brief area like "Account Access", "Billing", "Login", etc.]
"""
    time.sleep(3)
    response = client.generate_content(prompt)
    result_text = response.text.strip()
    lines = result_text.split("\n")
    result = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return {
        "company": result.get("COMPANY", company),
        "request_type": result.get("REQUEST_TYPE", "product_issue"),
        "product_area": result.get("PRODUCT_AREA", "general_support")
    }

def domain_agent(client, issue, company, corpus, product_area):
    relevant_docs = find_relevant_docs(corpus, company, issue)
    prompt = f"""You are a support specialist for {company}.
A customer has submitted the following support ticket:

ISSUE: {issue}
PRODUCT AREA: {product_area}

Here are the relevant support documents to help you answer:
---
{relevant_docs}
---

Rules:
- Answer ONLY based on the support documents provided above
- If the answer is not in the documents, say "I don't have enough information"
- Be helpful, clear and concise
- Do not make up policies or information not in the docs

Provide a helpful response to the customer:"""
    time.sleep(3)
    response = client.generate_content(prompt)
    return response.text.strip()

def safety_agent(client, issue, response, company):
    prompt = f"""You are a safety checker for customer support at {company}.

Review this support ticket and proposed response, then decide if we should:
- REPLY: Send the response to the customer (safe, grounded answer found)
- ESCALATE: Send to human agent (sensitive, risky, or no good answer)

TICKET: {issue}

PROPOSED RESPONSE: {response}

Escalate if the ticket involves:
- Fraud or suspicious activity
- Account hacking or security breach
- Legal threats or complaints
- Financial disputes over large amounts
- The response says "I don't have enough information"
- Malicious or harmful intent
- Extremely sensitive personal situations

Respond in EXACTLY this format:
STATUS: [replied/escalated]
JUSTIFICATION: [one sentence explanation]
"""
    time.sleep(3)
    response_obj = client.generate_content(prompt)
    response_text = response_obj.text.strip()
    lines = response_text.split("\n")
    result = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    status = result.get("STATUS", "escalated").lower()
    justification = result.get("JUSTIFICATION", "Requires human review")
    if status == "escalated":
        final_response = "This issue requires attention from our support team. A human agent will contact you shortly."
    else:
        final_response = response
    return {
        "status": status,
        "justification": justification,
        "response": final_response
    }

def process_ticket(client, corpus, issue, subject, company, log_file):
    print(f"\n🎫 Processing ticket...")
    print(f"   Issue: {issue[:80]}...")
    log_file.write(f"\n{'='*60}\n")
    log_file.write(f"TICKET:\nIssue: {issue}\nSubject: {subject}\nCompany: {company}\n")

    print("   🤖 Agent 1 (Router) working...")
    routing = router_agent(client, issue, subject, company)
    log_file.write(f"\nROUTER AGENT OUTPUT:\n{routing}\n")

    print("   🤖 Agent 2 (Domain Specialist) working...")
    draft_response = domain_agent(
        client, issue,
        routing["company"],
        corpus,
        routing["product_area"]
    )
    log_file.write(f"\nDOMAIN AGENT OUTPUT:\n{draft_response}\n")

    print("   🤖 Agent 3 (Safety Checker) working...")
    final = safety_agent(client, issue, draft_response, routing["company"])
    log_file.write(f"\nSAFETY AGENT OUTPUT:\n{final}\n")

    print(f"   ✅ Done! Status: {final['status']}")
    return {
        "status": final["status"],
        "product_area": routing["product_area"],
        "response": final["response"],
        "justification": final["justification"],
        "request_type": routing["request_type"]
    }