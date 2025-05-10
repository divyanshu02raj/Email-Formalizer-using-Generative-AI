import streamlit as st
import requests

#Groq API key 
GROQ_API_KEY = "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"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# Streamlit Page Config
st.set_page_config(page_title="Email Formalizer", layout="centered")
st.title("📧 Email Formalizer using LLaMA3 (Groq)")
st.markdown("Convert casual messages into professional emails using the Groq API + LLaMA3.")

# User Input
user_input = st.text_area("✍️ Enter your casual message below:", height=150, placeholder="e.g., hey can u send me the ppt for today's lecture?")

# Generate button
if st.button("Generate Formal Email"):
    if not user_input.strip():
        st.warning("⚠️ Please enter a message to formalize.")
    else:
        # Prepare payload
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that rewrites casual messages into formal emails."
                },
                {
                    "role": "user",
                    "content": f"Convert this to a formal email:\n\n{user_input.strip()}"
                }
            ],
            "temperature": 0.7
        }

        # API call
        try:
            response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            formal_email = response.json()["choices"][0]["message"]["content"].strip()
            st.subheader("📨 Formal Email Output:")
            st.success(formal_email)
        except requests.exceptions.RequestException as e:
            st.error(f"🚨 API Request failed: {e}")
        except Exception as e:
            st.error(f"🚨 Unexpected error: {e}")
