# MY_BUILD.md — How I Built This

This document explains my thought process, decisions, and challenges while building this project for HackerRank Orchestrate May 2026.

---

## My Approach

When I read the problem statement, I had two choices — build a simple single agent or a multi-agent pipeline. I chose the multi-agent approach because separation of concerns makes each part more reliable and the architecture is easier to explain and debug.

The idea: instead of one agent trying to classify, search, answer, and safety-check all at once, I split those responsibilities into three focused agents.

---

## Agent Design Decisions

**Router Agent**
The first challenge was handling tickets where `company = None`. Rather than defaulting to a fixed company, I pass the issue content to the Router and let it infer the company from context. This handles edge cases like a user asking about HackerRank without mentioning the company name.

**Domain Specialist Agent**
I used keyword-based RAG instead of vector embeddings. For this corpus size and time constraint, keyword matching was fast, interpretable, and effective enough. The agent is strictly instructed to answer only from retrieved docs — if the answer isn't there, it says so honestly.

**Safety Agent**
The safety layer was important to prevent the system from confidently answering sensitive or risky tickets. The escalation triggers (fraud, hacking, legal, no answer found) were designed based on real support team escalation patterns.

---

## Tech Choices

- **Gemini API (free tier)** — I originally planned to use Claude API but hit credit limits as a student. Switched to Google Gemini which has a generous free tier.
- **Rate limiting handled** — Added `time.sleep(3)` between API calls to respect free tier limits.
- **python-dotenv** — API key is stored in `.env` file and never hardcoded, keeping it safe.

---

## Challenges

1. **API credits** — Ran out of Anthropic API credits early. Switching to Gemini mid-hackathon required rewriting the agent calls.
2. **Rate limits** — Free tier limits caused processing delays. Added sleep delays to handle gracefully.
3. **VIM editor** — Git's default editor opened during merge and caused confusion. Added `core.editor = notepad` to git config after.

---

## What I Would Improve

- Replace keyword matching with proper vector embeddings (e.g. sentence-transformers) for better retrieval accuracy
- Add confidence scoring so the system knows how certain it is
- Fine-tune escalation rules using the sample data as training signal
- Add retry logic with exponential backoff for rate limit errors

---

## What I Learned

This was my first time building an AI agent system. Key learnings:

- How multi-agent pipelines work in practice
- What RAG (Retrieval Augmented Generation) actually means when implemented
- How to make API calls from Python
- How to handle real-world constraints like rate limits and missing data
- That shipping something working under time pressure teaches more than any tutorial
