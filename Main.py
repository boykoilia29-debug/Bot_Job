import telebot
from telebot import types
import openpyxl
from openpyxl import Workbook
import os
from datetime import datetime

# Конфигурация
TOKEN = '8712850028:AAFHOX1kcw_5vNYryKjp0KxR3G8YmhJigtg'  # Вставьте токен вашего бота
bot = telebot.TeleBot(TOKEN)

# Состояния пользователей
user_states = {}
user_data = {}

# Функция для инициализации Excel файла
def init_excel():
    if not os.path.exists('applications.xlsx'):
        wb = Workbook()
        ws = wb.active
        ws.title = "Заявки"
        headers = ['Дата', 'Username', 'Желаемая должность', 'Опыт работы', 'Статус']
        ws.append(headers)
        wb.save('applications.xlsx')

# Функция для сохранения данных в Excel
def save_to_excel(username, position, experience):
    wb = openpyxl.load_workbook('applications.xlsx')
    ws = wb.active
    
    # Ищем следующую свободную строку
    next_row = ws.max_row + 1
    
    # Записываем данные
    ws.cell(row=next_row, column=1, value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ws.cell(row=next_row, column=2, value=username)
    ws.cell(row=next_row, column=3, value=position)
    ws.cell(row=next_row, column=4, value=experience)
    ws.cell(row=next_row, column=5, value='Новая')
    
    wb.save('applications.xlsx')

# Приветственное сообщение со списком вакансий
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # ЗДЕСЬ НУЖНО ЗАПОЛНИТЬ СПИСОК ВАКАНСИЙ
    # Впишите актуальные вакансии между кавычками
    vacancies_list = """
    • Менеджер по продажам
    • Маркетолог
    • Разработчик Python
    • Дизайнер
    • Копирайтер
    """
    
    welcome_text = f"""
🎯 <b>Добро пожаловать в бот для приема заявок!</b>

📋 <b>Актуальные вакансии:</b>
{vacancies_list}

Для подачи заявки нажмите кнопку ниже 👇
    """
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📝 Подать заявку")
    markup.add(btn)
    
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=markup)

# Начало процесса подачи заявки
@bot.message_handler(func=lambda message: message.text == "📝 Подать заявку")
def start_application(message):
    user_id = message.chat.id
    user_states[user_id] = 'awaiting_username'
    
    bot.send_message(
        user_id, 
        "Шаг 1 из 3\n\n"
        "Пожалуйста, отправьте ваш Telegram username (например: @username):",
        reply_markup=types.ReplyKeyboardRemove()
    )

# Обработчик для получения username
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_username')
def get_username(message):
    user_id = message.chat.id
    username = message.text.strip()
    
    # Проверка формата username
    if not username.startswith('@'):
        username = '@' + username
    
    user_data[user_id] = {'username': username}
    user_states[user_id] = 'awaiting_position'
    
    bot.send_message(user_id, "Шаг 2 из 3\n\nКем вы хотите работать?")

# Обработчик для получения желаемой должности
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_position')
def get_position(message):
    user_id = message.chat.id
    position = message.text.strip()
    
    user_data[user_id]['position'] = position
    user_states[user_id] = 'awaiting_experience'
    
    bot.send_message(user_id, "Шаг 3 из 3\n\nЕсть ли у вас опыт работы? (Если да, напишите сколько)")

# Обработчик для получения опыта и сохранения заявки
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'awaiting_experience')
def get_experience(message):
    user_id = message.chat.id
    experience = message.text.strip()
    
    # Сохраняем данные
    user_data[user_id]['experience'] = experience
    
    # Сохраняем в Excel
    save_to_excel(
        user_data[user_id]['username'],
        user_data[user_id]['position'],
        experience
    )
    
    # Очищаем состояния
    del user_states[user_id]
    
    # Отправляем подтверждение
    bot.send_message(
        user_id,
        "✅ <b>Заявка успешно отправлена!</b>\n\n"
        "Мы рассмотрим вашу заявку и свяжемся с вами в ближайшее время.\n"
        "Спасибо за интерес к нашей компании!",
        parse_mode='HTML'
    )
    
    # Возвращаем главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📝 Подать заявку")
    markup.add(btn)
    bot.send_message(user_id, "Чтобы подать новую заявку, нажмите кнопку ниже:", reply_markup=markup)

# Обработчик команды для просмотра заявок (для администратора)
@bot.message_handler(commands=['chakApplication'])
def admin_panel(message):
    # Здесь можно добавить проверку на admin_id
    admin_id = 8347600681  # ЗАМЕНИТЕ НА ВАШ ID
    
    if message.chat.id == admin_id:
        wb = openpyxl.load_workbook('applications.xlsx')
        ws = wb.active
        
        if ws.max_row > 1:
            response = "📊 <b>Последние заявки:</b>\n\n"
            
            # Показываем последние 5 заявок
            start_row = max(2, ws.max_row - 4)
            for row in range(start_row, ws.max_row + 1):
                date = ws.cell(row=row, column=1).value
                username = ws.cell(row=row, column=2).value
                position = ws.cell(row=row, column=3).value
                experience = ws.cell(row=row, column=4).value
                
                response += f"📅 {date}\n"
                response += f"👤 {username}\n"
                response += f"💼 {position}\n"
                response += f"📝 Опыт: {experience}\n"
                response += "─" * 20 + "\n"
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Пока нет заявок")
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде")

# Инициализация Excel при запуске
init_excel()

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()