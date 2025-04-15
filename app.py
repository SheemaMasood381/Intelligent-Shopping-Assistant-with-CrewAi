import streamlit as st
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
import os
from dotenv import load_dotenv
import speech_recognition as sr

# Load environment variables
load_dotenv(".env")

# Initialize LLM
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
gemini_llm = LLM(
    api_key=GOOGLE_API_KEY,
    model="gemini/gemini-2.0-flash-lite",
    temperature=0,
    max_tokens=None
)

# Helper function for voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening for voice input...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write("Recognized: " + text)
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
            return None

# Define Agents
input_collector = Agent(
    role="User Input Collector",
    goal="Gather and clarify user requirements for product search from text or voice input, with a focus on products available in Pakistan.",
    backstory="You are an expert in understanding user needs from various input types and translating them into clear search parameters, ensuring the results are relevant to users in Pakistan.",
    llm=gemini_llm,
    verbose=True
)

search_tool = SerperDevTool(api_key=SERPER_API_KEY)
scrape_tool = ScrapeWebsiteTool(website_url='https://google.com/')

web_searcher = Agent(
    role="Web Search Specialist",
    goal="Find product listings across multiple websites",
    backstory="You are a master of online product search, capable of finding the best deals.",
    tools=[search_tool, scrape_tool],
    llm=gemini_llm,
    allow_delegation=False,
    verbose=True
)

analyst = Agent(
    role="Product Analyst",
    goal="Analyze product listings for best prices and reviews",
    backstory="You are skilled in comparing products to identify the best deals.",
    llm=gemini_llm,
    verbose=True
)

review_tool = WebsiteSearchTool(
    config=dict(
        llm=dict(
            provider="google",
            config=dict(
                model="gemini/gemini-2.0-flash-lite",
                api_key=GOOGLE_API_KEY
            )
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document"
            )
        )
    )
)

review_agent = Agent(
    role="Review Analyzer",
    goal="Analyze reviews and summarize user sentiment.",
    tools=[review_tool],
    backstory="You extract pros and cons from product reviews using advanced RAG techniques.",
    llm=gemini_llm,
    verbose=True
)

recommender = Agent(
    role="Shopping Recommendation Specialist",
    goal="Recommend the best product based on analysis and user preferences",
    backstory="You provide tailored product recommendations with clear reasoning.",
    llm=gemini_llm,
    verbose=True
)

# Define Tasks
input_task = Task(
    description=(
        "Process the user input '{user_input}' to generate a refined product search query.\n"
        "Details should be based on this specific input."
    ),
    expected_output="A well-formed product search query based on the user's input.",
    agent=input_collector
)

search_task = Task(
    description="Search online for the best matching products using the refined search query.",
    expected_output="A list of product listings from various websites with key details.",
    agent=web_searcher,
    context=[input_task]
)

analysis_task = Task(
    description="Analyze product listings to find best options based on price, ratings, and features.",
    expected_output="A summary of top deals with pros and cons.",
    agent=analyst,
    context=[search_task]
)

review_task = Task(
    description="Analyze reviews and summarize key pros and cons for shortlisted products.",
    expected_output="Summarized reviews in bullet points.",
    agent=review_agent,
    context=[analysis_task]
)

recommendation_task = Task(
    description="Recommend the best product to the user with a purchase link and reasoning.",
    expected_output="A clear product recommendation with explanation and purchase link.",
    agent=recommender,
    context=[review_task]
)

product_knowledge = StringKnowledgeSource(
    content="Information about current product trends, including electronics, fashion, beauty, lifestyle, and more."
)

# Setup the Crew
shopping_crew = Crew(
    agents=[input_collector, web_searcher, analyst, review_agent, recommender],
    tasks=[input_task, search_task, analysis_task, review_task, recommendation_task],
    verbose=True,
    process=Process.sequential,
    embedder={
        "provider": "google",
        "config": {
            "model": "models/text-embedding-004",
            "api_key": GOOGLE_API_KEY,
        }
    }
)


# --- Streamlit App UI ---
st.set_page_config(page_title="ShopSmart.AI", page_icon="🛒")
st.title("🛍️ ShopSmart.AI – Voice/Text Shopping Assistant using Gen AI")

# --- Sidebar ---
with st.sidebar:
    st.header("🛠️ Controls")
    
    # Handle reset from URL
    query_params = st.query_params
    if "reset" in query_params and query_params["reset"] == "1":
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

    # Start new chat via query param
    if st.button("🧹 Start New Chat"):
        st.query_params["reset"] = "1"
        st.rerun()

    # Manual chat reset
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input type selection
input_type = st.radio("Choose input type", ("Text", "Voice"), horizontal=True)

# Capture input
if input_type == "Text":
    user_input = st.chat_input("Ask me about a product or continue shopping...")
else:
    if st.button("🎤 Click to Speak"):
        user_input = get_voice_input()
    else:
        user_input = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching and analyzing..."):
            result = shopping_crew.kickoff(inputs={"user_input": user_input})
            response = result.raw
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("""<style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        color: gray;
        background-color: white;
    }
    .footer hr {
        border: 1px solid #ddd;
        margin: 0;
    }
    </style>
    <div class="footer">
        <hr>
        Powered by Streamlit | Developed by Sheema Masood<br>
    </div>""", unsafe_allow_html=True)
