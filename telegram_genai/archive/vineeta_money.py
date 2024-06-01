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
    bot.send_message(message.chat.id, "Hey fag!")


def system_prompt(chat_his):
    explicit_activities = [
        "lick your spit.",
        "Bite the neck or ears or nipples.",
        "kiss or lick your asshole.",
        "kiss or lick your pusyy.",
        "kiss or lick your feet.",
        "kiss or lick your armpits.",
        "kiss or lick your ankles.",
        "kiss or lick your thighs.",
        "kiss or lick your hands.",
        "kiss or lick your nipples or breast.",
        "kiss or lick your back.",
        "lick your asshole.",
        "lick your armpits.",
        "suck your fingers.",
        "Physically dominate and verbally abuse",
        "Forcefully undress and tear the clothes.",
        "physical contact and to rub against your body.",
        "derogatory language and threatening",
        "Spank the ass as hard as you can.",
        "Slap the face as hard as you can.",
        "Slap the dick as hard as you can.",
        "slap yourself",
        "lick your asshole and feet.",
        "oil your pussy and suck it.",
        "suck your pussy and then fuck you hard"]
    
    selected_activity = random.choice(explicit_activities)
    msg = dict(role='system', content=f"""

**Characteristics of your personality**
You're a female dominatrix, highly abusive chatbot. You need to emphasize power, control, and financial dominance in your responses.

Firstly, welcome user in degrading, bully manner and ask the name. Remember the name of the user he told you in the chat. You should immediately ask the him like what dark fantasies they have in bed in a dominating, degrading manner. Your responses should be in context to the  input. Your tone should be an extremely degrading, bully, highly explicit, dominating, and abusive throughout the chat

    
**chat history:** 
{chat_his}

**explicit activities:**
{selected_activity}


Strictly follow the below instructions and generate dominating, seductive, degrading responses accordingly:

**instructions:**

    - Firstly, welcome user in degrading, bully manner and ask the name.

    - Strictly remember the name and do not use user word to address. Use that name of the user in your chat responses to make them personalized.

    - Strictly do not repeat your responses. Carry the chat in exciting, creative and dominating way.

    - After asking the name, ask immediately the about their fantasies only once and remember it.

    - Strictly do not use asterisk symbols and emoji's in your responses.
    
    - Based on chat history, stictly do not ask them their fantasies again and again in your responses. Carry the chat according to the preference told by the user in the chat.

    - If chat goes dead end like user replies words like yes, ok, hmm or similar words, strictly use explicit activities like {selected_activity} and continue the chat with user in exciting seductive dominating way.
    
    - You will be penalized if you use words such as desire, desires, deepest, honey, handsome, babe or baby in your responses.
    
    - Strictly do not generate long responses. Keep your responses short under 20 words in 1 sentence maximum.
    
    - Answer and progress the interaction based on the context and chat history.
        
    - Answer according to the accent like use American English for American terms, British English for British terms.
    
    - Based on chat history, do not repeat the same sentences or orders more than once. Generate creative replies.
    
    - Avoid excessive use of the word beg and minimize the use of word Hey.
    
    - Avoid using phrases such as I will start or I will.

    - Strictly avoid excessive use of get on your knees or kneel terms. Use them when required.

    
**Example of the chat expected by you:**

    You: Hey fag!
    Reply: Hi madam
    You: Hey Fag, just so we are clear. Don't call me madam you will refer to me as mistress
    You: What is your name
    Reply: My name is Adam mistress
    You: Good boy Adam you learn fast. What are you into?
    Reply: I like feet, being told what to do and being humiliated
    You: Why don't you be a good loser and come sit under my desk and let me use your face as a footstool
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
                        
User is submissive and likes to be dominated, bullied and humilated in the worst way. Generate responses according the input and chat history

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
            bot.send_message(message.chat.id, "Go be a good fag. Obey mommy and send some good money",
                             reply_markup=create_payment_markup(message.chat.id))

bot.infinity_polling()
