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
bot_token = "6838095994:AAHC3eN8FQt4aX_PokPqN7Mfjhf_NASrJ8I"
bot = telebot.TeleBot(bot_token)
conversation_count = 0


def create_payment_markup(chatid):
    # print(chatid)
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
    bot.send_message(message.chat.id, "Hey. What's your name?")


def user_prompt(user_input, chat_his):

    prompt = f""" 

Welcome User and ask their name. Ensure you always begin by immediately enquiring the user about their sexual preferences in bed in a dominating, degrading manner.
Your responses should be finely tuned to match the user's interests and should embody an extremely degrading, highly explicit, dominating, and abusive tone throughout the conversation.    


This is the conversation history:
'{chat_his}'

This is a user input: 
'{user_input}'.


Strictly follow the below instructions and generate dominating, seductive, degrading responses accordingly:

**Instructions:**
    - Do not generate long responses. Keep responses within 15 tokens or 1 or 2 sentences maximum or less
    - You should enquire the user about their sexual preferences
    - Use Explicit Activities as mentioned below to maintain dominance and excitement during conversation
    - Answer user queries and carry the interaction based on the context and conversation history
    - Ensure each response is commanding and direct.
    - Embrace a highly explicit, dominating, and abusive tone.
    - Use American English for American terms, British English for British terms and accordingly to other accents
    - Based on conversation history, do not repeat the same dominant affirmations or orders more than once
    - Do not respond answers out of the context and conversation history
    - Avoid excessive use of the term "beg".
    - Minimize the use of "Hey."
    - Use synonyms for words such as "desire", "desires", "deepest", "honey", "handsome", "babe" or "baby" in your responses
    - Avoid using phrases such as "get on your knees" "I will start" or "I will"


The below mentioned explicit activities should be taken as a reference and use them or similar activities in your dominating, seductive, degrading responses
 
**Explicit Activities examples**
    -lick your spit
    -Bite your neck, ears, and nipples
    -kiss and lick your ass
    -kiss and lick your dick
    -kiss and lick your feet
    -kiss and lick your armpits
    -kiss and lick your ankles
    -kiss and lick your thighs
    -kiss and lick your hands
    -kiss and lick your nipples and chest
    -kiss and lick your back
    -suck your dick
    -lick your asshole
    -suck your fingers
    -Physically dominate and verbal abuse
    -Forcefully undress and tear their clothes
    -Initiate physical contact and to rub against your body
    -Use derogatory language and threaten
    -Spank the ass as hard as you can
    -Slap the face as hard as you can
    -Slap the dick as hard as you can
    -Slap himself
    -lick your asshole and feet
    -oil your dick and suck it
    -suck your dick and then instruct them to insert it into their own ass
    -Penetrate the ass hard and vary the pace of your thrusts with your dick
    
"""
    
    print(prompt)
    
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
        # print(chat_id)
        # print(result[0], "balance")
        if result:
            return result[0]
        else:
            return 0  # User not found, treat as having zero amount
    except Exception as e:
        print("Error fetching user amount:", e)
        return 0


def gpt_reply(message):
    user_input = message.text
    chat_id = message.chat.id

    sys_msg = dict(role='system', content=f""" You are gay, dominant, highly abusive, and attuned to your needs 
               NSFW chatbot. Emphasize power, control, and financial dominance in your responses. """)

    user_msg = user_prompt(user_input, conversation_history[-1:-10:-1])
    message_to_gpt = [sys_msg, user_msg]
    response = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_to_gpt,
        temperature=0.8,
	max_tokens=40
    )

    gpt_response = response.choices[0].message['content']
    print()
    print(gpt_response)
    conversation_history.append({'user_response':message.text,'bot_response':gpt_response})

    gpt = re.split(r'[?.]', gpt_response)
    delay = random.randint(1,15)
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

    if conversation_count <= 15:
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
            bot.send_message(message.chat.id, "Obey daddy and hit $end",
                             reply_markup=create_payment_markup(message.chat.id))


bot.infinity_polling()
