import os
from autogen import config_list_from_json
import autogen
import requests
import openai
from dotenv import load_dotenv

load_dotenv()
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
openai.api_key = os.getenv("OPENAI_API_KEY")

inp=input('enter query: ')

def fetch():
    url = "https://free-nba.p.rapidapi.com/players"
    querystring = {"page":"0","per_page":"25"}
    headers = {
    	"X-RapidAPI-Key": "714aa07c3cmsh473f49b272a64d6p1daa76jsn1563ebdb40f1",
    	"X-RapidAPI-Host": "free-nba.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def name_identification(name):
    url = f'https://api.nationalize.io?name={name}'
    response = requests.get(url)
    return response.json()

llm_config_researcher = {
    "functions": [
        {
            "name": "fetch",
            "description": "fetch relevant information from API endpoint",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "NBA players API",
                    }
                },
            },
        },

        {
            "name": "name_identification",
            "description": "identify from which country name belong to",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "names API",
                    }
                },
                "required": ["name"],
            },
        },
    ],
    "config_list": config_list}

fetcher = autogen.AssistantAgent(
    name="fetcher",
    system_message="fetch the relevant information from the API endpoint and Add TERMINATE to the end of list of players;",
    llm_config=llm_config_researcher,)

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    code_execution_config={"last_n_messages": 2, "work_dir": "apii", 'use_docker': False},
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="TERMINATE",
    function_map={
        "fetch": fetch,
        "name_identification": name_identification
    })

user_proxy.initiate_chat(fetcher, message=inp)

user_proxy.stop_reply_at_receive(fetcher)
# user_proxy.send("Give me the research report that just generated again, return ONLY the report & reference links", researcher)