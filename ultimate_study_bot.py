import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import google.generativeai as genai
from datetime import time

# लॉगिंग सेट करें
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("8997111684:AAF_UCmdi6DZuhYVLj0TDws7kS01PPFojgM")
GEMINI_API_KEY = os.getenv("AQ.Ab8RN6L2rhfMmRqzr3XjwmesU5BSt1i_IEqCcs_sT1MJhPSMxg")

# AI कॉन्फ़िगरेशन
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# सैंपल क्विज़ डेटाबेस
DAILY_QUIZ = [
    {
        "id": "q1",
        "question": "📝 **आज का PYQ (Science):**\n\nप्रकाश की गति (Speed of Light) सबसे अधिकतम किसमें होती है?",
        "options": [
            ["A) पानी (Water)", "wrong_water"],
            ["B) काँच (Glass)", "wrong_glass"],
            ["C) वैक्यूम (Vacuum)", "correct_vacuum"],
            ["D) हवा (Air)", "wrong_air"]
        ],
        "explanation": "सही जवाब **C) वैक्यूम (Vacuum)** है। वैक्यूम में प्रकाश की गति लगभग $3 \times 10^8 \text{ m/s}$ होती है, जहाँ कोई रुकावट नहीं होती।"
    }
]

# /start कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 नमस्ते! मैं आपका अल्टीमेट AI सुपर-ट्यूटर बोट हूँ।\n\n"
        "🚀 **सारे सब्जेक्ट्स के लिए मेरे फीचर्स:**\n"
        "1. **📸 फोटो/टेक्स्ट डाउट:** कोई भी सवाल या बुक की फोटो भेजें।\n"
        "2. **⏱️ /pomodoro :** 25 मिनट फोकस स्टडी टाइमर शुरू करें।\n"
        "3. **📝 /summary [विषय] :** किसी भी कठिन टॉपिक की शॉर्ट समरी पाएं।\n"
        "4. **🃏 /flashcard [विषय] :** याद रखने के लिए AI फ्लैशकार्ड्स बनाएं।\n"
        "5. **🎭 /roleplay [किरदार] :** किसी साइंटिस्ट/एक्सपर्ट टीचर के रूप में मुझसे बात करें।\n"
        "6. **🎯 /set_quiz :** डेली सुबह 9 बजे के क्विज़ बटन्स चालू करें।\n\n"
        "आप जो भी विषय (Maths, Science, History, Coding) पढ़ना चाहते हैं, बस शुरू हो जाइए!"
    )

# फीचर 1: टेक्स्ट और फोटो से डाउट सॉल्व करना + रोलप्ले मोड
async def handle_any_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("सोच रहा हूँ... 🧠")
    
    # चेक करें कि क्या यूजर ने कोई रोलप्ले सेट किया है
    role = context.user_data.get('role', 'an expert tutor')
    
    base_prompt = f"You are {role}. Solve this study doubt or explain the topic step-by-step in simple Hindi/Hinglish. Keep it highly engaging, educational, and easy to understand for a student."
    
    try:
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            image_parts = [{"mime_type": "image/jpeg", "data": bytes(photo_bytes)}]
            user_text = update.message.caption if update.message.caption else ""
            
            response = model.generate_content([f"{base_prompt}\nContext: {user_text}", image_parts[0]])
        else:
            user_text = update.message.text
            response = model.generate_content(f"{base_prompt}\nQuestion: {user_text}")
            
        await update.message.reply_text(response.text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("माफ़ कीजिएगा, समझने में थोड़ी दिक्कत हुई। कृपया दोबारा प्रयास करें।")

# फीचर 2: पोमोडोरो टाइमर (Pomodoro Timer)
async def pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏱️ **पोमोडोरो सेशन शुरू!** अगले 25 मिनट के लिए सब बंद करके पढ़ाई पर फोकस करें। मैं आपको ब्रेक के समय याद दिलाऊंगा। ऑल द बेस्ट! 👍")
    
    # 25 मिनट का इंतजार (टेस्टिंग के लिए आप इसे कम कर सकते हैं, जैसे 10 या 15 सेकंड)
    await asyncio.sleep(25 * 60)
    
    await update.message.reply_text("🎉 **25 मिनट पूरे हुए!** बेहतरीन काम। अब 5 मिनट का छोटा सा ब्रेक (Short Break) लीजिए। अपनी आँखें बंद करें और थोड़ा पानी पिएं! 🥤")
    
    await asyncio.sleep(5 * 60)
    await update.message.reply_text("🔔 **ब्रेक खत्म!** क्या आप अगला सेशन शुरू करने के लिए तैयार हैं? दोबारा शुरू करने के लिए /pomodoro टाइप करें।")

# फीचर 3: स्मार्ट समरी (Smart Summary)
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("कृपया कमांड के साथ विषय भी लिखें। जैसे: `/summary Photosynthesis`")
        return
        
    await update.message.reply_text("शॉर्ट नोट्स तैयार कर रहा हूँ... 📝")
    prompt = f"Create a short, high-yield summary of the topic '{topic}' in bullet points using simple Hindi/Hinglish. Include key concepts, formula (if any), and why it is important for exams."
    response = model.generate_content(prompt)
    await update.message.reply_text(response.text, parse_mode="Markdown")

# फीचर 4: फ्लैशकार्ड (Flashcards)
async def flashcard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("कृपया विषय का नाम लिखें। जैसे: `/flashcard Indian Constitution`")
        return
        
    await update.message.reply_text("फ्लैशकार्ड्स बना रहा हूँ... 🃏")
    prompt = f"Create 3 interactive Flashcards (Question and Answer format) for memorizing '{topic}' easily. Write in Hindi/Hinglish."
    response = model.generate_content(prompt)
    await update.message.reply_text(response.text, parse_mode="Markdown")

# फीचर 5: AI रोलप्ले टीचर (Roleplay)
async def roleplay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role_choice = " ".join(context.args)
    if not role_choice:
        await update.message.reply_text("कृपया बताएं कि आप मुझे क्या बनाना चाहते हैं? जैसे: `/roleplay Albert Einstein` या `/roleplay Strict IAS Officer`")
        return
    
    context.user_data['role'] = role_choice
    await update.message.reply_text(f"🎭 **रोलप्ले मोड ऑन!** अब मैं **{role_choice}** की तरह बात करूँगा। मुझसे कोई भी सवाल पूछ कर देखिए!")

# फीचर 6: डेली क्विज़ और बटन हैंडलर (पहले की तरह)
async def send_daily_quiz(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    quiz = DAILY_QUIZ[0]
    keyboard = [[InlineKeyboardButton(opt[0], callback_data=f"{quiz['id']}_{opt[1]}")] for opt in quiz["options"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=job.chat_id, text=quiz["question"], reply_markup=reply_markup)

async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    quiz = DAILY_QUIZ[0]
    
    response_text = f"🎉 **बिल्कुल सही जवाब!**\n\n{quiz['explanation']}" if "correct" in data else f"❌ **गलत जवाब!**\n\n{quiz['explanation']}"
    await query.edit_message_text(text=f"{quiz['question']}\n\n---\n\n{response_text}", parse_mode="Markdown")

async def set_daily_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.job_queue.run_daily(send_daily_quiz, time(9, 0, 0), chat_id=chat_id, name=str(chat_id))
    await update.message.reply_text("✅ डेली क्विज़ सेट हो गया है!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # सभी कमांड्स लिंक करना
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pomodoro", pomodoro))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("flashcard", flashcard))
    app.add_handler(CommandHandler("roleplay", roleplay))
    app.add_handler(CommandHandler("set_quiz", set_daily_timer))
    app.add_handler(CallbackQueryHandler(button_click_handler))
    
    # टेक्स्ट और फोटो के लिए कॉमन मैसेंजर
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_any_input))

    print("🚀 आपका अल्टीमेट AI स्टडी बोट पूरी तरह से तैयार है...")
    app.run_polling()

if __name__ == '__main__':
    main()

