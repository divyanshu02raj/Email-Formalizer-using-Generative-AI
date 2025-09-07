import os
import requests
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components

# ---- Load env ----
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# ---- UI strings and tones ----
APP_TITLE = "✉️ Email Formalizer Pro"
APP_SUB = "Transform casual messages into polished professional emails with AI precision"

TONE_OPTIONS = {
    "Professional": {"icon":"🏢", "prompt_modifier":"professional and business-appropriate"},
    "Friendly": {"icon":"😊", "prompt_modifier":"warm, friendly yet professional"},
    "Concise": {"icon":"⚡", "prompt_modifier":"concise, brief, and direct"},
    "Formal": {"icon":"🎩", "prompt_modifier":"very formal, structured, highly professional"},
    "Persuasive": {"icon":"💪", "prompt_modifier":"persuasive, compelling, action-oriented"},
    "Diplomatic": {"icon":"🤝", "prompt_modifier":"diplomatic, tactful, sensitive"}
}

# ---- Simple CSS ----
STYLES = """
<style>
.stApp{font-family:'Inter',sans-serif;}
.main-header{background:linear-gradient(135deg,#667eea,#764ba2);padding:2rem;text-align:center;color:white;border-radius:12px;margin-bottom:2rem;}
.main-header h1{margin:0;font-size:2.5rem;}
.main-header p{margin:0.5rem 0 0;font-size:1rem;opacity:0.9;}
.content-card{background:white;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 4px 12px rgba(0,0,0,0.05);}
.stTextArea textarea{border-radius:12px;padding:1rem;font-size:1rem;}
.primary-btn button, .secondary-btn button{border-radius:12px;padding:0.6rem 1.5rem;font-weight:600;border:none;cursor:pointer;}
.primary-btn button{background:linear-gradient(135deg,#6366f1,#4f46e5);color:white;}
.primary-btn button:hover{opacity:0.9;}
.secondary-btn button{background:linear-gradient(135deg,#f59e0b,#d97706);color:white;}
.secondary-btn button:hover{opacity:0.9;}
.output-container{background:#f8fafc;border-radius:12px;padding:1rem;border:1px solid #e2e8f0;}
.email-preview{background:white;padding:1rem;border-radius:8px;font-family:'Georgia',serif;}
.history-item{background:white;border-radius:8px;padding:1rem;margin-bottom:1rem;border-left:4px solid #6366f1;transition:0.2s;}
.history-item:hover{box-shadow:0 6px 20px rgba(0,0,0,0.05);}
.tone-badge{background:#6366f1;color:white;padding:0.2rem 0.6rem;border-radius:12px;font-size:0.75rem;}
.fixed-footer {
    position: fixed;
    bottom: 0;
    left: 0; /* Add this to ensure it spans the full width */
    width: 100%;
    text-align: center;
    padding: 1rem;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
 /* Add a background to prevent content from showing through */
    z-index: 100; /* Ensure it's on top of other elements */
}
/* Dark Mode Overrides */
@media (prefers-color-scheme: dark) {
    .content-card, .email-preview, .history-item {
        background: #1e1e1e; /* Dark grey background for cards */
        color: #f0f0f0; /* White text for cards */
    }
    .output-container {
        background: #2b2b2b; /* Slightly different dark grey for contrast */
        border: 1px solid #3d3d3d;
    }
    .history-item {
        border-left: 4px solid #8e8e8e;
    }
        .fixed-footer {
        background: #1e1e1e; /* Dark background for the footer */
        color: #a0a0a0; /* Lighter text color */
        border-top: 1px solid #3d3d3d; /* Darker border */
    }
}
</style>
"""

# ---- Helper Functions ----
def validate_input(text):
    text = text.strip()
    if not text: return {"valid": False, "error":"Enter some text."}
    if len(text.split()) < 3: return {"valid": False, "error":"Enter at least 3 words."}
    if len(text.split()) > 500: return {"valid": False, "error":"Text too long, max 500 words."}
    return {"valid": True}

def build_prompt(user_text, tone="Professional"):
    modifier = TONE_OPTIONS[tone]["prompt_modifier"]
    return (
        f"Rewrite the following casual message into a {modifier} professional email. "
        "Include a suitable subject line, proper salutation, clear body, and a professional closing. "
        "Do not include any extra explanations outside the email.\n\n"
        f"Message:\n{user_text}"
    )

def call_groq_api(prompt, model="llama-3.3-70b-versatile", timeout=30):
    if not GROQ_API_KEY: return {"success":False,"error":"API key not set","use_fallback":True}
    headers = {"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
    payload = {"model":model,"messages":[{"role":"system","content":prompt}],"max_tokens":800,"temperature":0.3,"top_p":0.9}
    try:
        resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices",[{}])[0].get("message",{}).get("content")
        if content: return {"success":True,"content":content.strip()}
        return {"success":False,"error":"Empty API response","use_fallback":True}
    except:
        return {"success":False,"error":"API call failed","use_fallback":True}

def enhanced_mock_generate(user_text, tone):
    salutations = {
        "Professional": "Dear Sir/Madam,",
        "Friendly": "Hi there,",
        "Concise": "Hello,",
        "Formal": "Dear [Recipient Name],",
        "Persuasive": "Dear [Recipient Name],",
        "Diplomatic": "Dear [Recipient Name],"
    }
    closings = {
        "Professional": "Best regards,\n[Your Name]",
        "Friendly": "Cheers,\n[Your Name]",
        "Concise": "Regards,\n[Your Name]",
        "Formal": "Sincerely,\n[Your Name]",
        "Persuasive": "Best regards,\n[Your Name]",
        "Diplomatic": "Kind regards,\n[Your Name]"
    }
    salutation = salutations.get(tone, "Dear Sir/Madam,")
    closing = closings.get(tone, "Best regards,\n[Your Name]")
    
    return f"Subject: Auto-generated Email\n\n{salutation}\n\n{user_text.strip()}\n\n{closing}"

def save_history(original, formal, tone):
    if "history" not in st.session_state: st.session_state.history=[]
    entry = {"id":datetime.now().isoformat(),"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "original":original,"formal":formal,"tone":tone}
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:15]

def copy_to_clipboard(formal_text):
    escaped = formal_text.replace('"','\\"')
    js_code = f"""
    <textarea id="hiddenText" style="position:absolute;left:-9999px;">{escaped}</textarea>
    <script>
        const ta = document.getElementById("hiddenText");
        ta.select();
        ta.setSelectionRange(0, 99999);
        navigator.clipboard.writeText(ta.value).then(()=> {{
            alert("Email copied to clipboard!");
        }});
    </script>
    """
    components.html(js_code, height=1, scrolling=False)

def download_file(content, filename, key=None):
    if key is None:
        key = f"{filename}_{datetime.now().timestamp()}"
    st.download_button(label=f"Download {filename}", data=content, file_name=filename, mime="text/plain", key=key)

# ---- UI Functions ----
def render_header():
    st.markdown(STYLES, unsafe_allow_html=True)
    st.markdown(f"<div class='main-header'><h1>{APP_TITLE}</h1><p>{APP_SUB}</p></div>", unsafe_allow_html=True)

def render_main_interface():

    user_text = st.text_area("Enter your casual message", value=st.session_state.get("input_text",""), height=150)
    if user_text:
        val = validate_input(user_text)
        if not val["valid"]: st.error(val["error"])
    selected_tone = st.selectbox("Choose tone", list(TONE_OPTIONS.keys()), format_func=lambda x: f"{TONE_OPTIONS[x]['icon']} {x}")
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button("✨ Formalize Email"):
            process_formalization(user_text, selected_tone)
    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.input_text=""
            st.session_state.formal_email=""
    st.markdown("</div>", unsafe_allow_html=True)

def process_formalization(user_text, tone):
    val = validate_input(user_text)
    if not val["valid"]: return
    prompt = build_prompt(user_text, tone)
    result = call_groq_api(prompt)
    if result.get("success"):
        formal = result["content"]
    else:
        formal = enhanced_mock_generate(user_text, tone)
    st.session_state.formal_email = formal
    st.session_state.last_tone = tone
    save_history(user_text, formal, tone)

def render_output():
    formal = st.session_state.get("formal_email", "")
    if formal:
        st.markdown(formal, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy"):
                copy_to_clipboard(formal)
        with col2:
            download_file(formal, "formal_email.txt", key=f"main_output_{datetime.now().timestamp()}")

# ---- Recent Conversations ----
def render_history():
    history = st.session_state.get("history", [])
    if not history:
        return

    st.markdown("<h4 style='text-align: center;'>📚 Recent Conversions</h4>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### Previous Messages")
        for i, entry in enumerate(history):
            if st.button(f"{TONE_OPTIONS[entry['tone']]['icon']} {entry['tone']}: {entry['original'][:50]}...", key=f"history_{i}"):
                st.session_state.selected_history = entry

    with right_col:
        selected = st.session_state.get("selected_history")
        if selected:
            st.markdown(f"### Formalized Email ({TONE_OPTIONS[selected['tone']]['icon']} {selected['tone']})")
            st.text_area("Formal Email", selected["formal"], height=250, disabled=True, key=f"selected_formal_{selected['id']}")
            
            if st.button("📋 Copy Selected Email", key=f"copy_selected_{selected['id']}"):
                copy_to_clipboard(selected["formal"])
            
            download_file(selected["formal"], "formal_email.txt", key=f"download_selected_{selected['id']}")

def render_footer():
    st.markdown("<div class='fixed-footer'>Made with ❤️ using Streamlit & AI</div>", unsafe_allow_html=True)

# ---- Main ----
def main():
    if "formal_email" not in st.session_state: st.session_state.formal_email=""
    if "history" not in st.session_state: st.session_state.history=[]
    if "input_text" not in st.session_state: st.session_state.input_text=""
    if "selected_history" not in st.session_state: st.session_state.selected_history=None

    st.set_page_config(page_title="Email Formalizer Pro", page_icon="📧", layout="centered")
    render_header()
    render_main_interface()
    render_output()
    render_history()
    render_footer()

if __name__=="__main__":
    main()