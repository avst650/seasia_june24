import autogen, tiktoken

inp=input('Enter your product name: ')

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

msg=f"""
Sumarize the reviews of {inp} from top 3 websites. 

If there is a bot blocker skip that website and jump to next website. answer should be under 8000 tokens.
"""

print("tokens: ", num_tokens_from_string(msg, "cl100k_base"))

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    file_location="/home/anush/Desktop/ai_agents/",
    filter_dict={
        # "model": {"gpt4"},
        "model": ["gpt-4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314", "gpt-3.5-turbo"],
    },
)

llm_config={
    "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "code",
        "use_docker": False,
    },
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

user_proxy.initiate_chat(
    assistant,
    # message=f"""
    # Sumarize the reviews of {inp} from top 3 websites. 
    # If there is a bot blocker skip that website and jump to next website
    # """)
    message=msg)
