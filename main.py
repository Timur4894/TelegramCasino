import sqlite3
from telebot import types
import telebot
import random
import time
import requests

response = requests.get('https://api.telegram.org/bot<YOUR_TOKEN>/getMe', timeout=600)


# Создаем подключение к базе данных
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()

last_spin_time = {}


# Создаем таблицу, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        chat_id INTEGER,
        real_balance REAL,
        demo_balance REAL
    )
''')
conn.commit()

# Вставляем пользователя в базу данных
def insert_user(username, chat_id):
    cursor.execute('''
        INSERT INTO users (username, chat_id, real_balance, demo_balance)
        VALUES (?, ?, 0.0, 0.0)
    ''', (username, chat_id))
    conn.commit()

# Обновляем баланс пользователя
def update_balance(chat_id, real_balance=None, demo_balance=None):
    if real_balance is not None:
        cursor.execute('''
            UPDATE users
            SET real_balance = ?
            WHERE chat_id = ?
        ''', (real_balance, chat_id))
    if demo_balance is not None:
        cursor.execute('''
            UPDATE users
            SET demo_balance = ?
            WHERE chat_id = ?
        ''', (demo_balance, chat_id))
    conn.commit()

# Токен вашего бота
bot_token = '6589007050:AAG-cj1bTYlJ4cdgYu4Z8sa1uK2cjM3UWOY'
bot = telebot.TeleBot(bot_token)

# Проверка существования пользователя в базе данных
def user_exists(chat_id):
    cursor.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
    data = cursor.fetchone()
    return data is not None


def get_real_balance(chat_id):
    cursor.execute('SELECT real_balance FROM users WHERE chat_id = ?', (chat_id,))
    data = cursor.fetchone()
    return data[0] if data else 0


@bot.message_handler(commands=['start'])
def handle_start(message):
    if user_exists(message.chat.id):
        bot.reply_to(message, f'✅Вы уже зарегистрированы как {message.from_user.username}✅')
    else:
        insert_user(message.from_user.username, message.chat.id)
        bot.reply_to(message, '✅Привет! Ты зарегистрирован в нашей системе✅')

    real_balance = get_real_balance(message.chat.id)
    bot.send_message(message.chat.id, f'Ваш реальный баланс ⚜️{real_balance}⚜️', reply_markup=generate_markup())



@bot.message_handler(func=lambda message: message.text == 'Пополнить Баланс📲')
def handle_replenish_balance(message):
    markup = generate_payment_method_markup()
    bot.send_message(chat_id=message.chat.id, text="Выберете способ оплаты:", reply_markup=markup)



def generate_payment_method_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('💳Перевод на карту💳')
    button2 = types.KeyboardButton('📩Перевод на криптокошелек📩')
    button3 = types.KeyboardButton('📱Оплата через телеграм📱')
    button4 = types.KeyboardButton("Назад↩️")
    markup.add(button1, button2, button3, button4)
    return markup

@bot.message_handler(func=lambda message: message.text == '📩Перевод на криптокошелек📩')
def handle_crypto_payment(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        f'Минимальный ввод средств - 100 UAH💵\n'
        f'Для депозита криптовалюты LTC, отправьте средства на адрес: <code>ltc1q3894lgd3em7eyyaaanglkf3vk7haj3ne942m8m</code> 🚀\n'
        f'Для депозита криптовалюты SOL, отправьте средства на адрес: <code>F8zjvekk4AFghZrJqFNQ3gRYgikYBH6HHD7w8Qw4kB5x</code> 🌞\n'
        f'Для депозита криптовалюты MATIC, отправьте средства на адрес: <code>0x59fde972706997b8b4e1036411F150Fe70383550</code> 🚴‍♀️\n'
        f'После успешной отправки криптовалютных средств, пожалуйста, отправьте чек платежа вместе ID сюда -> <a href="https://t.me/casinosupportt">casinosupportt</a>\n'
        f'Ваш уникальный ID - {user_id} 🆔',
        parse_mode='HTML',
    )


@bot.message_handler(func=lambda message: message.text == '💳Перевод на карту💳')
def handle_card_payment(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        f'Минимальный ввод средств - 150 UAH💵\n'
        f'<code>5355 5722 5193 8757</code>\n'
        f'После успешной отправки денежных средств, пожалуйста, отправьте чек платежа вместе с вашим ID сюда -> <a href="https://t.me/casinosupportt">casinosupportt</a>\n'
        f'Ваш уникальный ID - {user_id} 🆔',
        parse_mode='HTML',
    )


@bot.message_handler(func=lambda message: message.text == '📱Оплата через телеграм📱')
def handle_tp_payment(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Данный тип оплаты временно не доступный')



@bot.message_handler(func=lambda message: message.text == 'Вывод Средств💸')
def handlein_replenish_balance(message):
    chat_id = message.chat.id
    real_balance = get_real_balance(chat_id)  # Получаем реальный баланс пользователя

    if real_balance >= 300:  # Проверяем, что баланс больше или равен 300 UAH
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button1 = types.KeyboardButton('💳На Карту💳')
        button2 = types.KeyboardButton('📩Вывод на криптокошелек📩')
        button3 = types.KeyboardButton('Назад↩️')
        markup.add(button1, button2, button3)

        bot.send_message(
            chat_id=chat_id,
            text="Выберете способ вывода💵:",
            reply_markup=markup
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text="‼️ Минимальная сумма вывода 300 UAH ‼️"
        )

# Обработчик кнопки "💳На Карту💳"
@bot.message_handler(func=lambda message: message.text == '💳На Карту💳')
def handle_card_withdrawal(message):
    chat_id = message.chat.id

    # Отправляем сообщение пользователю с инструкцией
    bot.send_message(
        chat_id=chat_id,
        text="Введите номер карты и суму вывода в формате:\n"
             "{Номер} / {Сума} \n"
             "Пример* 5355 5722 5193 8752 / 550UAH "
    )

    # Устанавливаем следующий шаг обработки ввода номера карты и имени
    bot.register_next_step_handler(message, process_card_withdrawal)



@bot.message_handler(func=lambda message: message.text == '📩Вывод на криптокошелек📩')
def handle_crypto_withdrawal(message):
    chat_id = message.chat.id

    # Отправляем сообщение пользователю с инструкцией
    bot.send_message(
        chat_id=chat_id,
        text="Введите адрес криптокошелька и суму вывода в формате:\n"
             "{Адрес} / {Сума} \n"
             "Пример* ltc1q3894lgd3em7eyyaaanglkf3vk7haj3ne942m8m / 350UAH "
    )

    # Устанавливаем следующий шаг обработки ввода номера карты и имени
    bot.register_next_step_handler(message, process_card_withdrawal)


# Обработка введенного номера карты и имени получателя
def process_card_withdrawal(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Проверяем, является ли текст сообщения командой "Назад↩️
    if message.text == 'Назад↩️':
        bot.send_message(
            chat_id=chat_id,
            text=f"Повторно нажмите 'Назад↩️'")
        return

    withdrawal_info = message.text.strip()

    # Отправляем уведомление администратору
    admin_notification = f"Пользователь с ником {message.from_user.username} и ID {user_id} отправил запрос на вывод  - {withdrawal_info}"
    bot.send_message(-4080329633, admin_notification)

    # Здесь вы можете добавить логику для обработки запроса вывода на карту
    # Например, обновление баланса пользователя, запись запроса в базу данных и т. д.

    # Отправляем подтверждение пользователю
    bot.send_message(
        chat_id=chat_id,
        text=f"Ваш запрос на вывод принят:\n{withdrawal_info}\n\n"
             "Запрос на вывод отправлен✅\n"
             " обработка займет ~20 минут⏱️. Если средства не поступили, пожалуйста, напишите в нашу техподдержку🧑‍💻-> <a href='https://t.me/casinosupportt'>casinosupportt</a>",parse_mode='HTML'
    )


#------------------------------------------------------------------------------------------------------------------------------------------------------------------#




#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#Логика игры "🥝", "🍇", "🌶", "🍅", "🍓", "🥕"   🧛🏻🧝🏻‍♀️🧟🧙🏻🧚🏻‍♀️🧞🥷🏻
user_game = {}

user_bets = {}
fruits_and_veggies = ["🥝", "🍇", "🌶", "🍅", "🍓", "🥕"]


@bot.message_handler(func=lambda message: message.text == 'Начать Играть🎰')
def handle_start_playing(message):
    markup = generate_play_mode_markup()
    bot.send_message(chat_id=message.chat.id, text="Выберите режим игры:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🪙Играть с демонстрационным счетом🪙')
def handle_demo_play(message):
    markup = generate_demo_game_markup()
    bot.send_message(chat_id=message.chat.id, text="‼️Выберите игру‼️", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Назад↩️')
def handle_go_back(message):
    bot.send_message(chat_id=message.chat.id, text="📍Возвращаемся обратно📍", reply_markup=generate_markup())

@bot.message_handler(func=lambda message: message.text == '⚜️Играть На реальный баланс⚜️')
def handle_real_play(message):
    real_balance = get_real_balance(message.chat.id)
    if real_balance == 0:
        bot.send_message(chat_id=message.chat.id, text="‼️Ваш баланс равен 0, для игры на реальный баланс вы должны пополнить баланс‼️")
    else:
        bot.send_message(chat_id=message.chat.id, text="‼️Выберите игру‼️", reply_markup=generate_game_markup())

@bot.message_handler(func=lambda message: message.text == 'Слоты🎰')
def handle_slots(message):
    user_game[message.chat.id] = 'slots'
    bot.send_message(chat_id=message.chat.id, text="💰Введите размер ставки в чат: (3 - 50 UAH)💰", reply_markup=generate_back_markup())


@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_bet_size(message):
    bet_size = int(message.text)
    user_id = message.chat.id
    real_balance = get_real_balance(user_id)

    if user_game.get(message.chat.id) == 'slots' and 3 <= bet_size <= 50:
        user_bets[message.chat.id] = bet_size
        # Отправка картинки с текстом
        with open('aaa.jpg', 'rb') as photo:
            bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f"Вы продолжили со ставкой 💰{bet_size}💰\n"
                                                                         f"🎰 Правила Слотов: Выигрыш при 3, 4, 5 или 6 одинаковых символах в ряд или 3 символа наискосок. Удачи на барабанах! 💰",
                           reply_markup=generate_slot_markup())

    elif user_game.get(user_id) == 'baccarat' and 3 <= bet_size <= 25:

        if bet_size > real_balance:
            bot.send_message(user_id, "❌Ваша ставка превышает ваш баланс, пожалуйста, понизьте ее.❌")

            return

        user_bets[user_id] = bet_size
        with open('bacara.jpg', 'rb') as photo:
            bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f"Вы продолжили со ставкой 💰{bet_size}💰\n"
                                      f"🃏 Правила Баккара: Выбери цвет - синий или красный (45% шанс), или серый (10% шанс). Выплаты За синий и красный - x2, за серый - x10. Удачи!",
                             reply_markup=generate_baccarat_markup())

@bot.message_handler(func=lambda message: message.text == 'Spin📍')
def handle_spin(message):
    bet_size = user_bets.get(message.chat.id, 0)
    real_balance = get_real_balance(message.chat.id)



    if real_balance == 0:
        bot.send_message(chat_id=message.chat.id, text="❌Ваш баланс равен 0, для игры на реальный баланс вы должны пополнить баланс❌")
        bot.send_message(chat_id=message.chat.id, text="Выберите действие:", reply_markup=generate_markup())
        return

    if bet_size > real_balance:
        bot.send_message(chat_id=message.chat.id, text="❌Ваша ставка превышает ваш баланс, пожалуйста понизьте ее❌")
        handle_slots(message)
        return

    new_balance = real_balance - bet_size
    update_balance(message.chat.id, real_balance=new_balance)
    # bot.send_message(message.chat.id, f'Ваш актуальный реальный баланс ⚜️{new_balance}⚜️')

    spin_result = generate_spin()
    bot.send_message(chat_id=message.chat.id, text=spin_result)  # всегда отправляйте результат спина

    total_winning_amount = 0

    for line in spin_result.split("\n"):
        if has_six_consecutive(line):
            total_winning_amount += bet_size * 5
        elif has_five_consecutive(line):
            total_winning_amount += bet_size * 4
        elif has_four_consecutive(line):
            total_winning_amount += bet_size * 3
        elif has_three_consecutive(line):
            total_winning_amount += bet_size * 2

    # Добавляем проверку на диагональные комбинации для 3 символов
    spin_matrix = [list(line) for line in spin_result.split("\n")]
    if has_diagonal_consecutive(spin_matrix):
        total_winning_amount += bet_size * 2

    if total_winning_amount:
        new_balance += total_winning_amount
        update_balance(message.chat.id, real_balance=new_balance)
        bot.send_message(chat_id=message.chat.id, text=f"💎Вы выиграли {total_winning_amount}💎\n"
                                                       f"Баланс ⚜️{new_balance}⚜️ UAH")
    else:
        new_balance += total_winning_amount
        update_balance(message.chat.id, real_balance=new_balance)
        bot.send_message(chat_id=message.chat.id, text=f"❌Вы проиграли❌\n"
                                                       f"Баланс ⚜️{new_balance}⚜️ UAH")


def has_three_consecutive(line):
    for i in range(0, len(line) - 2):
        if line[i] == line[i+1] == line[i+2]:
            return True
    return False

def has_four_consecutive(line):
    for i in range(0, len(line) - 3):
        if line[i] == line[i+1] == line[i+2] == line[i+3]:
            return True
    return False

def has_five_consecutive(line):
    for i in range(0, len(line) - 4):
        if line[i] == line[i+1] == line[i+2] == line[i+3] == line[i+4]:
            return True
    return False

def has_six_consecutive(line):
    for i in range(0, len(line) - 5):
        if line[i] == line[i+1] == line[i+2] == line[i+3] == line[i+4] == line[i+5]:
            return True
    return False




@bot.message_handler(func=lambda message: message.text == 'Изменить ставку⚙️')
def handle_change_bet(message):
    bot.send_message(chat_id=message.chat.id, text="💰Введите размер ставки в чат: (3 - 50 UAH)💰")



def generate_spin():
    line1 = "➖➡️" + ''.join(random.choices(fruits_and_veggies, k=6)) + "⬅️➖"
    line2 = "➖➡️" + ''.join(random.choices(fruits_and_veggies, k=6)) + "⬅️➖"
    line3 = "➖➡️" + ''.join(random.choices(fruits_and_veggies, k=6)) + "⬅️➖"
    return line1 + "\n" + line2 + "\n" + line3


def consecutive_symbols(line):
    max_count = 0
    current_count = 1

    for i in range(1, len(line)):
        if line[i] == line[i - 1]:
            current_count += 1
        else:
            if current_count > max_count:
                max_count = current_count
            current_count = 1

    if current_count > max_count:
        max_count = current_count

    return max_count


def has_diagonal_consecutive(matrix):
    """Проверяет наличие трех одинаковых символов по диагонали."""
    for i in range(len(matrix) - 2):
        for j in range(len(matrix[i]) - 2):
            if matrix[i][j] == matrix[i+1][j+1] == matrix[i+2][j+2]:
                return True
            if matrix[i][j+2] == matrix[i+1][j+1] == matrix[i+2][j]:
                return True
    return False

@bot.message_handler(func=lambda message: message.text == 'Демо Слоты🎰')
def handle_demo_slots(message):
    markup = generate_demo_slots_markup()
    bot.send_message(chat_id=message.chat.id, text="Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📍Spin')
def handle_spin_demo(message):
    bet_size = user_bets.get(message.chat.id, 0)
    spin_result = generate_spin()

    bot.send_message(chat_id=message.chat.id, text=spin_result)  # всегда отправляйте результат спина

    total_win_multiplier = 0
    spin_matrix = [list(line) for line in spin_result.split("\n")]

    for line in spin_result.split("\n"):
        if has_six_consecutive(line):
            total_win_multiplier += 5
        elif has_five_consecutive(line):
            total_win_multiplier += 4
        elif has_four_consecutive(line):
            total_win_multiplier += 3
        elif has_three_consecutive(line):
            total_win_multiplier += 2

    # Добавляем проверку на диагональные комбинации для 3 символов
    if has_diagonal_consecutive(spin_matrix):
        total_win_multiplier += 2

    if total_win_multiplier:
        bot.send_message(chat_id=message.chat.id, text=f"Вы выиграли бы x{total_win_multiplier}🪙 от ставки")


@bot.message_handler(func=lambda message: message.text == 'Бакара🎲')
def handle_baccarat(message):
    user_game[message.chat.id] = 'baccarat'
    real_balance = get_real_balance(message.chat.id)
    if real_balance == 0:
        bot.send_message(message.chat.id, "❌Ваш баланс равен 0, для игры на реальный баланс вы должны пополнить баланс❌")
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=generate_markup())
    else:
        bot.send_message(message.chat.id, "💰Введите размер ставки в чат: (3 - 25 UAH)💰")




def generate_baccarat_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начать Играть в Бакару🎰")
    item2 = types.KeyboardButton("Изменить ставку⚙️")
    item3 = types.KeyboardButton("Назад↩️")

    markup.row(item1)
    markup.row(item2, item3)
    return markup  # Важно добавить эту строку для возврата разметки

@bot.message_handler(func=lambda message: message.text == 'Начать Играть в Бакару🎰')
def handle_start_baccarat_game(message):
    markup = generate_baccarat_color_markup()
    bot.send_message(message.chat.id, "🎲Выберете цвет на который будете ставить🎲", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['🟦', '🟥', '⬜️'])
def handle_baccarat_color_choice(message):
    color_choice = message.text
    user_id = message.chat.id
    real_balance = get_real_balance(user_id)

    if real_balance == 0:
        bot.send_message(user_id, "❌Ваш баланс равен 0, для игры на реальный баланс вы должны пополнить баланс❌")
        bot.send_message(user_id, "Выберите действие:", reply_markup=generate_markup())
        return

    if color_choice == '🟦' or color_choice == '🟥':
        win_chance = 45
    elif color_choice == '⬜️':
        win_chance = 3
        payout_multiplier = 10  # set the multiplier to 10 for the gray color
    else:
        win_chance = 0

    if random.randint(1, 100) <= win_chance:
        # Пользователь выиграл, увеличиваем баланс в
        bet_size = user_bets.get(user_id, 0)
        if color_choice == '⬜️':
            new_balance = real_balance + (bet_size * payout_multiplier)
        else:
            new_balance = real_balance + (bet_size * 2)
        update_balance(user_id, real_balance=new_balance)
        bot.send_message(user_id, "💎Победа! Ваш баланс увеличен💎")
    else:
        # Пользователь проиграл, уменьшаем баланс на размер ставки
        bet_size = user_bets.get(user_id, 0)
        new_balance = real_balance - bet_size
        update_balance(user_id, real_balance=new_balance)
        bot.send_message(user_id, "🛑Проигрыш. Ваш баланс уменьшен🛑")

    # Отправляем сообщение о текущем балансе
    bot.send_message(user_id, f'Ваш текущий реальный баланс ⚜️{new_balance}⚜️')


@bot.message_handler(func=lambda message: message.text == 'Демо Бакара🎲')
def handle_demo_baccarat(message):
    rules_text = "Демо Бакара - это игра, в которой вы можете попробовать свою удачу без риска потери реальных денег.🎲\n\n" \
                 "Удачи в игре!🍀"

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton("Начать Демо Игру")
    item2 = types.KeyboardButton("Назад↩️")
    markup.row(item1, item2)

    bot.send_message(chat_id=message.chat.id, text=rules_text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Начать Демо Игру')
def handle_start_demo_baccarat_game(message):
    markup = generate_demo_baccarat_color_markup()
    bot.send_message(message.chat.id, "🎲Выберете цвет на который будете ставить🎲", reply_markup=markup)

def generate_demo_baccarat_color_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    colors = ['🟦 demo', '🟥 demo', '⬜️ demo']
    markup.add(*[types.KeyboardButton(color) for color in colors])
    markup.add(types.KeyboardButton('Назад↩️'))
    return markup





@bot.message_handler(func=lambda message: message.text in ['🟦 demo', '🟥 demo', '⬜️ demo'])
def handle_demo_baccarat_color_choice(message):
    color_choice = message.text
    user_id = message.chat.id

    if color_choice == '🟦 demo' or color_choice == '🟥 demo':
        win_chance = 50  # Шанс победы для синего и красного цветов 35%
    elif color_choice == '⬜️ demo':
        win_chance = 7  # Шанс победы для серого цвета 3%
        payout_multiplier = 10
    else:
        win_chance = 0

    if random.randint(1, 100) <= win_chance:
        # Пользователь выиграл
        if color_choice == '⬜️ demo':
            bot.send_message(user_id, f"💎Победа💎 \nВыигрыш составил бы: x{payout_multiplier} от ставки")
        else:
            bot.send_message(user_id, "💎Победа💎 \nВыигрыш составил бы: x2 от ставки")

    else:
        # Пользователь проиграл
        bot.send_message(user_id, "🛑Проигрыш🛑")

    # Добавьте здесь обновление баланса, если это необходимо




def generate_baccarat_color_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    blue_button = types.KeyboardButton("🟦")
    red_button = types.KeyboardButton("🟥")
    gray_button = types.KeyboardButton("⬜️")
    back_button = types.KeyboardButton("Назад↩️")

    markup.add(blue_button, red_button, gray_button)
    markup.add(back_button)

    return markup

def generate_demo_slots_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('📍Spin')
    button2 = types.KeyboardButton('Назад↩️')
    markup.add(button1, button2)
    return markup


def generate_back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('Назад↩️')
    markup.add(button)
    return markup

def generate_play_mode_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('⚜️Играть На реальный баланс⚜️')
    button2 = types.KeyboardButton('🪙Играть с демонстрационным счетом🪙')
    button3 = types.KeyboardButton('Назад↩️')
    markup.add(button1, button2, button3)

    return markup

def generate_demo_game_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('Демо Бакара🎲')
    button2 = types.KeyboardButton('Демо Слоты🎰')
    button3 = types.KeyboardButton('Назад↩️')
    markup.add(button1, button2, button3)

    return markup

def generate_slot_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('Spin📍')
    button2 = types.KeyboardButton('Изменить ставку⚙️')
    button3 = types.KeyboardButton('Назад↩️')
    markup.add(button1, button2, button3)
    return markup



def generate_game_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('Бакара🎲')
    button2 = types.KeyboardButton('Слоты🎰')
    button3 = types.KeyboardButton('Назад↩️')
    markup.add(button1, button2, button3)
    return markup
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#Вывод бабок



@bot.message_handler(func=lambda message: message.text == 'Узнать реальный Баланс⚜️')
def know_balance(message):
    user_id = message.chat.id
    real_balance = get_real_balance(user_id)
    bot.send_message(chat_id=message.chat.id, text=f"Ваш реальный баланс ⚜️{real_balance}⚜️")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------#


def generate_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton('Пополнить Баланс📲')
    button2 = types.KeyboardButton('Начать Играть🎰')
    button3 = types.KeyboardButton('Вывод Средств💸')
    button4 = types.KeyboardButton('Узнать реальный Баланс⚜️')
    markup.add(button1, button2, button3,button4)
    return markup



# Запуск бота
bot.polling()

