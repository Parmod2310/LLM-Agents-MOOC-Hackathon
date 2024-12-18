from typing import Dict, List
from autogen import ConversableAgent, register_function
import sys
import os
from dotenv import load_dotenv


SCORE_KEYWORDS = {
    1: ["awful", "horrible", "disgusting"],
    2: ["bad", "unpleasant", "offensive"],
    3: ["average", "uninspiring", "forgettable"],
    4: ["good", "enjoyable", "satisfying"],
    5: ["awesome", "incredible", "amazing"]
}


def normalize(name: str) -> str:
    return (
        name.lower()
        .replace('-', ' ')
        .replace('.', ' ')
        .replace('  ', ' ')
        .strip()
    )

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    restaurant_data = {}
    reviews = []
    actual_name = None

    restaurant_name_normalized = normalize(restaurant_name)

    try:
        with open('restaurant-data.txt', 'r') as f:
            lines = f.readlines()

        for line in lines:
            if not line.strip():
                continue

            line_normalized = normalize(line)
            if line_normalized.startswith(restaurant_name_normalized):
                actual_name = line.split('.')[0].strip()
                reviews.append(line.strip())

        if actual_name and reviews:
            restaurant_data[actual_name] = reviews

        return restaurant_data
    except FileNotFoundError:
        print("Error: restaurant-data.txt not found")
        return {}

def calculate_overall_score(restaurant_name: str, food_scores: List[int], service_scores: List[int]) -> Dict[str, str]:

    if len(food_scores) != len(service_scores) or len(food_scores) == 0:
        raise ValueError("Food scores and customer service scores must have the same non-zero length")

    total_food = sum(food_scores)
    total_service = sum(service_scores)
    N = len(food_scores)

    overall_score = (total_food + total_service) / (2 * N)

    overall_score = max(1.0, min(overall_score, 5.0))

    formatted_score = "{:.3f}".format(overall_score)
    return {restaurant_name: formatted_score}

def create_agent(name: str, system_message: str, llm_config: dict) -> ConversableAgent:
    return ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config
    )

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

def main(user_query: str):
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
    entrypoint_agent = create_agent(
        "entrypoint_agent",
        """You are the supervisor agent coordinating the restaurant review analysis process.""",
        llm_config
    )

    agents = {
        "data_fetch": create_agent("data_fetch_agent", "", llm_config),
        "analyzer": create_agent("review_analyzer_agent", "", llm_config),
        "scorer": create_agent("scoring_agent", "", llm_config)
    }

    register_function(fetch_restaurant_data, caller=entrypoint_agent, executor=agents["data_fetch"])
    register_function(calculate_overall_score, caller=entrypoint_agent, executor=agents["scorer"])

    result = entrypoint_agent.initiate_chats([
        {"recipient": agents["data_fetch"], "message": f"Find reviews for this query: {user_query}"},
        {"recipient": agents["analyzer"], "message": "Analyze these reviews to extract scores."},
        {"recipient": agents["scorer"], "message": "Calculate the overall score using extracted scores."}
    ])

    print(result)
    return result

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the overall score for Taco Bell?"
    main(query)
