import re
import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
import openai

def capitalize_words(text):
    return " ".join(word.capitalize() for word in text.split())

def truncate_text(text, limit):
    return text[:limit] if len(text) > limit else text

def scrape_website(landing_page):
    try:
        response = requests.get(landing_page, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            return " ".join(paragraphs)
    except requests.RequestException:
        pass
    return ""

def generate_ad_copy_with_ai(keywords, landing_page, sentiment, usps, ctas, temperature):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OpenAI API key not found in environment variables."

    scraped_content = scrape_website(landing_page)
    prompt = f"""
    Generate a Google Responsive Search Ad with the following parameters:
    - Keywords: {', '.join(keywords)}
    - Landing Page: {landing_page}
    - Sentiment: {sentiment}
    - Unique Selling Points: {', '.join(usps)}
    - Call-To-Actions: {', '.join(ctas)}
    - Website Content: {scraped_content[:1000]} (truncated for brevity)

    Ensure that:
    - Headlines are full sentences, max 30 characters each (15 headlines)
    - Descriptions are max 90 characters each (4 descriptions)
    - Paths (2) are max 15 characters each
    - Ad copy complies with Google Ads policies
    """

    client = openai.Client(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert ad copywriter for Google Ads."},
                  {"role": "user", "content": prompt}],
        temperature=temperature
    )

    return response.choices[0].message.content

# Streamlit UI
st.title("AI-Powered Google Ads RSA Generator")

landing_page = st.text_input("Landing Page URL:")
keywords = st.text_area("Enter Keywords (comma-separated):").split(",")
sentiment = st.selectbox("Select Sentiment:", ["Positive", "Neutral", "Persuasive"])
usps = st.text_area("Enter Unique Selling Points (comma-separated):").split(",")
ctas = st.text_area("Enter Call-To-Actions (comma-separated):").split(",")
temperature = st.slider("AI Creativity (Temperature):", 0.0, 1.0, 0.7)

generate_button = st.button("Generate Ad Copy")

if generate_button:
    if landing_page and keywords and usps and ctas:
        with st.spinner("Generating ad copy..."):
            ad_copy = generate_ad_copy_with_ai(keywords, landing_page, sentiment, usps, ctas, temperature)
            st.subheader("Generated Ad Copy:")
            st.write(ad_copy)
    else:
        st.error("Please fill in all required fields.")
