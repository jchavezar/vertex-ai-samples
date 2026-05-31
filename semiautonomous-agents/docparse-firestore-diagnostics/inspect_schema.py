from google.cloud import discoveryengine_v1beta as discoveryengine

try:
    req = discoveryengine.ConverseConversationRequest()
    print("ConverseConversationRequest fields (v1beta):")
    print(dir(req))
    # Also inspect Query or TextInput if they exist
    print("\nTextInput fields (v1beta):")
    try:
        ti = discoveryengine.TextInput()
        print(dir(ti))
    except Exception as e:
        print("TextInput error:", e)
except Exception as e:
    print("Error (v1beta):", e)

from google.cloud import discoveryengine_v1 as discoveryengine_v1
try:
    req = discoveryengine_v1.ConverseConversationRequest()
    print("\nConverseConversationRequest fields (v1):")
    print(dir(req))
except Exception as e:
    print("Error (v1):", e)
