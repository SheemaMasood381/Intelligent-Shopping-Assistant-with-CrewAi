from crewai import task


input_task = Task(
    description=(
        "Take the user's input: '{user_input}' and convert it into a clean, optimized search query .\n"
        "for online product discovery in Pakistan."
        "Details should be based on this specific input.\n"
        "Make sure to include relevant keywords and phrases that would help in finding the best products.\n"
    ),
    expected_output="A well-formed product search query based on the user's input.",
    agent=input_collector
)
search_task = Task(
    description="Search online for the best matching products using the refined search query.",
    expected_output="A list of product listings from various websites with key details.",
    agent=web_searcher,
    context=[input_task]  # Use the output from input_task
)

analysis_task = Task(
    description="Analyze product listings to find best options based on price, ratings, and features.",
    expected_output="A summary of top deals with pros and cons.",
    agent=analyst,
    context=[search_task]  # Use the output from search_task
)

review_task = Task(
    description="Analyze reviews and summarize key pros and cons for shortlisted products.",
    expected_output="Summarized reviews in bullet points.",
    agent=review_agent,
    context=[analysis_task]  # Use the output from analysis_task
)

recommendation_task = Task(
    description="Recommend the best product to the user with a purchase link and reasoning.",
    expected_output="A clear product recommendation with explanation and purchase link.",
    agent=recommender,
    context=[review_task]  # Use the output from review_task
)