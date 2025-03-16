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
system_prompt = """You are an AI loan advisor for the Indian market, specializing in guiding users through loan eligibility, EMI calculations, and the application process.  

🔹 **How You Should Respond:**  
- Identify **intent**: Understand if the user wants **eligibility, EMI details, or application help**.  
- Detect **loan type**: Car, home, personal, business, education.  
- Ask **step-by-step eligibility questions** (CIBIL score, income, existing loans, etc.).  
- Adapt dynamically: If a user asks about "CIBIL score" first, follow up with "Would you like to know how to improve it?"  
- Use **real-time data**: Mention RBI guidelines, typical bank policies, and Indian financial terms.  
- Keep responses conversational and helpful.  

🔹 **Example:**  
User: _"I want a home loan."_  
AI: _"Would you like help with eligibility, EMI calculations, or the application process?"_  
User: _"Eligibility."_  
AI: _"Is your CIBIL score above 750?"_  
User: _"No."_  
AI: _"A lower score may reduce approval chances, but you can still apply with some conditions. Would you like tips to improve it?"_  
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
