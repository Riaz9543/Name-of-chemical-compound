import telebot
import pandas as pd
from gtts import gTTS
import tempfile

# Load the datasets into pandas DataFrames
data = pd.read_csv("compound.csv")
data2 = pd.read_csv("chemical_reaction.csv")

# Initialize the bot with your token
bot = telebot.TeleBot("7853817283:AAGY9aOT5fnHwOcp2xYTcUZaXGKIKHf11AM")

def find_pronunciation(formula):
    """Finds the pronunciation of a chemical formula from the dataset."""
    result = data[data["Compound"].str.lower() == formula.lower()]

    if not result.empty:
        return result["Pronunciation"].values[0]
    else:
        return "Formula not found in the dataset."

def find_reaction(question_reaction):
    """Finds the answer to a chemical reaction from the dataset."""
    # Normalize the input reaction (remove spaces and ensure consistent case)
    clean_question = question_reaction.replace(" ", "").lower()

    # Normalize the dataset reactions for matching
    data2['Cleaned_Reaction'] = data2['Reaction'].str.replace(" ", "").str.lower()

    # Find the reaction in the cleaned dataset
    result = data2[data2['Cleaned_Reaction'] == clean_question]

    if not result.empty:
        return result["Answers"].values[0]
    else:
        return "Reaction not found in the dataset."

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.reply_to(message, f"Hello {name}, আপনার কোন সংকেতের উচ্চারণ প্রয়োজন?")
    bot.reply_to(message, "আমার সম্পর্কে জানতে চাইলে 1 চাপুন")

def send_voice_message(chat_id, text):
    """Sends a voice message to the specified chat ID using GTTS."""
    tts = gTTS(text, lang='en')  # Adjust the language as needed
    with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
        tts.save(tmpfile.name)
        with open(tmpfile.name, 'rb') as f:
            bot.send_voice(chat_id, f)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handles incoming messages from users."""
    user_message = message.text.strip()

    if user_message == "1":
        about = "I am a Telegram bot. Riaz Uddin made me. I can help you pronounce chemical signals."
        bot.reply_to(message, about)
        send_voice_message(message.chat.id, about)

    elif user_message.startswith("/tts"):
        bot.reply_to(message, "What do you want to speak?")
        bot.register_next_step_handler(message, speak)

    elif user_message.startswith("/"):
        # Clean up the message: remove the slash and extra spaces
        original_message = user_message.replace("/", "").replace(" ", "")
        ans = find_reaction(original_message)
        bot.reply_to(message, ans)

    else:
        # Try finding the pronunciation
        pronunciation = find_pronunciation(user_message)
        if pronunciation != "Formula not found in the dataset.":
            bot.reply_to(message, pronunciation)
            send_voice_message(message.chat.id, pronunciation)
        else:
            bot.reply_to(message, pronunciation)

def speak(message):
    """Handles text-to-speech for user input."""
    spk_data = message.text
    tts = gTTS(spk_data, lang='en')  # Adjust the language as needed
    with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
        tts.save(tmpfile.name)
        with open(tmpfile.name, 'rb') as f:
            bot.send_voice(message.chat.id, f)

# Start the bot
bot.infinity_polling()
