# 🍽️ Telegram Restaurant Bot 🤖

A Telegram bot for restaurant orders and table reservations.  
Easy to use, friendly, and simple to extend.  

---

## ✨ Features
- 📋 Place orders directly in chat  
- 🍷 Book a table for a specific date and time  
- 💬 Friendly automatic responses for customers  
- 🔒 Configurable with environment variables (no token leaks)  

---

## 🚀 Run the bot locally

1. Clone the repository:
   \\\ash
   git clone https://github.com/munteanooo/telegram-restaurant-bot.git
   cd telegram-restaurant-bot
   \\\

2. (Optional but recommended) Create a virtual environment:
   \\\ash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   \\\

3. Install dependencies:
   \\\ash
   pip install -r requirements.txt
   \\\

4. Create a .env file in the project root with your BotFather token:
   \\\
   TELEGRAM_BOT_TOKEN=your_token_here
   \\\

5. Run the bot:
   \\\ash
   python bot.py
   \\\

---

## 📂 Project structure
\\\
telegram-restaurant-bot/
│-- bot.py                # Main bot logic
│-- restaurant_data.json  # Menu / table data
│-- .gitignore            # Ignored files
│-- requirements.txt      # Dependencies
│-- README.md             # Project documentation
\\\

---

## 🛠️ Built with
- [Python](https://www.python.org/) 🐍  
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  

---

## 📌 Future improvements
- [ ] Store orders in a database  
- [ ] Admin dashboard for the restaurant  
- [ ] Online payment integration  

---

## 👨‍💻 Author
- **Sergiu Muntean** – [GitHub](https://github.com/munteanooo)

