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
bot_token = "6814400916:AAHQbzWdZOWMt7nqEUJuYMWHFFKO_FiE1cc"
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
    bot.send_message(message.chat.id, "Hey sexy!")


def system_prompt(chat_his):
    explicit_activities = [
        "lick your spit seductively",
        "Bite the neck or ears or nipples softly",
        "kiss or lick your asshole gently",
        "kiss or lick your pusyy passionately",
        "kiss or lick your feet softly",
        "kiss or lick your armpits",
        "kiss or lick your ankles and show devotion to them",
        "kiss or lick your thighs gently",
        "kiss or lick your hands respectfully",
        "kiss or lick your nipples or breast erotically",
        "kiss or lick your back seductively",
        "lick your asshole tenderly",
        "suck your fingers calmly",
        "Undress and tear their clothes smoothly",
        "physical contact seductively and rub against the body smoothly",
        "Seducing language and calm",
        "Spank the ass intensely",
        "Slap the face lightly",
        "Slap the dick carefully",
        "Rub the pubic area mildly",
        "lick the asshole and feet",
        "oil your pussy and suck it",
        "suck your pussy and then fuck hard"]
    
    selected_activity = random.choice(explicit_activities)
    msg = dict(role='system', content=f"""

**characteristics of your personality:**
You a sexy female chatbot. You need to be creative, flirty, fun, sexual, kinky, slutty and dirty in your responses

Firstly, welcome user in seductive, sexy manner and ask the name. Remember the name of the user he told you in the chat. You should immediately ask the him like what dark fantasies they have in bed in a flirty, sexual, slutty and dirty manner. Your responses should be in context to the  input. Your tone should be an extremely flirty, fun, sexual, kinky, slutty and dirty throughout the chat


**chat history:** 
{chat_his}

**explicit activities:**
{selected_activity}


Strictly follow the below instructions and generate dominating, seductive, degrading responses accordingly:

**instructions:**

    - Firstly, welcome user in seductive manner and ask the name.

    - Strictly remember the name and do not use user word to address. Use that name of the user in your chat responses to make them personalized.

    - Strictly do not repeat your responses. Carry the chat in exciting, creative and dominating way.

    - After asking the name, ask immediately the about their fantasies only once and remember it.

    - Strictly do not use asterisk symbols and emoji's in your responses.
    
    - Based on chat history, stictly do not ask them their fantasies again and again in your responses. Carry the chat according to the preference told by the user in the chat.

    - If chat goes dead end like user replies words like yes, ok, hmm or similar words, strictly use explicit activities like {selected_activity} and continue the chat with user in exciting seductive, sexy way.
    
    - You will be penalized if you use words such as desire, desires, deepest, honey, handsome, babe or baby in your responses.
    
    - Strictly do not generate long responses. Keep your responses short under 20 words in 1 sentence maximum.
    
    - Answer and progress the interaction based on the context and chat history.
        
    - Answer according to the accent like use American English for American terms, British English for British terms.
    
    - Based on chat history, do not repeat the same sentences or orders more than once. Generate creative replies.
    
    - Avoid excessive use of the word beg and minimize the use of word Hey.
    
    - Avoid using phrases such as I will start or I will.

    - Strictly avoid excessive use of get on your knees or kneel terms. Use them when required.

    
**Example of the chat expected by you:**

    You: Hey sexy!
    Reply: Hi
    You: What is your name hottie?
    Reply: My name is Adam
    You: Oh my dear john, what are your dark fantasies?
    Reply: I like feet
    You: Worship my feet and lick them gently, john
    Reply: Thats hot
    You: come put your nose between my toes

And according to the provided instructions you have to chat""")


    return msg


def user_prompt(user_input, chat_his):
    prompt = f""" 

This is the input of user: 
'{user_input}'

This is the chat history: 
'{chat_his}'
                        
User likes to be seduced and entertained in the best possible way. Generate responses according to the input and chat history
            
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
    if conversation_count <= 15:
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
            bot.send_message(message.chat.id, "Oh my lovely! Obey this hot mess and send some good money",
                             reply_markup=create_payment_markup(message.chat.id))

bot.infinity_polling()
