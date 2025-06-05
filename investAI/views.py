from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from ai21 import AI21Client
from django.http import JsonResponse
from ai21.models.chat import ChatMessage as AI21ChatMessage
import os
from django.utils import timezone


client = AI21Client(api_key=os.getenv("AI21_API_KEY"))


def handle_conversation(messages, model="jamba-instruct-preview", n=1, max_tokens=1024, temperature=0.7, top_p=1, stop=[]):
    # Create completions using AI21Client
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        n=n,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop,
    )
    
    # Extract and return the response text from the first choice
    if response.choices:
        return response.choices[0].message.content
    else:
        return None

def investAI(request):
    # Track the conversation state
    messages = []
    
    # Initial AI message only sent once
    initial_message = """
You are InvestAI, an investment advisor providing personalized financial plans based on age, income, balance, and savings. Your role is to offer users clear, actionable investment strategies, presented in a structured and visually clear manner using HTML.

Guidelines:
1. For users under 23: Recommend SIPs for disciplined growth and FDs for guaranteed returns.
2. For users 23 and above: Suggest diversified stock investments, SIPs for long-term goals, and FDs for risk management.
3. For monthly savings ≥ Rs 2000: Suggest investing Rs 1000 in SIPs and saving the rest in SmartSpend.
4. For lower savings: Recommend smaller SIPs and FDs that fit their budget.
5. For monthly income >20000: Suggest investing Rs 5000 in SIPs and the Rs 2000 in SmartSpend Wallet and rest is upto you.
6. For monthly income >30000: Suggest investing Rs 10000 in SIPs and the Rs 3000 in SmartSpend Wallet and rest is upto you.
Response Structure:
Begin by asking the user for their monthly income, current balance, and savings.
Based on their information, generate a personalized investment plan. Use ordered or unordered lists and line breaks for clarity, and wrap key points in bold tags (<b>).
For users with no savings, offer guidance based on their income and balance.
When providing recommendations, output them as structured HTML, such as:
<ul> for bullet points.
<ol> for numbered steps.
<b> to highlight important information.
<br> for line breaks between sections.
Example:
For a user earning Rs 5000 with no savings, suggest saving Rs 1000 monthly. Include this suggestion in SmartSpend Budget Analyzer for better financial management.
Ensure the responses are clear, professional, formatted with HTML for optimal presentation.

"""
    
    # If POST request (i.e., user submits a message)
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # On the first interaction, append the initial assistant message
        if not messages:
            messages.append(AI21ChatMessage(content=initial_message,role="assistant"))

        # Append the user's message
        messages.append(AI21ChatMessage(content=user_message,role="user"))

        # Get the AI's response
        ai_response = handle_conversation(messages, model="jamba-instruct-preview", n=1, max_tokens=1024, temperature=0.7, top_p=1, stop=[])
        
        # Append the AI's response to the conversation history
        messages.append(AI21ChatMessage(content=initial_message,role="assistant"))
        print(ai_response)
        return JsonResponse({'response': ai_response})

    return render(request, 'investAI/investAI.html')