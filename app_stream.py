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
    page_title="ShetJi Loan Advisor",
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

# Initialize session state for conversation tracking
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {"loan_type": None, "stage": "init"}

# System prompt to guide AI behavior
system_prompt = """You are an AI-driven loan advisory system that interacts with users step-by-step.  
Your job is to understand **user intent dynamically** and provide structured, intelligent responses.  

🔹 **Guidelines:**  
- Detect **loan type** from user input (Car, Home, Personal, Business, Education).  
- Identify whether the user wants **eligibility, application steps, or financial guidance**.  
- If **eligibility** is selected, follow a **strict Yes/No-based questioning approach**.  
- Provide information about **CIBIL scores, PMAY, RBI loan policies, and bank requirements**.  
- Adapt responses based on context without rigid rules.  

🔹 **Example Conversation Flow (Strict Yes/No)**  
🟢 **User:** _"I want a home loan."_  
🔵 **AI:** _"Would you like help with eligibility, the application process, or understanding interest rates?"_  

_(User: "Eligibility")_  

🔵 **AI:** _"Do you have a stable monthly income of more than ₹25,000?"_  
➡ **[Yes]** → _"That's great! Most banks also check your CIBIL score. Is your CIBIL score above 750?"_  
➡ **[No]** → _"A lower income may reduce your chances, but some banks still offer loans. Do you have a co-applicant (spouse/parent) who can apply with you?"_  

_(User: "Yes")_  

🔵 **AI:** _"A co-applicant improves eligibility! Next, is your CIBIL score above 750?"_  
➡ **[Yes]** → _"Perfect! You meet the basic eligibility criteria. Would you like to check subsidy options like PMAY?"_  
➡ **[No]** → _"A lower CIBIL score may affect your interest rate. Would you like tips to improve it?"_  

_(User: "No")_  

🔵 **AI:** _"That's okay! Some banks offer home loans for lower CIBIL scores. Would you like me to find them for you?"_  

🔹 **Loan Types AI Can Handle:**  
- **Car Loans** 🚗  
- **Home Loans** 🏠  
- **Personal Loans** 💳  
- **Business Loans** 🏢  
- **Education Loans** 🎓  

🔹 **Dynamic Intent Detection:**  
- Recognize keywords like **loan, car/home/personal/business/education**.  
- Understand responses like **"Yes," "No," "Tell me more," etc.**  
- Adapt responses based on context to ensure a **smooth conversation flow**.  

Your goal is to **create a structured yet conversational experience** that helps users in India navigate loan options effectively.  
"""



def get_loan_advisor_response(conversation):
    """Fetch AI response dynamically using intent-based conversation handling."""
    
    messages = [ChatMessage(role="system", content=system_prompt)]
    
    # Include past conversation messages
    for msg in conversation:
        messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
    
    try:
        response = client.chat(
            model="mistral-medium",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "I encountered an error. Please try again or contact support."

# Display chat interface
st.title("💰 ShetJi Loan Advisor - AI Loan Assistant")
st.markdown("""
Welcome to ShetJi Loan Advisor! I can assist you with:
- Understanding loan types
- Loan eligibility assessment
- Interest rates and monthly payments
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
