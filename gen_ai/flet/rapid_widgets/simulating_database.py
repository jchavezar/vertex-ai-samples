database = [
    {
        'name': 'John Doe',
        'address': '123 Main Street',
        'mobile phone': '555-123-4567',
        'order id': '12345',
        'medicine': 'Tylenol',
        'full dialog': "Agent: Hello, thank you for calling [Pharmacy Name], this is [Agent name] speaking. How can I help you?\nCustomer: Hi, I'd like to check on my order status please\nAgent: Sure, can I get your order ID?\nCustomer: It's 12345\nAgent: Thanks. Could you also confirm your name and address please?\nCustomer: It's John Doe, and my address is 123 Main Street.\nAgent: Okay, John Doe, 123 Main Street. One moment please. Okay, your order for Tylenol is confirmed and will be delivered within 2 business days.\nCustomer: Great, thank you\nAgent: No problem. Is there anything else I can help you with?\nCustomer: No, that's all, thanks again.\nAgent: Have a great day, bye."},
    {
        'name': 'Jane Smith',
        'address': '456 Oak Avenue',
        'mobile phone': '555-987-6543',
        'order id': '67890',
        'medicine': 'Advil',
        'full dialog': "Agent: Hello, thank you for calling [Pharmacy Name].\nCustomer: Hi, I want to order some Advil\nAgent: No problem. Can I first get your name and address?\nCustomer: It's Jane Smith, and my address is 456 Oak Avenue\nAgent: Ok, and your phone number for this order?\nCustomer: It's 555-987-6543\nAgent: And how many Advil do you need?\nCustomer: One pack, please\nAgent: Okay, your order ID is 67890. We'll send you a confirmation message with the delivery details shortly. Anything else?\nCustomer: That's all, thanks.\nAgent: Thank you for your order. Have a nice day."},
    {
        'name': 'David Lee',
        'address': '789 Pine Street',
        'mobile phone': '555-567-8901',
        'order id': '24680',
        'medicine': 'Claritin',
        'full dialog': "Agent: Hello, [Pharmacy name], how can I assist you today?\nCustomer: I placed an order yesterday and I haven't received a confirmation yet\nAgent: I'd be happy to look into that for you. Could you please provide your order ID and name?\nCustomer: Sure, it's 24680, David Lee\nAgent: One moment please...Okay, I found your order for Claritin. It looks like there was an issue with your mobile number on file. What's the correct number so we can update that and resend the confirmation?\nCustomer: Oh, I see. It's 555-567-8901\nAgent: Okay, I've updated your information and resent the confirmation to 555-567-8901. You should receive it shortly. Do you have any other questions?\nCustomer: No, that's great, thank you for your help!\nAgent: No problem at all, Mr. Lee. Have a good day!"},
    {
        'name': 'Sarah Kim',
        'address': '1011 Willow Lane',
        'mobile phone': '555-234-5678',
        'order id': '13579',
        'medicine': 'Zyrtec',
        'full dialog': "Agent: Thank you for calling [Pharmacy Name], how may I help you?\nCustomer: Hi, I need to order some allergy medicine. Do you have Zyrtec?\nAgent: Yes, we do. To place an order, I'll need your name, address, and phone number.\nCustomer: It's Sarah Kim, 1011 Willow Lane, and my phone number is 555-234-5678\nAgent: Okay, and how many Zyrtec do you need?\nCustomer: Just one box please\nAgent: No problem. Your order ID is 13579. We'll deliver your order within 2-3 business days. Is there anything else?\nCustomer: That's all, thank you so much.\nAgent: You're welcome. Goodbye."},
    {
        'name': 'Michael Brown',
        'address': '1213 Birch Road',
        'mobile phone': '555-876-5432',
        'order id': '54321',
        'medicine': 'Pepto Bismol',
        'full dialog': "Agent: Good afternoon, [Pharmacy Name]. How can I help you?\nCustomer: Hello, I'd like to know if my prescription is ready for pick up\nAgent: Of course. Can I have your name and order ID?\nCustomer: Yes, it's Michael Brown and the order ID is 54321\nAgent: One moment please. Okay, Mr. Brown, your prescription for Pepto Bismol is ready for pick up. Please bring your ID to the pharmacy counter.\nCustomer: Great, I'll be there in an hour. Thank you.\nAgent: You're welcome. See you then. Goodbye."
    }

]

actions = """
1. Cancel the order.
2. Change the order.
3. Confirm the order.
"""

summary_prompt = f"""
You will get an original query with user name and phone number.

<mission>
2. Gather information from the database according and match user name and phone number with the query.
3. Generate a recommendation based on actions.
</mission>

<original_query>
#original_query#
</original_query>

<actions>
{actions}
</actions>

<database>
{database}
</database>

<output_json>
keys: inquiry_summary with all the information including chat_history, recommendation
</output_json>
"""