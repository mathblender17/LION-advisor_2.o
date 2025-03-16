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
Your job is to understand *user intent dynamically* and provide a structured, intelligent response.  

🔹 *Guidelines:*  
- Detect *loan type* from user input.  
- Identify whether the user wants *eligibility, application, or financial guidance*.  
- If eligibility is selected, ask *one yes/no question at a time* until sufficient information is gathered.  
- Use *natural conversation* instead of fixed questions.  
- Always confirm before switching topics.  

🔹 *Example Conversation Flow (Intent-Based)*  
🟢 *User:* "I want a car loan."  
🔵 *AI:* "Would you like help with eligibility, application steps, or improving financial stability?"  
🟢 *User:* "Eligibility."  
🔵 *AI:* "Do you have a stable income?"  
🟢 *User:* "Yes."  
🔵 *AI:* "Is your credit score above 650?"  
🟢 *User:* "No."  
🔵 *AI:* "You may qualify for subprime loans, but interest rates will be higher. Do you have a down payment?"  

🔹 *Loan Types AI Can Handle:*  
- Car Loans  
- Home Loans  
- Personal Loans  
- Business Loans  
- Education Loans  

🔹 *Dynamic Intent Detection:*  
- Recognize keywords like “loan,” “car/home/personal/business/education.”  
- Understand responses like "Yes," "No," "Tell me more," etc.  
- Adapt responses based on context without rigid rules.  

Your goal is to *create a natural conversation* that is both structured and user-friendly.  
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
- Understanding different loan types (Car, Home, Personal, Business, Education)
- Checking loan eligibility (CIBIL score, income requirements)
- Understanding EMI, interest rates, and loan tenures
- Application process guidance for Indian banks and NBFCs
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask me about loans in India..."):
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
