import os

def load_corpus(data_path):
    """
    Loads all support documents from the data folder.
    Returns a dictionary with company name as key and docs as value.
    """
    corpus = {
        "HackerRank": "",
        "Claude": "",
        "Visa": ""
    }

    companies = {
        "HackerRank": "hackerrank",
        "Claude": "claude",
        "Visa": "visa"
    }

    for company, folder in companies.items():
        company_path = os.path.join(data_path, folder)
        all_text = []

        # Walk through all files in the folder
        for root, dirs, files in os.walk(company_path):
            for file in files:
                if file.endswith(".md") or file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            all_text.append(content)
                    except:
                        pass

        corpus[company] = "\n\n".join(all_text)
        print(f"✅ Loaded {company} corpus: {len(corpus[company])} characters")

    return corpus


def find_relevant_docs(corpus, company, issue, max_chars=3000):
    """
    Finds the most relevant part of docs for a given issue.
    Simple keyword matching approach.
    """
    if company not in corpus:
        # If company is None or unknown, search all
        all_docs = "\n\n".join(corpus.values())
    else:
        all_docs = corpus[company]

    # Split into chunks and find most relevant
    words = issue.lower().split()
    lines = all_docs.split("\n")

    scored_lines = []
    for i, line in enumerate(lines):
        score = sum(1 for word in words if word in line.lower())
        if score > 0:
            scored_lines.append((score, i, line))

    # Sort by score
    scored_lines.sort(reverse=True)

    # Get top relevant lines with context
    relevant = []
    seen_indices = set()
    for score, idx, line in scored_lines[:20]:
        for j in range(max(0, idx-2), min(len(lines), idx+3)):
            if j not in seen_indices:
                relevant.append(lines[j])
                seen_indices.add(j)

    result = "\n".join(relevant)
    return result[:max_chars] if result else all_docs[:max_chars]