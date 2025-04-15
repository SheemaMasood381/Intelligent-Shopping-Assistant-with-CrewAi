from crewai import Crew, Process
from utils import load_environment_variables, get_api_key, check_environment_variables
# Import agents and tasks
from agents import input_collector, web_searcher, analyst, review_agent, recommender
from tasks import input_task, search_task, analysis_task, review_task, recommendation_task

# Load environment variables at the start of your script
load_environment_variables()

# Check if all required API keys are available
required_keys = ["GOOGLE_API_KEY", "SERPER_API_KEY"]
check_environment_variables(required_keys)

# Now get API keys securely
GOOGLE_API_KEY = get_api_key("GOOGLE_API_KEY")
SERPER_API_KEY = get_api_key("SERPER_API_KEY")

# Create the Crew
shopping_crew = Crew(
    agents=[
        input_collector,
        web_searcher,
        analyst,
        review_agent,
        recommender
    ],
    tasks=[
        input_task,
        search_task,
        analysis_task,
        review_task,
        recommendation_task
    ],
    process=Process.sequential,  # Each agent takes input from the previous one
    verbose=True,
    embedder={
        "provider": "google",
        "config": {
            "model": "models/text-embedding-004",
            "api_key": GOOGLE_API_KEY,
        }
    }
)
