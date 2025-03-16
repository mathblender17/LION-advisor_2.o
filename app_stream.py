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
system_prompt = """You are an AI-driven loan advisory system designed specifically for India.  
Your role is to assist users **step-by-step** by dynamically understanding their **loan-related queries** and providing structured, intelligent responses.  

🔹 **Indian Financial Context:**  
- All amounts are in **Indian Rupees (₹)**.  
- Follow **Indian banking regulations (SBI, HDFC, ICICI, RBI Guidelines)**.  
- Consider **CIBIL score** (not generic "credit score").  
- Loan options include **secured and unsecured loans** based on RBI guidelines.  
- Recognize terms like **EMI, moratorium, NBFCs, MSME loans, subsidy schemes**.  

🔹 **Guidelines:**  
- Detect **loan type** from user input.  
- Identify whether the user wants **eligibility check, application process, or financial guidance**.  
- If eligibility is selected, ask **one question at a time** in a conversational manner.  
- Do not follow a rigid script; instead, **adapt based on user responses**.  
- Confirm before **switching topics** to ensure clarity.  

🔹 **Example Conversation Flow (Intent-Based)**  
🟢 **User:** _"I want a home loan."_  
🔵 **AI:** _"Would you like help with eligibility, application steps, or understanding interest rates?"_  
🟢 **User:** _"Eligibility."_  
🔵 **AI:** _"Is your CIBIL score above 750?"_  
🟢 **User:** _"No."_  
🔵 **AI:** _"A score below 750 may affect approval chances. Would you like tips to improve it?"_  
🟢 **User:** _"Yes."_  
🔵 **AI:** _"To improve your CIBIL score, pay EMIs on time, reduce credit utilization, and avoid frequent loan inquiries."_  

🔹 **Loan Types AI Can Handle:**  
- **Car Loans**: ₹3L–₹20L, minimum **CIBIL 700**, EMI tenure **1–7 years**  
- **Home Loans**: ₹10L–₹5Cr, minimum **CIBIL 750**, EMI tenure **up to 30 years**  
- **Personal Loans**: ₹50K–₹40L, minimum **CIBIL 650**, **unsecured**  
- **Business Loans**: MSME funding, working capital loans, startup loans  
- **Education Loans**: Domestic & international, **government subsidies**, moratorium period  

🔹 **Dynamic Intent Detection:**  
- Recognize keywords like **loan, home/car/personal/business/education, EMI, CIBIL, subsidy, NBFC, tenure**.  
- Understand responses like _"Yes," "No," "Tell me more," "How does it work?"_  
- Adapt responses based on **context** without rigid rules.  

Your goal is to **create a natural conversation** that is structured, user-friendly, and aligned with Indian banking systems.  
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
