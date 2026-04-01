import streamlit as st
import requests
import feedparser
import pandas as pd
import time

# --- 1. Progress Logic (Simplified) ---
def simple_progress(status_text_area, progress_bar, message="Processing..."):
    """Standard professional progress bar."""
    status_text_area.info(message)
    for i in range(1, 101):
        time.sleep(0.01)
        progress_bar.progress(i)

# --- 2. Dynamic Library Loader ---
def get_llm_library(provider):
    try:
        if provider in ["Aliyun (Qwen)", "OpenAI", "Grok (xAI)", "DeepSeek", "Custom"]:
            from openai import OpenAI
            return OpenAI
        elif provider == "Gemini":
            import google.generativeai as genai
            return genai
    except ImportError as e:
        st.error(f"❌ Library Missing: Run `pip install {e.name}`")
        return None
    return None

# --- 3. Multi-Provider Generation Logic ---
def generate_content(provider, api_key, system_prompt, user_prompt, base_url=None):
    if not api_key:
        st.warning(f"Provide API Key for {provider}")
        return None
    lib = get_llm_library(provider)
    if not lib: return None
    try:
        if provider in ["Aliyun (Qwen)", "OpenAI", "Grok (xAI)", "DeepSeek", "Custom"]:
            endpoints = {
                "Aliyun (Qwen)": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "OpenAI": "https://api.openai.com/v1",
                "Grok (xAI)": "https://api.x.ai/v1",
                "DeepSeek": "https://api.deepseek.com"
            }
            client = lib(api_key=api_key, base_url=base_url or endpoints.get(provider))
            model_name = "qwen-max" if provider == "Aliyun (Qwen)" else "gpt-4-turbo"
            if provider == "Grok (xAI)": model_name = "grok-beta"
            resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            return resp.choices[0].message.content
        elif provider == "Gemini":
            lib.configure(api_key=api_key)
            model = lib.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
    except Exception as e:
        st.error(f"LLM Error: {str(e)}")
        return None

# --- 4. Trend Scraping Logic ---
def fetch_trends(query):
    results = []
    hn_url = f"https://hn.algolia.com/api/v1/search?query={query}&tags=story&numericFilters=created_at_i>{int(pd.Timestamp.now().timestamp()) - 604800}"
    try:
        hn_data = requests.get(hn_url).json()
        for hit in hn_data.get('hits', [])[:8]:
            results.append({"source": "HN", "title": hit['title'], "url": hit.get('url') or f"https://news.ycombinator.com/item?id={hit['objectID']}"})
    except: pass
    subs = ["SaaS", "marketing"]
    for sub in subs:
        rss_url = f"https://www.reddit.com/r/{sub}/search.rss?q={query}&sort=relevance&t=week"
        headers = {'User-Agent': 'B2B-Trend-Bot-v1'}
        try:
            resp = requests.get(rss_url, headers=headers)
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:4]:
                results.append({"source": f"r/{sub}", "title": entry.title, "url": entry.link})
        except: pass
    return results

# --- 5. Streamlit UI ---
st.set_page_config(page_title="High-Signal Engine", layout="wide")
st.title("🚀 B2B LinkedIn High-Signal Engine")

with st.sidebar:
    st.header("Settings")
    provider = st.selectbox("Select Model", ["OpenAI", "Gemini", "Grok (xAI)", "DeepSeek","Aliyun (Qwen)",  "Custom"])
    api_key = st.text_input(f"{provider} API Key", type="password")
    custom_url = st.text_input("Custom API Base URL", placeholder="https://api.example.com/v1")
    industry = st.text_input("Industry Context", "GenAI & B2B Marketing")

tab1, tab2, tab3 = st.tabs(["[1] Style Extraction", "[2] Trend Discovery", "[3] The Gauntlet"])

# --- TAB 1: Style ---
with tab1:
    st.header("Step 1: Extract Creator DNA")
    examples = st.text_area("Paste Viral LinkedIn Posts (--- separator)", height=250)
    if st.button("Extract Style Guide"):
        p_bar = st.progress(0)
        p_status = st.empty()
        simple_progress(p_status, p_bar, "Extracting style patterns...")
        sys = "Analyze these LinkedIn posts (--- separator). Extract: Hook Type, Rhythm, Formatting, Length of sentences & post, CTA, and Credibility Moves. Output Style Guide to produce similar posts."
        guide = generate_content(provider, api_key, sys, examples, custom_url)
        if guide:
            st.session_state['style'] = guide
            p_status.success("Style analysis complete.")
            st.markdown(guide)

# --- TAB 2: Trends ---
with tab2:
    st.header("Step 2: High-Signal Trend Briefing")
    query = st.text_input("Search Keywords", value="AI B2B marketing generative")
    if st.button("Scan HN & Reddit"):
        p_bar = st.progress(0)
        p_status = st.empty()
        simple_progress(p_status, p_bar, "Scanning global data sources...")
        raw_trends = fetch_trends(query)
        processed = []
        for t in raw_trends:
            summary = generate_content(provider, api_key, "Summarize why this matters for B2B founders in 2 sentences.", t['title'], custom_url)
            processed.append({"title": t['title'], "source": t['source'], "summary": summary, "url": t['url']})
        st.session_state['trends'] = processed
        p_status.success("Trend discovery complete.")

    if 'trends' in st.session_state:
        for t in st.session_state['trends']:
            with st.container(border=True):
                st.write(f"**[{t['source']}]** {t['title']}")
                st.caption(t['summary'])
                st.link_button("View Original", t['url'])

# --- TAB 3: The Gauntlet ---
with tab3:
    st.header("Step 3: Multi-Step Anti-Slop Generation")
    if 'trends' not in st.session_state:
        st.info("Please fetch trends in Tab 2 first.")
    else:
        topic = st.selectbox("Select Topic", [t['title'] for t in st.session_state['trends']])
        
        if st.button("Generate Final Post C"):
            p_bar = st.progress(0)
            p_status = st.empty()
            style_guide = st.session_state.get('style', "Direct and professional.")
            
            # Sub-Step A: Style Draft
            p_status.info("Phase 1: Generating initial draft...")
            content_a = generate_content(provider, api_key, f"Style Guide: {style_guide}", f"Write a high-signal LinkedIn post about: {topic}", custom_url)
            p_bar.progress(33)
            
            # Sub-Step B: Critique
            p_status.info("Phase 2: Running adversarial critique...")
            critique_sys = "You are a skeptical B2B analyst. Identify 3 weak points, generic 'AI slop' phrases, corporate buzzwords, or unproven claims in the text. Be brutal."
            content_b = generate_content(provider, api_key, critique_sys, content_a, custom_url)
            p_bar.progress(66)
            
            # Sub-Step C: Synthesis
            p_status.info("Phase 3: Synthesizing final content...")
            
            synthesis_sys_prompt = f"""
            You are a Top 1% B2B LinkedIn Ghostwriter. Your goal is to rewrite a post to remove all "AI Slop".
            
            STRICT RULES:
            1. THE HOOK: Use the most stinging, contrarian, or "brutal truth" point from the CRITIQUE (Content B) to write a new 1-2 line hook. 
            2. THE BODY: Rewrite the original DRAFT (Content A). Remove every generic adjective. If the CRITIQUE called a point "weak" or "fluff", replace it with a specific example, a number, or a technical "hard truth".
            3. TONE: Expert-to-expert. No "cheerleading". No "unlocking potential". Use a "broken rhythm" (short sentences, frequent line breaks).
            4. STYLE GUIDE COMPLIANCE: {style_guide}
            """
            
            synthesis_user_prompt = f"""
            [ORIGINAL DRAFT A]:
            {content_a}
            
            [BRUTAL CRITIQUE B]:
            {content_b}
            
            TASK: 
            Create a new, ready-to-publish LinkedIn post that sounds like a human expert who just got called out for being too generic and is now doubling down with specific, hard-hitting insights.
            """
            
            content_c = generate_content(provider, api_key, synthesis_sys_prompt, synthesis_user_prompt, custom_url)
            
            p_bar.progress(100)
            p_status.success("Final generation complete.")

            st.success("🔥 Final Post C")
            st.code(content_c, language="markdown")
            
            with st.expander("Review Generation History"):
                st.subheader("Initial Draft A")
                st.write(content_a)
                st.subheader("The Critique B")
                st.error(content_b)