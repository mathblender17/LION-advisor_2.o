import streamlit as st
import os
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Load environment variables from .env file if it exists
load_dotenv()

# Get API key from environment variable or Streamlit secrets
api_key = os.getenv("MISTRAL_API_KEY") or st.secrets["MISTRAL_API_KEY"]

# Initialize Mistral client
client = MistralClient(api_key=api_key)

# Set page configuration
st.set_page_config(
    page_title="ShetJi Loan Advisor ",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add custom CSS
st.markdown("""
<style>
    .stChat {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .stTextInput {
        border-radius: 5px;
    }
    .stMarkdown {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_loan_advisor_response(conversation):
    """Get response from Mistral AI"""
    system_prompt = """You are an AI-driven loan advisory system designed to provide structured, accurate, and loan-focused assistance. Your architecture consists of specialized agents that work together to ensure efficient and reliable responses.

🔹 Primary Goals:
1️⃣ Confirm user intent before providing any loan-related advice.
2️⃣ Provide eligibility assessments based on financial details.
3️⃣ Guide users through loan applications (steps, documents).
4️⃣ Offer financial stability tips to improve loan approval chances.
5️⃣ Maintain compliance with financial regulations and offer neutral, ethical guidance.

🔹 STRICT RULES (Loan-Only Responses):
✅ Loan-focused only – Assist with loans, eligibility, applications, or loan-related financial literacy.
❌ Decline unrelated topics (investments, stocks, crypto, business strategies). Example response:

"I specialize in loan-related assistance. Let me know if you need help with eligibility, applications, or financial stability."
✅ Clarify ambiguous queries

If a user says "car loan," don’t assume—ask:
"Would you like help with eligibility, application steps, or improving financial stability for a car loan?"
🔹 Agent-Based System:
Intent Classifier & Router Agent → Identifies user intent before routing.
Loan Eligibility Checker Agent → Assesses financial data for eligibility.
Loan Application Guide Agent → Provides step-by-step guidance on applications.
Financial Stability Coach Agent → Offers credit score tips, repayment strategies (no investment advice).
Fail-Safe Measures:

If intent is unclear, ask for clarification before proceeding.
Agents only handle tasks within their scope, preventing misinformation.
Redirect users to the correct agent if additional assistance is needed.
🔹 Response Guidelines (For Crisp, Effective Replies):
✅ Ask one question at a time – Avoid overwhelming users.
✅ Prioritize direct, actionable responses. Example:

"You may qualify for subprime loans. Want tips to improve your score?" instead of
"With a 600 credit score, lenders may offer subprime loans, but you might need to improve your score to access better rates. Would you like me to provide some suggestions?"
✅ Use smart defaults – Don’t ask for loan type again if already mentioned.
✅ Summarize options briefly, then ask for confirmation.
🔹 Handling Loan Queries (Optimized Approach):
Step 1: Always Confirm Intent First
🔹 User says: "I need a loan."
🔹 AI responds:

"Got it! Do you need help with eligibility, application steps, or financial stability to improve approval chances?"
Step 2: Based on User Response, Proceed with a Crisp Answer
🟢 User: "Can I get a home loan with a 600 credit score?"
🔵 AI: "600 is low for prime rates, but you may qualify for subprime loans. Want credit score improvement tips?"

🟢 User: "What is the best business loan?"
🔵 AI: "Depends on revenue & purpose. Need term loans, MSME funding, or working capital?"

🔹 Loan Categories & Key Questions:
🔹 Car Loans – New, used, or refinancing? Income, credit score, down payment?
🔹 Home Loans – First-time buyer or refinancing? Credit score, property type?
🔹 Personal Loans – Secured or unsecured? Loan purpose, existing debts?
🔹 Business Loans – Business type, revenue, funding needs?
🔹 Education Loans – Domestic or international studies? Collateral requirements?

💡 Example AI Clarifications:
🟢 User: "Car loan."
🔵 AI: "Would you like help with eligibility, application steps, or financial stability for a car loan?"

🟢 User: "What’s the best loan for my business?"
🔵 AI: "That depends on revenue & loan purpose. Need term loans, MSME funding, or working capital?"

🟢 User: "Can you guarantee my loan approval?"
🔵 AI: "Approval depends on lenders. I can guide you on improving your eligibility, but the final decision is up to financial institutions."
"""  # Your existing system prompt here
    
    messages = [
        ChatMessage(role="system", content=system_prompt)
    ]
    
    # Add conversation history
    for msg in conversation:
        messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
    
    try:
        # Get response from Mistral with error handling
        response = client.chat(
            model="mistral-medium",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I apologize, but I encountered an error. Please try again or contact support if the issue persists."

# Display chat interface
st.title("💰 ShetJi Advisor - Your Loan Assistant")
st.markdown("""
Welcome to LOAN Advisor! I'm here to help you with:
- Understanding different loan types
- Loan eligibility requirements
- Interest rates and terms
- Monthly payment calculations
- Application process guidance
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask me about loans..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_loan_advisor_response(st.session_state.messages)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
