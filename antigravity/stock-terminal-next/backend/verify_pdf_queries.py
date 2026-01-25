import requests
import json
import time

url = "http://localhost:8085/search/analyze-pdf"
# Test ESG PDF
pdf_url = "https://www.factset.com/hubfs/Landing%20Page%20Images%20+%20Files/Paper_Stock%20Price%20Reactions%20to%20ESG%20News%20The%20Role%20of%20ESG%20Ratings%20and%20Disagreement.pdf"

queries = [
    "How many unique firm-day observations were included in the final sample of the study on stock price reactions to ESG news?",
    "What was the timeframe for the ESG news observations analyzed in the paper?",
    "According to the paper, what is the scale used by TruValue Labs for ESG news scores, and what score represents a neutral impact?"
]

for q in queries:
    print(f"\n--- Query: {q} ---")
    try:
        # Increase timeout heavily because PDF is large
        with requests.post(url, json={"url": pdf_url, "query": q}, stream=True, timeout=60) as r:
            for line in r.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "text" in data:
                            # Accumulate text to see full format
                            print(data["text"], end="", flush=True)
                        elif "error" in data:
                            print(f"\n[API ERROR]: {data['error']}")
                    except Exception as json_err:
                        print(f"\n[JSON ERROR]: {json_err} line: {line}")
            print("\n") # Newline after stream ends
    except Exception as e:
        print(f"[REQUEST FAILED]: {e}")
    print("\n--------------------------")
