import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
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

def generate_ad_copy_with_ai(keywords, landing_page, sentiment, usps, ctas):
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
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert ad copywriter for Google Ads."},
                  {"role": "user", "content": prompt}]
    )
    
    return response["choices"][0]["message"]["content"]

def main():
    st.title("AI-Powered Responsive Search Ads Generator")
    
    openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to generate ads.")
        return
    openai.api_key = openai_api_key
    
    keywords = st.text_area("Enter Keywords (comma-separated)", "best shipping software, affordable shipping rates, fast label printing").split(",")
    keywords = [k.strip() for k in keywords if k.strip()]
    
    landing_page = st.text_input("Landing Page URL", "https://www.stamps.com")
    
    sentiment = st.selectbox("Select Sentiment", ["Positive", "Neutral", "Urgent"])
    
    usps = st.text_area("Enter Unique Selling Points (comma-separated)", "Save Time & Money, Easy-To-Use Interface, Trusted By Thousands").split(",")
    usps = [u.strip() for u in usps if u.strip()]
    
    ctas = st.text_area("Enter Call-To-Actions (comma-separated)", "Sign Up Now, Start Saving Today, Try It Free").split(",")
    ctas = [c.strip() for c in ctas if c.strip()]
    
    if st.button("Generate Ad Copy"):
        ad_copy = generate_ad_copy_with_ai(keywords, landing_page, sentiment, usps, ctas)
        
        st.subheader("Generated Ad Copy:")
        st.text_area("Ad Copy Output", ad_copy, height=300)

if __name__ == "__main__":
    main()
