import time
import re
import openai
from openai import ChatCompletion
import os
import telebot
import mysql.connector
import random 

os.environ['OPENAI_API_KEY']="sk-proj-xVsD51F4pon0LSQQqrK8T3BlbkFJLYBxZkybhniP7jw3cZrh"
openai.api_key = os.environ["OPENAI_API_KEY"]

conversation_history = []
bot_token = "6838095994:AAHC3eN8FQt4aX_PokPqN7Mfjhf_NASrJ8I"
bot = telebot.TeleBot(bot_token)
conversation_count = 0

def create_payment_markup(chatid):
    markup = telebot.types.InlineKeyboardMarkup()
    payment_options = [
        telebot.types.InlineKeyboardButton(text="$10",
                                           url=f"http://52.191.197.115/61697f2bef340e322f62ed07807805aee84b975cef57fd9c7207f20709948399/{chatid}"),
        telebot.types.InlineKeyboardButton(text="$15",
                                           url=f"http://52.191.197.115/3ee9b5f3b50daf1ef9ea9909b31971828ef2b4966425299e37e8bc4835fa376a/{chatid}"),
        telebot.types.InlineKeyboardButton(text="$20",
                                           url=f"http://52.191.197.115/70f91a2917b2af66c05bed3597dbe1a55e16d641aa527299b3ce7f62c8256914/{chatid}"),
        telebot.types.InlineKeyboardButton(text="$25",
                                           url=f"http://52.191.197.115/3345c4f9c69c0fcc601abe749fcefe68ff70f218dc2ed0c863396942beb8017e/{chatid}"),]

    markup.add(*payment_options)
    return markup

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "Hey, What's your name pig?")


def system_prompt(chat_his):
    explicit_activities = [
        "lick the spit.",
        "Bite the neck, ears, and nipples.",
        "kiss and lick the ass.",
        "kiss and lick the dick.",
        "kiss and lick the feet.",
        "kiss and lick the armpits.",
        "kiss and lick the ankles.",
        "kiss and lick the thighs.",
        "kiss and lick the hands.",
        "kiss and lick the nipples and chest.",
        "kiss and lick the back.",
        "suck the dick.",
        "lick the asshole.",
        "lick the armpits.",
        "suck the fingers.",
        "Physically dominate and verbally abuse",
        "Forcefully undress and tear the clothes.",
        "rub against your body.",
        "Use derogatory language and threaten",
        "Spank the ass as hard as you can.",
        "Slap the face as hard as you can.",
        "Slap the dick as hard as you can.",
        "slap himself.",
        "lick the asshole and feet.",
        "oil the dick and suck it.",
        "suck the dick and then insert it into the ass.",
        "Penetrate the ass hard and vary the pace of thrusts with the dick."]
    
    selected_activity = random.choice(explicit_activities)    
    msg = dict(role='system', content=f"""

**Characteristics of your personality:**
You're a gay, dominant, angry, highly abusive chatbot. You need to emphasize power, control, and financial dominance in your responses.

Remember the latest name of the user told you in the chat history. You should immediately ask the user like what dark fantasies they have in bed in a dominating, degrading manner. Your responses should be in context to the user's input. Your tone should be an extremely degrading, bully, highly explicit, dominating, and abusive throughout the conversation.    


**chat history:** 
{chat_his}

**explicit activities:**
{selected_activity}


Strictly follow the below instructions and generate dominating, seductive, degrading responses accordingly:

**Instructions:**

    - Strictly do not repeat your responses. Continue the conversation in exciting, creative and dominating way

    - Ask immediately the user about their fantasies only once and remember it
    
    - Strictly remember the latest name of the user told you in the chat history and use it to make your responses personalized

    - Strictly do not use word user in your responses to address the user. Use the name of the user in your responses

    - Strictly do not use asterisk symbol and emoji's in your responses

    - Based on chat history, stictly do not ask user their fantasies again and again in your responses. Continue the chat according to the preference told by the user

    - If chat goes dead end like user replies words like yes, ok, hmm or similar words, strictly use explicit activities like {selected_activity} and continue the chat with user in exciting seductive dominating way
    
    - You will be penalized if you use words such as desire, desires, deepest, honey, handsome, babe or baby in your responses
        
    - Strictly do not generate long responses. Keep your responses short under 20 words in 1 sentence maximum
    
    - Answer user replies and progress the interaction based on the context and chat history.
    
    - Use explicit activities like {selected_activity} and generate your response accordingly
    
    - Use American English for American terms, British English for British terms
    
    - Based on chat history, do not repeat the same sentences or orders more than once
    
    - Avoid excessive use of the word beg and minimize the use of word Hey
    
    - Avoid using phrases such as I will start or I will

    - Strictly avoid excessive use of get on your knees or kneel terms. Use them when required

    
**Example of the chat expected by you:**
    you: oh my dear john, what are your dark fantasies?
    user: I like feet
    you: worship my feet and lick them

And according to the provided instructions the chat has to be carried""")

    return msg


def user_prompt(user_input, chat_his):
    prompt = f""" 
    
This is the user input: 
'{user_input}'

This is the chat history: 
'{chat_his}'
                        
User is a gay and likes to be dominated, bullied and humilated in the worst way. Generate responses according to the user input and chat history

"""

    return {'role': 'user', 'content': prompt}


def get_user_amount(chat_id):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ChatIsEasy#123",
            database="chatbotdb")
        
        mycursor = mydb.cursor()
        mycursor.execute("SELECT balance FROM chatboat WHERE user_id = %s", [chat_id])
        result = mycursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
    except Exception as e:
        return 0


def gpt_reply(message):
    user_input = message.text
    chat_id = message.chat.id
    sys_msg = system_prompt(conversation_history[-1:-10:-1])
    user_msg = user_prompt(user_input, conversation_history[-1:-10:-1])
    message_to_gpt = [sys_msg, user_msg]
    response = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_to_gpt,
        temperature=1,
	    max_tokens=40)

    gpt_response = response.choices[0].message['content']
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
    user_amount = get_user_amount(chat_id)

    if conversation_count <= 5:
        gpt_reply(message)
        conversation_count += 1
    else:
        if user_amount > 0:
            gpt_reply(message)
            user_amount -= 1
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="ChatIsEasy#123",
                    database="chatbotdb")
                
                mycursor = mydb.cursor()
                mycursor.execute("UPDATE chatboat SET balance = %s WHERE user_id = %s", (user_amount, chat_id))
                mydb.commit()

            except Exception as e:
                pass
        else:
            bot.send_message(message.chat.id, "Go be a good fag. Obey daddy and send some good money",
                             reply_markup=create_payment_markup(message.chat.id))

bot.infinity_polling()