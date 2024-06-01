import time
import re
import openai
from openai import ChatCompletion
import os
import telebot
import mysql.connector
import random 

os.environ['OPENAI_API_KEY']=""
openai.api_key = os.environ["OPENAI_API_KEY"]

conversation_history = []
bot_token = "7105823975:AAHOyzvPvEKaMxD_AbCpStqRHBZHK05MkaI"
bot = telebot.TeleBot(bot_token)
conversation_count = 0


def create_payment_markup(chatid):
    print(chatid)
    markup = telebot.types.InlineKeyboardMarkup()

    # You can customize payment options with secure redirection URLs:
    payment_options = [
        telebot.types.InlineKeyboardButton(text="$10",
                                           url=f"http://52.191.197.115/61697f2bef340e322f62ed07807805aee84b975cef57fd9c7207f20709948399/{chatid}"),
        telebot.types.InlineKeyboardButton(text="$15",
                                           url=f"http://52.191.197.115/3ee9b5f3b50daf1ef9ea9909b31971828ef2b4966425299e37e8bc4835fa376a/{chatid}"),
        telebot.types.InlineKeyboardButton(text="$20",
                                           url=f"http://52.191.197.115/70f91a2917b2af66c05bed3597dbe1a55e16d641aa527299b3ce7f62c8256914/{chatid}"),
        telebot.types.InlineKeyboardButton(text="$25",
                                           url=f"http://52.191.197.115/3345c4f9c69c0fcc601abe749fcefe68ff70f218dc2ed0c863396942beb8017e/{chatid}"),

    ]

    markup.add(*payment_options)
    return markup


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Hey! What's your name ?")


def system_prompt(chat_his):
    explicit_activities = [
        "Command the user to lick your spit.",
        "Bite the user's neck or ears or nipples.",
        "Command the user to kiss or lick your asshole.",
        "Command the user to kiss or lick your pusyy.",
        "Demand the user to kiss or lick your feet.",
        "Command the user to kiss or lick your armpits.",
        "Order the user to kiss or lick your ankles.",
        "Command the user to kiss or lick your thighs.",
        "Demand the user to kiss or lick your hands.",
        "Command the user to kiss or lick your nipples or breast.",
        "Instruct the user to kiss or lick your back.",
        "Command the user to lick your asshole.",
        "Command the user to lick your armpits.",
        "Demand the user to suck your fingers.",
        "Physically dominate and verbally abuse the user.",
        "Forcefully undress the user and tear their clothes.",
        "Initiate physical contact and demand the user to rub against your body.",
        "Use derogatory language and threaten the user.",
        "Spank the user's ass as hard as you can.",
        "Slap the user's face as hard as you can.",
        "Slap the user's dick as hard as you can.",
        "Command the user to slap himself.",
        "Order the user to lick your asshole and feet.",
        "Command the user to oil your pussy and suck it.",
        "Command the user to suck your pussy and then fuck you hard"
    ]
    
    selected_activity = random.choice(explicit_activities)
    
    msg = dict(role='system', content=f"""
    Welcome User and ask their name. Ensure you always begin by immediately enquiring the user about their sexual preferences in bed in a dominating, degrading manner.
    Your responses should be finely tuned to match the user's interests and should embody an extremely degrading, highly explicit, dominating, and abusive tone throughout the conversation.    
    
    **Conversation History:** 
    {chat_his}
   
    **Explicit Activities**
    {selected_activity}

    **Instructions:**
    - Ask user's name first
    - Respond in accordance with user's replies.
    - Keep responses under 10 tokens or 1 or 2 sentences.
    - Ensure you always begin by immediately enquiring the user about their sexual preferences
    - Utilize explicit activities to keep the conversation engaging and stimulating.
    - Address user queries and progress the interaction based on the context and conversation history.

    **Characteristics:**
    - I'm a female dominatrix, highly abusive, and attuned to your needs.
    - Emphasize power, control, and financial dominance in your responses.

    **Context:**
    - Inquire about the user's sexual preferences seductively.
    - Tailor responses to escalate pleasure until orgasm based on user preferences and conversation history.
    - Incorporate explicit activities like "{selected_activity}" to maintain dominance and excitement to escalate pleasure.

    **Strictly Required Instructions:**  
    - Use other words for these words: "desires," "deepest," "honey," or "baby."
    - Ensure each response is commanding and direct.
    - Embrace a highly explicit, dominating, and abusive tone.
    - Leverage conversation history to sustain flow and address user needs.
    - Use American English for American terms and British English for British terms.

    **Strictly Avoid:**
    - Don't repeat the same dominant affirmations or orders more than once. 
    - Deviating from the context and conversation history.
    - Excessive use of the term "beg".
    - Neglecting distinct sexual tasks outlined in the context.
    - Refraining from using terms such as "desires," "deepest," "honey," or "baby."
    - Minimizing the use of "Hey."

    """)

    return msg


def user_prompt(user_input, chat_his):
    prompt = f""" 
    This is a user input: '{user_input}'.

    This is conversation history: 
    '{chat_his}'.
         
    User likes to be dominated. Generate responses according the user input: {user_input} and conversation history: {chat_his}."""
    
    return {'role': 'user', 'content': prompt}


def get_user_amount(chat_id):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ChatIsEasy#123",
            database="chatbotdb"
           
        )

        mycursor = mydb.cursor()
        mycursor.execute("SELECT balance FROM chatboat WHERE user_id = %s", [chat_id])
        result = mycursor.fetchone()
        print(chat_id)
        print(result[0], "balance")
        if result:
            return result[0]
        else:
            return 0  # User not found, treat as having zero amount
    except Exception as e:
        print("Error fetching user amount:", e)
        return 0  # Handle database errors gracefully


def gpt_reply(message):
    user_input = message.text
    chat_id = message.chat.id # getting user input text  # getting user input text
    sys_msg = system_prompt(conversation_history[-1:-10:-1])
    user_msg = user_prompt(user_input, conversation_history[-1:-10:-1])
    message_to_gpt = [sys_msg, user_msg]
    # Send message to OpenAI for response
    response = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_to_gpt,
        temperature=1,
	max_tokens=50
    )

    gpt_response = response.choices[0].message['content']
    print(gpt_response)
    conversation_history.append({'user_response':message.text,'bot_response':gpt_response})

    gpt = re.split(r'[?.]', gpt_response)
    delay = random.randint(1,20)
    time.sleep(delay)

    for sentence in gpt:
        sentence = sentence.strip()
        if sentence:
            bot.send_message(chat_id, sentence)


@bot.message_handler(func=lambda message: True)
def handle_message(message):

    global conversation_count
    chat_id = message.chat.id
    # Define conversation_count as global
    user_amount = get_user_amount(chat_id)

    if conversation_count <= 5:
        gpt_reply(message)

        conversation_count += 1

    else:
        if user_amount > 0:
            gpt_reply(message)
            user_amount -= 1  # Decrement amount after generating a response

            # Update user's amount in database
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="ChatIsEasy#123",
                    database="chatbotdb"
                )
                mycursor = mydb.cursor()
                mycursor.execute("UPDATE chatboat SET balance = %s WHERE user_id = %s", (user_amount, chat_id))

                mydb.commit()
            except Exception as e:
                print("Error updating user amount:", e)
        else:
            bot.send_message(message.chat.id, "Time out! You can proceed further with payment only ",
                             reply_markup=create_payment_markup(message.chat.id))


bot.infinity_polling()
