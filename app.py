import streamlit as st
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
import os
from dotenv import load_dotenv
import speech_recognition as sr
from st_audiorec import st_audiorec
import whisper
from groq import Groq

# Load environment variables
load_dotenv(".env")

# Initialize LLM
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


gemini_llm = LLM(
    api_key=GOOGLE_API_KEY,
    model="gemini/gemini-2.0-flash-lite",
    temperature=0,
    max_tokens=None
)

# Initialize Whisper model for transcription
model = whisper.load_model("base")
client = Groq(api_key=GROQ_API_KEY)



# Helper function for transcribing audio using Groq
def transcribe_audio_with_groq(audio_data):
    # Send the audio to Groq for transcription
    try:
        response = groq_client.transcribe(audio_data)
        if response.status_code == 200:
            transcription = response.json()["text"]
            return transcription
        else:
            st.error("Error in transcribing audio with Groq: " + response.text)
            return None
    except Exception as e:
        st.error(f"An error occurred while transcribing: {str(e)}")
        return None


# Define Agents
input_collector = Agent(
    role="User Input Collector",
    goal="Gather and clarify user requirements for product search from text or voice input, with a focus on products available in Pakistan.",
    backstory="You are an expert in understanding user needs from various input types and translating them into clear search parameters, ensuring the results are relevant to users in Pakistan.",
    llm=gemini_llm,
    verbose=True
)

# Define  web search Tools
# Tools for specific websites
search_tool = SerperDevTool(api_key=SERPER_API_KEY)

scrape_google = ScrapeWebsiteTool(website_url='https://google.com/')
scrape_amazon = ScrapeWebsiteTool(website_url='https://www.amazon.com/')
scrape_daraz = ScrapeWebsiteTool(website_url='https://www.daraz.pk/')


web_searcher = Agent(
    role="Web Search Specialist",
    goal="Find product listings across Google, Amazon, and Daraz",
    backstory="You are a skilled product search expert who knows how to extract valuable listings from multiple platforms.",
    tools=[search_tool, scrape_google, scrape_amazon, scrape_daraz],
    llm=gemini_llm,
    allow_delegation=False,
    verbose=True
)



analyst = Agent(
    role="Product Comparison Expert",
    goal="Evaluate and compare product listings from different vendors to identify the best option based on quality, price, and reviews.",
    backstory="You are a skilled product analysis expert. Your job is to compare various options available online, understand their features and pricing, and help users make informed decisions by providing pros, cons, and recommendations.",
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
    goal="Analyze reviews and summarize user sentiment for the top product recommended by the analysis task from the specified vendor.",
    backstory="You analyze reviews from the selected vendor's website (Daraz, Amazon, AliExpress) for the chosen product to extract pros, cons, and overall user sentiment.",
    tools=[review_tool],
    llm=gemini_llm,
    verbose=True
)

# Define the final recommendation agent
recommender = Agent(
    role="Shopping Recommendation Specialist",
    goal="Recommend the best product based on analysis and user preferences",
    backstory="You provide tailored product recommendations with clear reasoning, combining product details and customer reviews to help users make the best purchase decision.",
    llm=gemini_llm,
    verbose=True
)

## Define Tasks
filters = {
    "min_rating": 4.0,
    "brand": "Sony"
}

# Manually format the filters
brand = filters["brand"] if filters["brand"] else "Any"

description = (
    f"Process the user input: '{{user_input}}'\n"
    f"Use the following filters if applicable:\n"
    f"- Minimum Rating: {filters['min_rating']}\n"
    f"- Preferred Brand: {brand}\n"
    "Generate a refined product search query based on these inputs."
)

# Now, use the formatted description in your Task
input_task = Task(
    description=description,
    expected_output="A well-formed product search query based on the user's input.",
    agent=input_collector
)


search_task = Task(
    description="""
        Search online for the best matching products using the refined search query.
        Look for product listings across Google, Amazon, and Daraz. Use appropriate tools for each platform 
        (e.g., Serper API for Google, scraping for Amazon and Daraz). Return a summarized list with key details 
        like title, price, link, and brief description.
    """,
    expected_output="A list of product listings from Google, Amazon, and Daraz with key details.",
    agent=web_searcher,
    context=[input_task]
)

analysis_task = Task(
    description=(
        "Analyze the provided product listings from different websites (Google, Amazon, Daraz). "
        "Compare key features, prices, availability, and customer ratings. "
        "Summarize the pros and cons of each option and select the best product(s) based on overall value. "
        "Include the vendor name (Amazon, Daraz, or AliExpress) for the top recommended product."
    ),
    expected_output="A summary of pros and cons for each product, with a final recommended option, reasoning, and the vendor name.",
    agent=analyst,
    context=[search_task]
)


review_task = Task(
    description=(
        "Using the top product recommendation and vendor from the analysis task, "
        "summarize customer reviews for this product. Review feedback will include pros, cons, and sentiment analysis. "
        "First, determine the correct website URL based on the vendor (Amazon, Daraz, or AliExpress). "
        "Then use the WebsiteSearchTool to analyze reviews from that specific website."
    ),
    expected_output="A summarized list of pros, cons, and user sentiment for the selected product from the appropriate vendor's website.",
    agent=review_agent,
    context=[analysis_task]
)

recommendation_task = Task(
    description="Provide the best product recommendation based on features, customer reviews, and user preferences.",
     expected_output="A concise product recommendation with summarized reasoning, including product features, price, pros/cons, and customer sentiment.",
    agent=recommender,
    context=[
        analysis_task,  # Output from Analysis Agent (Best Product)
        review_task     # Output from Review Agent (Review Analysis)
    ]
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
        st.session_state.clear()
        st.rerun()

    # Filters Section
    st.subheader("🔍 Filters (Optional)")

    filters = {
        "min_rating": st.slider("Minimum Rating", min_value=1.0, max_value=5.0, value=3.5),
        "brand": st.text_input("Preferred Brand", value="")
    }

    st.session_state["filters"] = filters
    st.write("Filters will be applied to the product search.")

# Filters are now stored in session state and ready to be used.
# --- Main Chat Area ---
st.header("💬 Chat with ShopSmart.AI")

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
    uploaded_audio = st.file_uploader("🎤 Upload audio for voice input", type=["mp3", "wav", "ogg"])

    if uploaded_audio:
        st.audio(uploaded_audio, format='audio/wav')  # Show audio player
        audio_data = uploaded_audio.read()  # Read audio data
        user_input = transcribe_audio_with_groq(audio_data)  # Transcribe audio to text using Groq

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching and analyzing..."):
            # When triggering the Crew to start processing with the inputs
            result = shopping_crew.kickoff(inputs={
                "user_input": user_input,
                "filters": st.session_state.get("filters", {})
            })
            response = result.raw
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer

st.markdown("""
    <style>
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
        color: gray;
        background-color: white;
        z-index: 100;
    }
    .custom-footer hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 0;
    }
    </style>

    <div class="custom-footer">
        <hr>
        Powered by Streamlit | Developed by Sheema Masood
    </div>
    """, unsafe_allow_html=True)

