import requests
import json
import os

def get_model_slugs():
    url = 'https://openrouter.ai/api/v1/models'
    print(f"Fetching models from {url}...")
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        
        # Check structure
        if "data" not in data:
            print("Error: 'data' field not found in response")
            return []
            
        models = []
        for item in data["data"]:
            if "id" in item:
                # Calculate Booleans
                modality = item.get("architecture", {}).get("modality", "")
                supported_params = item.get("supported_parameters", [])
                
                supports_vision = True if "image" in modality else False
                supports_tools = True if "tools" in supported_params else False
                supports_structured_output = True if "response_format" in supported_params else False
                supports_reasoning = True if "include_reasoning" in supported_params else False
                
                top_provider = item.get("top_provider", {})
                max_completion_tokens = top_provider.get("max_completion_tokens") if isinstance(top_provider, dict) else None
                
                models.append({
                    "id": item["id"],
                    "name": item.get("name"),
                    "context_length": item.get("context_length"),
                    "pricing_prompt": item.get("pricing", {}).get("prompt"),
                    "pricing_completion": item.get("pricing", {}).get("completion"),
                    "modality": modality,
                    "max_completion_tokens": max_completion_tokens,
                    "supports_vision": supports_vision,
                    "supports_tools": supports_tools,
                    "supports_structured_output": supports_structured_output,
                    "supports_reasoning": supports_reasoning
                })

                
        print(f"Found {len(models)} models with full metadata.")
        
        # Save to file for caching/reference
        output_path = "models.json"
        with open(output_path, "w") as f:
            json.dump(models, f, indent=2)
        print(f"Saved populated model metadata list to {output_path}")
        return models

        
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

if __name__ == "__main__":
    slugs = get_model_slugs()
    # Print first 5
    print("\nSample Models:")
    for slug in slugs[:5]:
        print(f" - {slug}")
