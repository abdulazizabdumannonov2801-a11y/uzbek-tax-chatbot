import streamlit as st
import requests
import json
import os
import tax_calculator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Config & Styling ---
st.set_page_config(
    page_title="UzbekTax AI",
    page_icon="🇺🇿",
    layout="centered"
)

# Custom CSS for a premium feel
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stChatMessage {
        background-color: #262730;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #2b313e;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stButton>button {
        background-image: linear-gradient(to right, #00C9FF 0%, #92FE9D  51%, #00C9FF  100%);
        margin: 10px;
        padding: 15px 45px;
        text-align: center;
        text-transform: uppercase;
        transition: 0.5s;
        background-size: 200% auto;
        color: white;            
        box-shadow: 0 0 20px #eee;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-position: right center; /* change the direction of the change here */
        color: #fff;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# --- App Logic ---

st.title("🇺🇿 UzbekTax AI Assistant")
st.caption("Expert Generative AI for Uzbekistan Tax Code (2025)")

# Sidebar for Key or Settings
with st.sidebar:
    st.header("Settings")
    # Try to get from env first
    env_key = os.getenv("GOOGLE_API_KEY")
    api_key_input = st.text_input("Enter Google API Key", value=env_key if env_key else "", type="password")
    
    # Use input if available, else env
    api_key = api_key_input if api_key_input else env_key
    
    st.info("Ask about PIT, CIT, VAT, or ask for calculation help!")
    st.markdown("---")
    st.markdown("**Core Rates (2025):**\n- PIT: 12%\n- CIT: 15%\n- VAT: 12%")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "content": "Assalomu alaykum! I am your Uzbekistan Tax assistant. I can explain tax rules for 2025 or calculate taxes for you. How can I help?"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Helper Functions ---
def get_gemini_response(messages, api_key):
    # Using gemini-2.5-flash as discovered in checks
    model_name = "gemini-2.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    system_instruction = {
        "parts": [{
            "text": """You are an expert Tax Consultant for Uzbekistan, updated with 2025 laws.
    
    Key Data Points for 2025:
    - **Personal Income Tax (PIT)**: 12% standard. 1% for students. 0% for dividends (Apr 2022-Dec 2028 for JSC shares).
    - **Corporate Income Tax (CIT)**: 15% standard. 20% for banks/mobile/cement. 10% for e-commerce. 1% for knitwear/footwear (preferential).
    - **Value Added Tax (VAT)**: 12% standard. 0% exports.
    
    Behavior:
    - Answer questions concisely and accurately.
    - When a user provides specific numbers (salary, profit, amount), ALWAYS call the appropriate tool to calculate.
    - Format monetary output nicely (e.g., "1,200,000 UZS").
    - If the user speaks Uzbek, reply in Uzbek. If English, reply in English."""
        }]
    }

    # API Format: { "role": "user"|"model", "parts": [{"text": "..."}] }
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    tools = [{
        "function_declarations": [
            {
                "name": "calculate_pit",
                "description": "Calculates Personal Income Tax (PIT) for 2025.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "income": {"type": "NUMBER", "description": "Gross income in UZS"},
                        "is_student": {"type": "BOOLEAN", "description": "If the taxpayer is a student (1% preferential rate)"}
                    },
                    "required": ["income"]
                }
            },
            {
                "name": "calculate_cit",
                "description": "Calculates Corporate Income Tax (CIT) for 2025.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "profit": {"type": "NUMBER", "description": "Taxable profit in UZS"},
                        "category": {"type": "STRING", "description": "Category: 'standard', 'bank', 'mobile', 'ecommerce'"}
                    },
                    "required": ["profit"]
                }
            },
            {
                "name": "calculate_vat",
                "description": "Calculates Value Added Tax (VAT) for 2025 (12%).",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "amount": {"type": "NUMBER", "description": "Total amount or base amount"},
                        "includes_vat": {"type": "BOOLEAN", "description": "True if amount includes VAT, False if amount is base"}
                    },
                    "required": ["amount"]
                }
            }
        ]
    }]

    payload = {
        "contents": contents,
        "system_instruction": system_instruction,
        "tools": tools
    }

    # First attempt
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    return response.json()

# --- Main Interaction ---
if api_key and (prompt := st.chat_input("Type your tax question...")):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call Gemini
    try:
        response_data = get_gemini_response(st.session_state.messages, api_key)
        
        if "error" in response_data:
            st.error(f"API Error: {response_data['error'].get('message')}")
        else:
            candidate = response_data.get("candidates", [{}])[0].get("content", {})
            parts = candidate.get("parts", [])
            
            final_text = ""
            function_calls = []

            for part in parts:
                if "text" in part:
                    final_text += part["text"]
                if "functionCall" in part:
                    function_calls.append(part["functionCall"])

            # 3. Handle Function Calls
            if function_calls:
                fc = function_calls[0]
                fn_name = fc["name"]
                args = fc.get("args", {})
                
                result = None
                if fn_name == "calculate_pit":
                    result = tax_calculator.calculate_pit(args.get("income"), args.get("is_student", False))
                elif fn_name == "calculate_cit":
                    result = tax_calculator.calculate_cit(args.get("profit"), args.get("category", "standard"))
                elif fn_name == "calculate_vat":
                    result = tax_calculator.calculate_vat(args.get("amount"), args.get("includes_vat", True))
                
                # Show Result
                tool_msg = f"**Calculation Result ({fn_name}):**\n```json\n{json.dumps(result, indent=2)}\n```"
                st.session_state.messages.append({"role": "model", "content": tool_msg})
                with st.chat_message("model"):
                    st.markdown(tool_msg)
                
                # Follow-up Summary
                summary_prompt = f"Explain this tax calculation result to the user naturally: {json.dumps(result)}"
                
                # Use same model for summary
                model_name = "gemini-2.5-flash"
                summary_response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}",
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"role": "user", "parts": [{"text": summary_prompt}]}]}
                )
                
                if summary_response.status_code == 200:
                    summary_cand = summary_response.json().get("candidates", [{}])[0].get("content", {})
                    summary_text = summary_cand.get("parts", [{}])[0].get("text", "")
                    if summary_text:
                        st.session_state.messages.append({"role": "model", "content": summary_text})
                        with st.chat_message("model"):
                            st.markdown(summary_text)

            elif final_text:
                st.session_state.messages.append({"role": "model", "content": final_text})
                with st.chat_message("model"):
                    st.markdown(final_text)

    except Exception as e:
        st.error(f"An error occurred: {e}")
