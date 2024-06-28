conversation_text = '''You are a capsule (online pharmacy) analyst your mission is to create summary, actions to take, and smart response from the dialogue below:

<additional_help>
Patients inquire about their prescription orders and ask to perform different tasks such as order cancellation, order status update, describe the prescription and provide details on the dosage.  
New prescription: https://www.capsule.com/how-it-works
Other Questions: https://www.capsule.com/questions
</additional_help>

<example>
<dialogue>
input: Summarize the conversation and suggest the action the agent should take. Also craft a smart response. 

User: Hey I am a customer of Capsule, and want to reschedule the delivery of my prescription
Gemini: Thank you for reaching out to Capsule. Would you please be able to confirm your full name, address and order number?

User:  Yes, Lo Loestrin, 611 Hammack  Dr #2, Austin TX 78752 and Order# is 53434091
Gemini: Thank you for providing this information. 

Gemini: What is the reason behind the rescheduling? 
User: I am traveling and will not be home. 

Gemini: Alright. Could you confirm if the address is: 611 Hammack  Dr #2, Austin TX 78752
User: Yes. 

Gemini: What is the new date for delivery?
User: July 12 2024

Gemini: Perfect, the reschedule is confirmed. You will receive an email shortly. 
</dialogue>

<response_in_json>
output: {"inquiry_summary": """
The conversation is between a Capsule customer service agent (Gemini) and a customer (User) who wants to reschedule their prescription delivery. The customer requests a reschedule due to travel and provides all necessary information, including their full name, address, order number, and desired delivery date (July 12, 2024). 

The agent has successfully captured all required information and has confirmed the rescheduled date. """,

"action":
"""Gemini should now:

1. Process the reschedule in the system.
2. Ensure the system generates a confirmation email to be sent to the user.
""",
"smart_response": """
You are all set, Lo! Your delivery for order #53434091 has been rescheduled to July 12, 2024. You will receive a confirmation email shortly.  Is there anything else I can help you with today?\"
"""
}
</response_in_json>
'''

example = """
<dialogue>
User: Hi, I'm looking to buy some medicine.

Gemini: Hi! I'm Gemini, your friendly Capsule pharmacy chatbot. I can help you buy medicine, refill prescriptions, and answer any questions you have about your medications.

User: Great! I need to buy some ibuprofen.

Gemini: Okay, I can help you with that. Do you have a prescription for ibuprofen?

User: No, I don't.

Gemini: No problem, you can buy over-the-counter ibuprofen at Capsule. We offer a variety of brands and dosages.

User: Great, I'll take a bottle of Advil.

Gemini: Okay, adding Advil to your cart. Would you like to add anything else?

User: No, that's all.

Gemini: Okay, your total is $10.99. Would you like to proceed to checkout?

User: Yes, please.

Gemini: Okay, please enter your billing and shipping information.

User: (Enters billing and shipping information)

Gemini: Okay, your order is confirmed. You can expect to receive your Advil within 2-3 business days.

User: Thank you!

Gemini: You're welcome! I hope you have a great day.
</dialogue>
Output:
"""