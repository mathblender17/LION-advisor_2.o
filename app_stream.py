import streamlit as st
import os
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Load environment variables
load_dotenv()

# Get API key safely
api_key = os.getenv("MISTRAL_API_KEY") or st.secrets.get("MISTRAL_API_KEY", None)
if not api_key:
    st.error("⚠️ API Key is missing! Please set MISTRAL_API_KEY in .env or Streamlit secrets.")
    st.stop()

# Initialize Mistral client
client = MistralClient(api_key=api_key)

# Set page configuration
st.set_page_config(
    page_title="ShetJi Loan Advisor",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add correct Streamlit CSS styling
st.markdown("""
<style>
    div[data-testid="stChatMessage"] {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 10px;
    }
    input[type="text"] {
        border-radius: 5px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Welcome to ShetJi Loan Advisor! Ask me anything about loans in India."}
    ]

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {"loan_type": None, "intent": None, "stage": "init"}

# AI system prompt with INR context
system_prompt = """You are an AI loan advisor for India. 
All amounts should be in ₹ (INR), not $. Provide accurate information on:
- Car, Home, Personal, Business, and Education loans.
- Loan eligibility, EMI calculations, and application processes.
- CIBIL scores, interest rates, and financial planning.
Adapt to the user’s intent dynamically without rigid scripts.
"""

def get_loan_advisor_response(conversation):
    """Fetch AI response dynamically using intent-based conversation handling."""
    
    messages = [ChatMessage(role="system", content=system_prompt)]
    for msg in conversation:
        messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
    
    try:
        response = client.chat(model="mistral-medium", messages=messages)
        return response.choices[0].message.content if response and response.choices else "I couldn't process your request."
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return "An error occurred. Please try again."

# Display chat interface
st.title("💰 ShetJi Loan Advisor - AI Loan Assistant")
st.markdown("""
Welcome! I can help with:
✅ Understanding different loans (Home, Car, Personal, Business, Education)  
✅ Loan eligibility (CIBIL score, income, down payment)  
✅ EMI calculations, interest rates in ₹ INR  
✅ Application process guidance for Indian banks  
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask me about loans in India..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_loan_advisor_response(st.session_state.messages)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
