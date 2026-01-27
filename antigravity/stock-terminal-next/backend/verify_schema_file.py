
import json
import os

try:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_tools_schema.json"))
    print(f"Checking file at: {path}")
    
    if not os.path.exists(path):
        print("FILE DOES NOT EXIST!")
        exit(1)
        
    with open(path, "r") as f:
        data = json.load(f)
        
    print(f"JSON Loaded. Found {len(data)} items.")
    
    found = False
    for item in data:
        if item.get("name") == "FactSet_EstimatesConsensus":
            found = True
            print("Found FactSet_EstimatesConsensus.")
            params = item.get("parameters", {}).get("properties", {})
            fpe = params.get("fiscalPeriodEnd")
            print(f"fiscalPeriodEnd: {fpe}")
            if fpe and "type" in fpe:
                print("SUCCESS: fiscalPeriodEnd has type.")
            else:
                print("FAILURE: fiscalPeriodEnd MISSING type!")
                
    if not found:
        print("FAILURE: FactSet_EstimatesConsensus NOT FOUND in schema file.")

except Exception as e:
    print(f"EXCEPTION: {e}")
