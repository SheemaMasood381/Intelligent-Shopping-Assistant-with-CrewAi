# agents.py

from crewai import Agent, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, WebsiteSearchTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# LLM Configuration
gemini_llm = LLM(
    api_key=GOOGLE_API_KEY,
    model="gemini/gemini-2.0-flash-lite",
    temperature=0.2,
    max_tokens=None
)

# Tools
search_tool = SerperDevTool(api_key=SERPER_API_KEY)
scrape_tool = ScrapeWebsiteTool(website_url='https://google.com/')
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

# 🧠 Agents

# 1. User Input Collector
input_collector = Agent(
    role="User Input Collector",
    goal="Gather and clarify user requirements for product search from text or voice input, especially for Pakistani markets.",
    backstory="An expert in understanding diverse user inputs and translating them into meaningful, localized product search queries.",
    llm=gemini_llm,
    verbose=True
)

# 2. Web Search Specialist
web_searcher = Agent(
    role="Web Search Specialist",
    goal="Find relevant and cost-effective product listings across multiple websites.",
    backstory="Master of web searches, skilled in identifying deals tailored to user preferences.",
    tools=[search_tool, scrape_tool],
    llm=gemini_llm,
    allow_delegation=False,
    verbose=True
)

# 3. Product Analyst
analyst = Agent(
    role="Product Analyst",
    goal="Analyze product listings for best prices, features, and user ratings.",
    backstory="A detail-oriented agent that compares product specs and reviews to find the top options.",
    llm=gemini_llm,
    verbose=True
)

# 4. Review Analyzer
review_agent = Agent(
    role="Review Analyzer",
    goal="Analyze customer reviews to extract common sentiments, pros, and cons.",
    tools=[review_tool],
    backstory="A sentiment-focused agent who uses RAG to summarize public opinion about products.",
    llm=gemini_llm,
    verbose=True
)

# 5. Recommendation Specialist
recommender = Agent(
    role="Shopping Recommendation Specialist",
    goal="Recommend the best-fit product with reasoning and purchase link.",
    backstory="A friendly and knowledgeable assistant who understands your needs and suggests the best option for you.",
    llm=gemini_llm,
    verbose=True
)
