from method1_rag_answer import run_legacy_rag_answer
from method2_agentic_assist import run_agentic_assist

# Constructing a query that exceeds 5000 characters
base_instruction = "I am requesting a comprehensive and highly detailed analysis of the documents provided in the datastore. "
repeated_phrase = "Please ensure that the summary covers all major points, risk factors, financial highlights, and strategic initiatives mentioned in exhaustive detail. "
long_query = base_instruction + (repeated_phrase * 40)

if __name__ == "__main__":
    print(f"Constructed query length: {len(long_query)} characters")
    
    print("===========================================")
    print("--- Testing Method 1 (RAG Answer) ---")
    print("===========================================")
    try:
        run_legacy_rag_answer(long_query)
    except Exception as e:
        print(f"Exception during Method 1: {e}")

    print("===========================================")
    print("--- Testing Method 2 (Agentic Assist) ---")
    print("===========================================")
    try:
        run_agentic_assist(long_query)
    except Exception as e:
        print(f"Exception during Method 2: {e}")
