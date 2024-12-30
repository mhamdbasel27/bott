import telebot
import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# التوكن الخاص بالبوت
BOT_TOKEN = "7408536418:AAFW9p8ljYYzI7RxtN96vkoPG9qTV4MD9Sw"
ADMIN_ID = 464292096  # ضع هنا رقم معرفك الشخصي (Telegram User ID)

bot = telebot.TeleBot(BOT_TOKEN)

# ملف البيانات
DATA_FILE = "data.json"
USERS_FILE = "users.json"

# إنشاء الملفات إذا لم تكن موجودة
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"materials": {}}, f)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({"users": []}, f)

# تحميل البيانات

def load_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    if "materials" not in data:
        data["materials"] = {}
        save_data(data)
    return data

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# حفظ البيانات

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# أوامر المدير

@bot.message_handler(commands=['add_material'])
def add_material(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "أدخل الرمز الفريد للمادة الجديدة:")
        bot.register_next_step_handler(msg, process_add_material)
    else:
        bot.send_message(message.chat.id, "هذا الأمر مخصص للمدير فقط.")

def process_add_material(message):
    material_code = message.text.strip()
    data = load_data()
    if material_code in data["materials"]:
        bot.send_message(message.chat.id, "هذه المادة موجودة بالفعل.")
    else:
        data["materials"][material_code] = []
        save_data(data)
        bot.send_message(message.chat.id, f"تمت إضافة المادة برمز: {material_code}.")

@bot.message_handler(commands=['delete_material'])
def delete_material(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "أدخل الرمز الفريد للمادة التي تريد حذفها:")
        bot.register_next_step_handler(msg, process_delete_material)
    else:
        bot.send_message(message.chat.id, "هذا الأمر مخصص للمدير فقط.")

def process_delete_material(message):
    material_code = message.text.strip()
    data = load_data()
    if material_code in data["materials"]:
        del data["materials"][material_code]
        save_data(data)
        bot.send_message(message.chat.id, f"تم حذف المادة والمنهج الخاص بها برمز: {material_code}.")
    else:
        bot.send_message(message.chat.id, "المادة غير موجودة.")

@bot.message_handler(commands=['add_curriculum'])
def add_curriculum(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "أدخل الرمز الفريد للمادة لإضافة المنهج:")
        bot.register_next_step_handler(msg, process_add_curriculum)
    else:
        bot.send_message(message.chat.id, "هذا الأمر مخصص للمدير فقط.")

def process_add_curriculum(message):
    material_code = message.text.strip()
    data = load_data()
    if material_code in data["materials"]:
        msg = bot.send_message(message.chat.id, "أرسل المنهج (ملف PDF أو فيديو أو صورة أو مستند):")
        bot.register_next_step_handler(msg, lambda m: save_curriculum(m, material_code))
    else:
        bot.send_message(message.chat.id, "المادة غير موجودة.")

def save_curriculum(message, material_code):
    data = load_data()
    if message.content_type in ["document", "photo", "video"]:
        file_id = None
        if message.content_type == "document":
            file_id = message.document.file_id
        elif message.content_type == "photo":
            file_id = message.photo[-1].file_id
        elif message.content_type == "video":
            file_id = message.video.file_id

        data["materials"][material_code].append({
            "type": message.content_type,
            "file_id": file_id
        })
        save_data(data)
        bot.send_message(message.chat.id, "تمت إضافة المنهج بنجاح.")
    else:
        bot.send_message(message.chat.id, "نوع الملف غير مدعوم. أرسل ملف PDF أو فيديو أو صورة.")

# واجهة المستخدم

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("أدخل رمز المادة", callback_data="enter_material_code"))
    markup.add(InlineKeyboardButton("جميع المواد", callback_data="list_materials"))
    markup.add(InlineKeyboardButton("تواصل مع المطور", url="https://t.me/Mohamedbasel2772"))
    bot.send_message(message.chat.id, "مرحبًا! اختر من القائمة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "enter_material_code")
def enter_material_code(call):
    msg = bot.send_message(call.message.chat.id, "أدخل رمز المادة:")
    bot.register_next_step_handler(msg, process_enter_material_code)

def process_enter_material_code(message):
    material_code = message.text.strip()
    data = load_data()
    if material_code in data["materials"]:
        curriculum = data["materials"][material_code]
        if curriculum:
            for item in curriculum:
                if item["type"] == "document":
                    bot.send_document(message.chat.id, item['file_id'])
                elif item["type"] == "photo":
                    bot.send_photo(message.chat.id, item['file_id'])
                elif item["type"] == "video":
                    bot.send_video(message.chat.id, item['file_id'])
        else:
            bot.send_message(message.chat.id, "لا يوجد منهج لهذه المادة.")
    else:
        bot.send_message(message.chat.id, "رمز المادة غير موجود.")

@bot.callback_query_handler(func=lambda call: call.data == "list_materials")
def list_materials(call):
    data = load_data()
    materials = data["materials"].keys()
    if materials:
        markup = InlineKeyboardMarkup()
        for material in materials:
            markup.add(InlineKeyboardButton(material, callback_data=f"view_material:{material}"))
        bot.send_message(call.message.chat.id, "اختر المادة لعرض المنهج:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "لا توجد مواد مضافة حتى الآن.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("view_material:"))
def view_material(call):
    material_code = call.data.split(":")[1]
    data = load_data()
    curriculum = data["materials"].get(material_code, [])
    if curriculum:
        for item in curriculum:
            if item["type"] == "document":
                bot.send_document(call.message.chat.id, item['file_id'])
            elif item["type"] == "photo":
                bot.send_photo(call.message.chat.id, item['file_id'])
            elif item["type"] == "video":
                bot.send_video(call.message.chat.id, item['file_id'])
    else:
        bot.send_message(call.message.chat.id, "لا يوجد منهج لهذه المادة.")

# إرسال رسالة جماعية

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "أرسل الرسالة أو الوسائط التي تريد إرسالها لجميع المستخدمين:")
        bot.register_next_step_handler(msg, process_broadcast)
    else:
        bot.send_message(message.chat.id, "هذا الأمر مخصص للمدير فقط.")

def process_broadcast(message):
    users = load_users()["users"]
    if not users:
        bot.send_message(message.chat.id, "لا يوجد مستخدمون لإرسال الرسائل.")
        return

    success_count = 0
    for user in users:
        try:
            if message.content_type == "text":
                bot.send_message(user, message.text)
            elif message.content_type == "photo":
                bot.send_photo(user, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == "video":
                bot.send_video(user, message.video.file_id, caption=message.caption)
            success_count += 1
        except Exception as e:
            print(f"Error sending to {user}: {e}")

    bot.send_message(message.chat.id, f"تم إرسال الرسالة إلى {success_count} مستخدم.")

# تشغيل البوت
print("Bot is running...")
bot.polling(none_stop=True)
