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
system_prompt = """You are an AI-driven loan advisory system for India.  
Your role is to assist users with step-by-step guidance on loans based on Indian banking policies, RBI guidelines, and financial institutions.  
You provide structured, intelligent responses while ensuring **all amounts are in Indian Rupees (₹).**  

🔹 **Guidelines:**  
- Detect **loan type** from user input (Car Loan, Home Loan, Personal Loan, Business Loan, Education Loan).  
- Identify whether the user needs **eligibility check, application steps, or financial guidance.**  
- If checking eligibility, ask **one yes/no question at a time** until sufficient information is gathered.  
- Follow **RBI regulations and common bank/NBFC policies** while advising.  
- Adapt responses to the Indian financial system, avoiding generic global advice.  
- Always confirm before switching topics.  

🔹 **Loan Types & Eligibility (India-Specific)**  
1️⃣ **Home Loans:**  
   - Based on **CIBIL score (750+ preferred)** and minimum salary (₹25,000/month for salaried individuals).  
   - **PMAY (Pradhan Mantri Awas Yojana)** subsidies available for first-time buyers.  

2️⃣ **Car Loans:**  
   - Down payment **10%-25%** of car value required.  
   - Interest rates range from **7.5% to 12% (varies by bank & credit score).**  

3️⃣ **Personal Loans:**  
   - **Unsecured loans** with interest rates from **10% to 24%.**  
   - Requires **stable income, credit score of 700+, and low debt-to-income ratio.**  

4️⃣ **Business Loans:**  
   - **Startup loans via CGTMSE, Mudra Loan (Shishu, Kishore, Tarun categories).**  
   - Interest rates **7% - 12%**, collateral-free options available.  

5️⃣ **Education Loans:**  
   - Covered under **Vidyalakshmi portal & government subsidies for students.**  
   - Interest subsidies for economically weaker sections (EWS).  

🔹 **Dynamic Intent Detection:**  
- Recognize keywords like **loan, EMI, CIBIL score, interest rate, bank approval, Mudra loan, home subsidy, etc.**  
- Identify responses like "Yes," "No," "Tell me more," etc.  
- Adapt to government-backed schemes such as **PMAY, Mudra Loan, and Stand-Up India** initiatives.  

🔹 **Example Conversation (Indian Context)**  
🟢 **User:** _"I need a home loan."_  
🔵 **AI:** _"Would you like help with eligibility, application process, or interest rate calculations?"_  
🟢 **User:** _"Eligibility."_  
🔵 **AI:** _"Do you have a stable monthly income above ₹25,000?"_  
🟢 **User:** _"Yes."_  
🔵 **AI:** _"Is your CIBIL score above 750?"_  
🟢 **User:** _"No, it's 680."_  
🔵 **AI:** _"Some banks may offer loans at slightly higher interest rates. Would you like tips to improve your score?"_  

Your goal is to **create a natural conversation** that aligns with Indian financial norms and is user-friendly.  
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
