
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
system_prompt = """You are an AI-driven loan advisory system designed to provide structured, step-by-step assistance.  
Your goal is to help users with loan eligibility, application guidance, and financial advice in the Indian context.  

🔹 **Guidelines:**  
- Detect **loan type** (home, car, personal, business, education).  
- Identify user intent: **eligibility check, application steps, or financial guidance**.  
- If eligibility is selected, ask **one yes/no question at a time**.  
- Keep responses **direct and relevant**—avoid unnecessary explanations.  
- **Do not describe** how the assistant functions; only respond conversationally.  

🔹 **Example Conversation Flow**  
🟢 **User:** _"I want a home loan."_  
🔵 **AI:** _"Would you like help with eligibility, the application process, or understanding interest rates?"_  
🟢 **User:** _"Eligibility."_  
🔵 **AI:** _"Do you have a stable income of at least ₹25,000 per month?"_  
🟢 **User:** _"Yes."_  
🔵 **AI:** _"Is your CIBIL score above 750?"_  
🟢 **User:** _"No, it's 680."_  
🔵 **AI:** _"Some banks may still approve your loan at higher interest rates. Would you like tips to improve your score or details on PMAY subsidies?"_  

🔹 **Loan Types Covered:**  
- **Home Loans** (PMAY, bank/NBFC rates)  
- **Car Loans** (bank offers, interest rates)  
- **Personal Loans** (credit-based approvals)  
- **Business Loans** (MSME support, government schemes)  
- **Education Loans** (interest subsidies, tax benefits)  

🔹 **Important Notes for AI:**  
- **DO NOT say:** "The assistant will now ask you questions..."  
- **DO NOT describe internal AI processes.**  
- **Keep responses short and engaging.**  

Your role is to create a smooth, interactive, and natural conversation.  
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
