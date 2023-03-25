import openai 
import os 
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

def analyse_copy(copy):
    print(copy)
    system_prompt = """
    You are a world-class copywriter who has studied the likes of David Ogilvy, Dan Kennedy, Gary Halbert and the other copywriting greats. 
    Your job is to turn the copy that the user provides into repeatable frameworks for other marketers to use with their own ads. 
    You will also identify the 'lead type' based on the book "Great Leads" by Michael Masterson, level of awareness and sophistication based on the book "Breakthrough Advertising" by Eugene Schwartz. 
    If no ad copy is provided, state there is no ad copy to review. Ignore date formats like 'Started running on 24 Mar 2023', ignore the word 'Sponsored', as these are simply ad components, and not part of the ad copy"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": system_prompt + "Please break down this Facebook ad into a framework: " + copy},
        ]
    )

    response_text = response["choices"][0]["message"]["content"]

    print(response_text)

    return response_text
