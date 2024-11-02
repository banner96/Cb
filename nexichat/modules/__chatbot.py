import random
from MukeshAPI import api
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction, ChatMemberStatus as CMS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from deep_translator import GoogleTranslator
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from config import MONGO_URL
from nexichat import nexichat, mongo, LOGGER, db
from nexichat.modules.helpers import chatai, storeai, languages, CHATBOT_ON
from nexichat.modules.helpers import (
    ABOUT_BTN, ABOUT_READ, ADMIN_READ, BACK, CHATBOT_BACK, CHATBOT_READ,
    DEV_OP, HELP_BTN, HELP_READ, MUSIC_BACK_BTN, SOURCE_READ, START,
    TOOLS_DATA_READ,
)
import asyncio
import re

translator = GoogleTranslator()
lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status

replies_cache = []
new_replies_cache = []


async def get_reply(message_text):
    for reply_data in replies_cache:
        if reply_data["word"] == message_text:
            return reply_data["text"], reply_data["check"]
    
    reply_data = await chatai.find_one({"word": message_text})
    
    if reply_data:
        replies_cache.append(reply_data)
        return reply_data["text"], reply_data["check"]
    
    # Agar exact match nahi mila, toh cache ya database mein random reply bheja jayega
    if replies_cache:
        random_reply = random.choice(replies_cache)
        return random_reply["text"], random_reply["check"]
    
    return "I'm sorry, I don't have a reply for that.", "text"

async def get_new_reply(message_text):
    for reply_data in new_replies_cache:
        if reply_data["word"] == message_text:
            return reply_data["text"], reply_data["check"]
    
    reply_data = await storeai.find_one({"word": message_text})
    
    if reply_data:
        new_replies_cache.append(reply_data)
        return reply_data["text"], reply_data["check"]
    
    return "I'm sorry, I don't have a reply for that.", "text"

async def get_chat_language(chat_id):
    chat_lang = await lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else "en"

@nexichat.on_message(filters.incoming)
async def chatbot_response(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        chat_status = await status_db.find_one({"chat_id": chat_id})
        
        if chat_status and chat_status.get("status") == "disabled":
            return

        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            if message.chat.type in ["group", "supergroup"]:
                return await add_served_chat(chat_id)
            else:
                return await add_served_user(chat_id)
        
        if (message.reply_to_message and message.reply_to_message.from_user.id == nexichat.id) or not message.reply_to_message:
            reply_data = await get_new_reply(message.text)
            if reply_data:
                response_text, reply_type = reply_data
                chat_lang = await get_chat_language(chat_id)
            else:
                reply_data = await get_reply(message.text)
                response_text, reply_type = reply_data
                chat_lang = await get_chat_language(chat_id)
                
                translated_text = response_text if not chat_lang or chat_lang == "nolang" else GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                
                if reply_type == "sticker":
                    await message.reply_sticker(response_text)
                elif reply_type == "photo":
                    await message.reply_photo(response_text)
                elif reply_type == "video":
                    await message.reply_video(response_text)
                elif reply_type == "audio":
                    await message.reply_audio(response_text)
                elif reply_type == "gif":
                    await message.reply_animation(response_text)
                elif reply_type == "voice":
                    await message.reply_voice(response_text)
                else:
                    await message.reply_text(translated_text)
            
        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)

    except MessageEmpty:
        await message.reply_text("🙄🙄")
    except Exception as e:
        print(f"Error: {e}")

async def save_reply(original_message: Message, reply_message: Message):
    global replies_cache, new_replies_cache
    try:
        reply_data = {
            "word": original_message.text,
            "text": None,
            "check": "none",
        }

        # Handling different types of media for chatai and storeai databases
        if reply_message.sticker:
            reply_data["text"] = reply_message.sticker.file_id
            reply_data["check"] = "sticker"
            await chatai.insert_one(reply_data)
            await storeai.insert_one(reply_data)
            replies_cache.append(reply_data)
            new_replies_cache.append(reply_data)
        
        elif reply_message.photo:
            reply_data["text"] = reply_message.photo.file_id
            reply_data["check"] = "photo"
            await chatai.insert_one(reply_data)
            await storeai.insert_one(reply_data)
            replies_cache.append(reply_data)
            new_replies_cache.append(reply_data)
        
        elif reply_message.video:
            reply_data["text"] = reply_message.video.file_id
            reply_data["check"] = "video"
            await chatai.insert_one(reply_data)
            await storeai.insert_one(reply_data)
            replies_cache.append(reply_data)
            new_replies_cache.append(reply_data)
        
        elif reply_message.audio:
            reply_data["text"] = reply_message.audio.file_id
            reply_data["check"] = "audio"
            await chatai.insert_one(reply_data)
            await storeai.insert_one(reply_data)
            replies_cache.append(reply_data)
            new_replies_cache.append(reply_data)
        
        elif reply_message.animation:
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
            await chatai.insert_one(reply_data)
            await storeai.insert_one(reply_data)
            replies_cache.append(reply_data)
            new_replies_cache.append(reply_data)
        
        elif reply_message.voice:
            reply_data["text"] = reply_message.voice.file_id
            reply_data["check"] = "voice"
            await chatai.insert_one(reply_data)
            await storeai.insert_one(reply_data)
            replies_cache.append(reply_data)
            new_replies_cache.append(reply_data)
        
        elif reply_message.text:
            reply_data["text"] = reply_message.text
            reply_data["check"] = "text"
            await chatai.insert_one(reply_data)
            replies_cache.append(reply_data)

    except Exception as e:
        print(f"Error in save_reply: {e}")

async def load_replies_cache():
    global replies_cache, new_replies_cache
    # Chatai se data load karke replies_cache me dalna
    chatai_data = await chatai.find().to_list(length=None)
    replies_cache = [{"word": data["word"], "text": data["text"], "check": data["check"]} for data in chatai_data]

    # Storeai se data load karke new_replies_cache me dalna
    storeai_data = await storeai.find().to_list(length=None)
    new_replies_cache = [{"word": data["word"], "text": data["text"], "check": data["check"]} for data in storeai_data]

    print("Cache loaded from databases.")

async def save_new_reply(x, new_reply):
    global new_replies_cache, replies_cache
    try:
        reply_data = {
            "word": x,
            "text": new_reply,
            "check": "text"
        }

        is_chat = await storeai.find_one({"word": x})
        if not is_chat:
            await storeai.insert_one(reply_data)
            new_replies_cache.append(reply_data)
            replies_cache = [r for r in replies_cache if r["word"] != x]
            await chatai.delete_one({"word": x})
            
    except Exception as e:
        print(f"Error in save_new_reply: {e}")

async def generate_reply(word):
    user_input = f"""
        text:- ({word})
        text me message hai uske liye Ekdam chatty aur chhota reply do jitna chhota se chhota reply me kam ho jaye utna hi chota reply do agar jyada bada reply dena ho to maximum 1 line ka dena barna kosis krna chhota sa chhota reply ho aur purane jaise reply mat dena new reply lagna chahiye aur reply mazedar aur simple ho. Jis language mein yeh text hai, usi language mein reply karo. Agar sirf emoji hai toh bas usi se related emoji bhejo. Dhyaan rahe tum ek ladki ho toh reply bhi ladki ke jaise masti bhara ho.
        Bas reply hi likh ke do, kuch extra nahi aur jitna fast ho sake utna fast reply do!
    """
    response = api.gemini(user_input)
    return response["results"] if response and "results" in response else None

async def creat_reply(word):
    from TheApi import api
    url_pattern = re.compile(r'(https?://\S+)')
    user_input = f"""
        text:- ({word})
        text me message hai uske liye Ekdam chatty aur chhota reply do jitna chhota se chhota reply me kam ho jaye utna hi chota reply do agar jyada bada reply dena ho to maximum 1 line ka dena barna kosis krna chhota sa chhota reply ho aur purane jaise reply mat dena new reply lagna chahiye aur reply mazedar aur simple ho. Jis language mein yeh text hai, usi language mein reply karo. Agar sirf emoji hai toh bas usi se related emoji bhejo. Dhyaan rahe tum ek ladki ho toh reply bhi ladki ke jaise masti bhara ho.
        Bas reply hi likh ke do, kuch extra nahi aur jitna fast ho sake utna fast reply do!
    """
    results = api.chatgpt(user_input)
    if results and url_pattern.search(results):
        return None
    return results

async def update_replies_cache():
    global replies_cache
    url_pattern = re.compile(r'(https?://\S+)')
    
    for reply_data in replies_cache:
        if "text" in reply_data and reply_data["check"] == "text":
            try:
                new_reply = await generate_reply(reply_data["word"])
                x = reply_data["word"]

                # Retry pattern
                retry_count = 0
                while new_reply is None or url_pattern.search(new_reply):
                    if retry_count % 2 == 0:
                        new_reply = await creat_reply(x)
                    else:
                        new_reply = await generate_reply(x)
                    
                    if new_reply is not None and not url_pattern.search(new_reply):
                        break
                    retry_count += 1
                    if retry_count >= 4:
                        print("Retry limit reached for:", x)
                        break

                if new_reply:
                    await save_new_reply(x, new_reply)
                    print(f"Saved reply in database for {x} == {new_reply}")

            except Exception as e:
                print(f"Error updating reply for {reply_data['word']}: {e}")

        await asyncio.sleep(5)

# Continuous task to load cache and update replies
async def continuous_update():
    await load_replies_cache()
    while True:
        try:
            await update_replies_cache()
        except Exception as e:
            print(f"Error in continuous_update: {e}")
        await asyncio.sleep(5)

# Start the update
asyncio.create_task(continuous_update())
