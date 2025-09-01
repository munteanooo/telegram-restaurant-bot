import json
import os
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

MENU_ITEMS = {
    "pizza_margherita": {"name": "Pizza Margherita", "price": 25.0},
    "salata_caesar": {"name": "Salată Caesar", "price": 18.0},
    "supa_pui": {"name": "Supă de pui", "price": 12.0},
    "friptura_vita": {"name": "Friptură de vită", "price": 35.0},
    "cheesecake": {"name": "Cheesecake", "price": 15.0}
}

DATA_FILE = "restaurant_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    data = load_data()
    str_user_id = str(user_id)
    if str_user_id not in data:
        data[str_user_id] = {
            "current_order": {},
            "last_completed_order": None,
            "order_type": None,
            "time": None,
            "people_count": None
        }
        save_data(data)
    return data[str_user_id]

def update_user_data(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🍽️ Meniu", callback_data="menu")],
        [InlineKeyboardButton("📅 Rezervare loc", callback_data="reservation")],
        [InlineKeyboardButton("✅ Finalizează comanda", callback_data="finalize_order")],
        [InlineKeyboardButton("❌ Anulare rezervare", callback_data="cancel_reservation")],
        [InlineKeyboardButton("📌 Statut rezervare", callback_data="order_status")],
        [InlineKeyboardButton("📞 Contacte manager", callback_data="contacts")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_menu_keyboard(user_data=None):
    keyboard = []
    for item_id, item_info in MENU_ITEMS.items():
        display_text = f"{item_info['name']} - {item_info['price']} MDL"
        if user_data and item_id in user_data.get("current_order", {}):
            quantity = user_data["current_order"][item_id]
            display_text += f" (🛒 x{quantity})"
        keyboard.append([InlineKeyboardButton(display_text, callback_data=f"item_{item_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Înapoi", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def get_quantity_keyboard(item_id):
    keyboard = [
        [
            InlineKeyboardButton("x1", callback_data=f"qty_{item_id}_1"),
            InlineKeyboardButton("x2", callback_data=f"qty_{item_id}_2"),
            InlineKeyboardButton("x3", callback_data=f"qty_{item_id}_3"),
            InlineKeyboardButton("x5", callback_data=f"qty_{item_id}_5")
        ],
        [
            InlineKeyboardButton("x10", callback_data=f"qty_{item_id}_10"),
            InlineKeyboardButton("x15", callback_data=f"qty_{item_id}_15"),
            InlineKeyboardButton("x20", callback_data=f"qty_{item_id}_20"),
            InlineKeyboardButton("x50", callback_data=f"qty_{item_id}_50")
        ],
        [InlineKeyboardButton("🔙 Înapoi la meniu", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_reservation_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("🍽️ La masă", callback_data="reservation_table")],
        [InlineKeyboardButton("📦 La pachet", callback_data="reservation_takeaway")],
        [InlineKeyboardButton("🔙 Înapoi", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_time_keyboard():
    keyboard = []
    times = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
    row = []
    for i, time in enumerate(times):
        row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Înapoi", callback_data="reservation")])
    return InlineKeyboardMarkup(keyboard)

def get_people_keyboard():
    keyboard = []
    for i in range(1, 11):
        if i <= 5:
            if (i - 1) % 5 == 0:
                row = []
            row.append(InlineKeyboardButton(str(i), callback_data=f"people_{i}"))
            if i % 5 == 0 or i == 5:
                keyboard.append(row)
        else:
            if (i - 6) % 5 == 0:
                row = []
            row.append(InlineKeyboardButton(str(i), callback_data=f"people_{i}"))
            if i == 10:
                keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Înapoi", callback_data="reservation")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "🍽️ Bine ați venit la Restaurant Cezar!\n\nVă rugăm să alegeți o opțiune din meniul de mai jos:"
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    
    if query.data == "menu":
        await query.edit_message_text("🍽️ Meniu Restaurant Cezar:\n\nAlegeți produsul dorit:", reply_markup=get_menu_keyboard(user_data))
    
    elif query.data == "back_to_main":
        welcome_text = "🍽️ Bine ați venit la Restaurant Cezar!\n\nVă rugăm să alegeți o opțiune din meniul de mai jos:"
        await query.edit_message_text(welcome_text, reply_markup=get_main_menu_keyboard())
    
    elif query.data.startswith("item_"):
        item_id = query.data.replace("item_", "")
        item_info = MENU_ITEMS[item_id]
        current_qty = user_data["current_order"].get(item_id, 0)
        qty_text = f" (În coș: {current_qty})" if current_qty > 0 else ""
        text = f"🍽️ {item_info['name']}\nPreț: {item_info['price']} MDL{qty_text}\n\nAlegeți cantitatea de adăugat:"
        await query.edit_message_text(text, reply_markup=get_quantity_keyboard(item_id))
    
    elif query.data.startswith("qty_"):
        parts = query.data.replace("qty_", "").split("_")
        item_id = "_".join(parts[:-1])
        quantity = int(parts[-1])
        
        if item_id not in user_data["current_order"]:
            user_data["current_order"][item_id] = 0
        user_data["current_order"][item_id] += quantity
        update_user_data(user_id, user_data)
        
        await query.edit_message_text("🍽️ Meniu Restaurant Cezar:\n\nAlegeți produsul dorit:", reply_markup=get_menu_keyboard(user_data))
    
    elif query.data == "reservation":
        await query.edit_message_text("📅 Rezervare loc:\n\nAlegeți tipul comenzii:", reply_markup=get_reservation_type_keyboard())
    
    elif query.data == "reservation_table":
        user_data["order_type"] = "La masă"
        update_user_data(user_id, user_data)
        await query.edit_message_text("🕐 Alegeți ora pentru rezervare:", reply_markup=get_time_keyboard())
    
    elif query.data == "reservation_takeaway":
        user_data["order_type"] = "La pachet"
        update_user_data(user_id, user_data)
        await query.edit_message_text("🕐 Alegeți ora pentru ridicare:", reply_markup=get_time_keyboard())
    
    elif query.data.startswith("time_"):
        time = query.data.replace("time_", "")
        user_data["time"] = time
        update_user_data(user_id, user_data)
        
        if user_data["order_type"] == "La masă":
            await query.edit_message_text("👥 Alegeți numărul de persoane:", reply_markup=get_people_keyboard())
        else:
            user_data["people_count"] = 1
            update_user_data(user_id, user_data)
            welcome_text = "🍽️ Bine ați venit la Restaurant Cezar!\n\nVă rugăm să alegeți o opțiune din meniul de mai jos:"
            await query.edit_message_text(welcome_text, reply_markup=get_main_menu_keyboard())
    
    elif query.data.startswith("people_"):
        people_count = int(query.data.replace("people_", ""))
        user_data["people_count"] = people_count
        update_user_data(user_id, user_data)
        welcome_text = "🍽️ Bine ați venit la Restaurant Cezar!\n\nVă rugăm să alegeți o opțiune din meniul de mai jos:"
        await query.edit_message_text(welcome_text, reply_markup=get_main_menu_keyboard())
    
    elif query.data == "finalize_order":
        if not user_data["current_order"] and not user_data["order_type"]:
            await query.edit_message_text("❌ Nu aveți nicio comandă sau rezervare activă!", reply_markup=get_main_menu_keyboard())
            return
        
        order_text = "✅ COMANDĂ FINALIZATĂ\n\n"
        order_text += "📋 Detalii comandă:\n"
        order_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        
        if user_data["order_type"]:
            order_text += f"📍 Tip comandă: {user_data['order_type']}\n"
            order_text += f"🕐 Ora: {user_data['time']}\n"
            if user_data["order_type"] == "La masă":
                order_text += f"👥 Numărul de persoane: {user_data['people_count']}\n"
            order_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        
        total = 0
        if user_data["current_order"]:
            order_text += "🍽️ Produse comandate:\n"
            for item_id, quantity in user_data["current_order"].items():
                item_info = MENU_ITEMS[item_id]
                subtotal = item_info["price"] * quantity
                total += subtotal
                order_text += f"• {item_info['name']} x{quantity} = {subtotal} MDL\n"
            order_text += f"━━━━━━━━━━━━━━━━━━━━\n"
            order_text += f"💰 TOTAL: {total} MDL\n"
        
        order_text += f"📅 Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        order_text += f"━━━━━━━━━━━━━━━━━━━━\n"
        order_text += "Mulțumim pentru comandă! Vă așteptăm la Restaurant Cezar!"
        
        user_data["last_completed_order"] = {
            "order_type": user_data["order_type"],
            "time": user_data["time"],
            "people_count": user_data["people_count"],
            "items": user_data["current_order"].copy(),
            "total": total,
            "date": datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        
        user_data["current_order"] = {}
        user_data["order_type"] = None
        user_data["time"] = None
        user_data["people_count"] = None
        update_user_data(user_id, user_data)
        
        await query.edit_message_text(order_text, reply_markup=get_main_menu_keyboard())
    
    elif query.data == "cancel_reservation":
        user_data["current_order"] = {}
        user_data["order_type"] = None
        user_data["time"] = None
        user_data["people_count"] = None
        update_user_data(user_id, user_data)
        await query.edit_message_text("❌ Rezervarea a fost anulată complet!", reply_markup=get_main_menu_keyboard())
    
    elif query.data == "order_status":
        status_text = "📌 STATUT REZERVARE\n\n"
        
        if user_data["current_order"] or user_data["order_type"]:
            status_text += "🔄 Comandă curentă (în progres):\n"
            status_text += f"━━━━━━━━━━━━━━━━━━━━\n"
            
            if user_data["order_type"]:
                status_text += f"📍 Tip comandă: {user_data['order_type']}\n"
                status_text += f"🕐 Ora: {user_data['time']}\n"
                if user_data["order_type"] == "La masă" and user_data["people_count"]:
                    status_text += f"👥 Numărul de persoane: {user_data['people_count']}\n"
            
            if user_data["current_order"]:
                status_text += "🍽️ Produse în coș:\n"
                current_total = 0
                for item_id, quantity in user_data["current_order"].items():
                    item_info = MENU_ITEMS[item_id]
                    subtotal = item_info["price"] * quantity
                    current_total += subtotal
                    status_text += f"• {item_info['name']} x{quantity} = {subtotal} MDL\n"
                status_text += f"💰 Total curent: {current_total} MDL\n"
        else:
            status_text += "❌ Nu aveți nicio comandă curentă.\n"
        
        if user_data["last_completed_order"]:
            status_text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
            status_text += "✅ Ultima comandă finalizată:\n"
            last_order = user_data["last_completed_order"]
            if last_order["order_type"]:
                status_text += f"📍 Tip comandă: {last_order['order_type']}\n"
                status_text += f"🕐 Ora: {last_order['time']}\n"
                if last_order["order_type"] == "La masă":
                    status_text += f"👥 Numărul de persoane: {last_order['people_count']}\n"
            if last_order["items"]:
                status_text += "🍽️ Produse:\n"
                for item_id, quantity in last_order["items"].items():
                    item_info = MENU_ITEMS[item_id]
                    subtotal = item_info["price"] * quantity
                    status_text += f"• {item_info['name']} x{quantity} = {subtotal} MDL\n"
                status_text += f"💰 Total: {last_order['total']} MDL\n"
            status_text += f"📅 Data: {last_order['date']}\n"
        
        await query.edit_message_text(status_text, reply_markup=get_main_menu_keyboard())
    
    elif query.data == "contacts":
        contact_text = "📞 CONTACTE MANAGER\n\n"
        contact_text += "👨‍💼 Manager Restaurant Cezar\n"
        contact_text += "━━━━━━━━━━━━━━━━━━━━\n"
        contact_text += "📱 Telefon: +40 123 456 789\n"
        contact_text += "📧 Email: manager@restaurantcezar.ro\n"
        contact_text += "🕐 Program: 12:00 - 23:00\n"
        contact_text += "📍 Adresă: Str. Exemplu nr. 1, București\n"
        contact_text += "━━━━━━━━━━━━━━━━━━━━\n"
        contact_text += "Sunați pentru rezervări speciale sau evenimente private!"
        
        await query.edit_message_text(contact_text, reply_markup=get_main_menu_keyboard())

def main():
    application = Application.builder().token("8329954152:AAHtARyQyo82jDVGZYkyozRTZKOeVTvsDZA").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()