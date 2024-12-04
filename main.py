#импорт библиотек // Import libraries
import requests
import json
import os
import datetime
import asyncio
import logging
import sys
import sqlite3
import create_db
import resource.general
from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    CallbackQuery
)
from dotenv import load_dotenv



#Получение токена с .env файла // Getting token from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")
router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class Form(StatesGroup):
  match_id = State()
  account_id = State()

#Загрузка файлов с дополнительной информацией // Download files with additional information
with open('resource\\dota2\\heroes.json', 'r') as heroes_json:
    heroes = json.load(heroes_json)

with open('resource\\general\\countries.json', 'r') as countries_json:
    country = json.load(countries_json)

with open('resource\\dota2\\dota2_ranks.json', 'r') as dota2_ranks_json:
    rank = json.load(dota2_ranks_json)

with open('resource\\general\\tournaments.json', 'r') as tournaments_json:
    tournaments = json.load(tournaments_json)

with open('resource\\general\\information.json', 'r') as information_json:
    info = json.load(information_json)




#Обработка команды /start // Processing /start command
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    
    await message.answer("""🇺🇸English
Hello, OpenTrackerBot is a bot created for conveniently tracking matches in Dota, as well as viewing statistics of other players.
Let's set up the bot!
\n
🇷🇺Russian
Привет, OpenTrackerBot - бот, созданный для удобного отслеживания матчей в доте, а так же просмотр статистики других игроков.
Давайте настроим бота!""",
parse_mode='HTML', disable_web_page_preview=True)


#Обработка команды /help // Processing /help command
@router.message(Command('help'))
async def command_help_handler(message: Message) -> None:
  await message.answer('''/findmatch - Узнать информацию о матче по его ID
/findplayer - Информация о игроке по его ID
''')


@router.message(Command('info'))
async def command_info(message: Message) -> None:
    await message.answer(f'Version: {info['info']['version']}')


#Обработка команды /findmatch // Processing /findmatch command
@router.message(Command('findmatch'))
async def command_findmatch_handler(message, state: FSMContext):
  await state.set_state(Form.match_id)
  await message.answer("Введите ID матча")

@router.message(Form.match_id)
async def get_match_data(message, state: FSMContext):
  await state.update_data(match_id=message.text)
  try:
    resp = requests.get(f'https://api.opendota.com/api/matches/{message.text}') # Отправка запроса на сервер opendota.com // Sending a request to the opendota.com server
    response = resp.json() # Получение ответа в виде json-файла // Collecting info in json-file format

    with open(f'{message.text}.json', 'w') as outfile:
      json.dump(response, outfile) #Сохранение полученного json-файла // Saving received json-file

    with open(f'{message.text}.json', 'r') as outfile:
      result = json.load(outfile) #Чтение полученного json-файла // Reading received json-file

    #Обработка и сохранение результатов матча в переменные // Processing and saving match results into variables
    data_win = result["radiant_win"]
    data_duration = str(datetime.timedelta(seconds=result["duration"]))
    data_radiant_score = result["radiant_score"]
    data_dire_score = result["dire_score"]
    #Создание пустых списков для сохранения информации о игроках // Creating empty lists to save player information
    data_players_radiant = []
    data_players_dire = []


    #Обработка информации о игроках, сохранение в списки в виде словарей // Processing information about players, saving to lists in the form of dictionaries
    for elem_result in result["players"]:
      if elem_result.get("team_number") == 0: #Если игрок находится на стороне сил света // If the player is on the radiant side
        players_info = dict()
        for elem_heroes in heroes["heroes"]:
          if str(elem_result.get("hero_id")) == elem_heroes["hero_id"]:
            players_info['hero'] = elem_heroes.get("hero_name")
          else:
            pass
        players_info['kills'] = elem_result.get("kills")
        players_info['deaths'] = elem_result.get("deaths")
        players_info['assists'] = elem_result.get("assists")
        data_players_radiant.append(players_info)
      elif elem_result.get("team_number") == 1: #Если игрок находится на стороне сил тьмы // If the player is on the dire side
        players_info = dict()
        for elem_heroes in heroes["heroes"]:
          if str(elem_result.get("hero_id")) == elem_heroes["hero_id"]:
            players_info['hero'] = elem_heroes.get("hero_name")
          else:
            pass
        players_info['kills'] = elem_result.get("kills")
        players_info['deaths'] = elem_result.get("deaths")
        players_info['assists'] = elem_result.get("assists")
        data_players_dire.append(players_info)
      else:
        pass

    

    #Отправка ботом сообщения с информацией о матче // Bot sending a message with information about a match
    if data_win: #Победа сил света // Radiant match-win 
      await message.answer(f'''🏆Силы света [{data_radiant_score}:{data_dire_score}] Силы тьмы 
Длительность: {data_duration}\n
🏆Силы света:\n
{data_players_radiant[0].get('hero')} - [{data_players_radiant[0].get('kills')}/{data_players_radiant[0].get('deaths')}/{data_players_radiant[0].get('assists')}]
{data_players_radiant[1].get('hero')} - [{data_players_radiant[1].get('kills')}/{data_players_radiant[1].get('deaths')}/{data_players_radiant[1].get('assists')}]
{data_players_radiant[2].get('hero')} - [{data_players_radiant[2].get('kills')}/{data_players_radiant[2].get('deaths')}/{data_players_radiant[2].get('assists')}]
{data_players_radiant[3].get('hero')} - [{data_players_radiant[3].get('kills')}/{data_players_radiant[3].get('deaths')}/{data_players_radiant[3].get('assists')}]
{data_players_radiant[4].get('hero')} - [{data_players_radiant[4].get('kills')}/{data_players_radiant[4].get('deaths')}/{data_players_radiant[4].get('assists')}]

Силы тьмы:\n
{data_players_dire[0].get('hero')} - [{data_players_dire[0].get('kills')}/{data_players_dire[0].get('deaths')}/{data_players_dire[0].get('assists')}]
{data_players_dire[1].get('hero')} - [{data_players_dire[1].get('kills')}/{data_players_dire[1].get('deaths')}/{data_players_dire[1].get('assists')}]
{data_players_dire[2].get('hero')} - [{data_players_dire[2].get('kills')}/{data_players_dire[2].get('deaths')}/{data_players_dire[2].get('assists')}]
{data_players_dire[3].get('hero')} - [{data_players_dire[3].get('kills')}/{data_players_dire[3].get('deaths')}/{data_players_dire[3].get('assists')}]
{data_players_dire[4].get('hero')} - [{data_players_dire[4].get('kills')}/{data_players_dire[4].get('deaths')}/{data_players_dire[4].get('assists')}]
''')
      
    else: ##Победа сил тьмы // Dire match-win 
      await message.answer(f'''Силы света [{data_radiant_score}:{data_dire_score}] Силы тьмы🏆
Длительность: {data_duration}
Силы света:\n
{data_players_radiant[0].get('hero')} - [{data_players_radiant[0].get('kills')}/{data_players_radiant[0].get('deaths')}/{data_players_radiant[0].get('assists')}]
{data_players_radiant[1].get('hero')} - [{data_players_radiant[1].get('kills')}/{data_players_radiant[1].get('deaths')}/{data_players_radiant[1].get('assists')}]
{data_players_radiant[2].get('hero')} - [{data_players_radiant[2].get('kills')}/{data_players_radiant[2].get('deaths')}/{data_players_radiant[2].get('assists')}]
{data_players_radiant[3].get('hero')} - [{data_players_radiant[3].get('kills')}/{data_players_radiant[3].get('deaths')}/{data_players_radiant[3].get('assists')}]
{data_players_radiant[4].get('hero')} - [{data_players_radiant[4].get('kills')}/{data_players_radiant[4].get('deaths')}/{data_players_radiant[4].get('assists')}]\n
🏆Силы тьмы:\n
{data_players_dire[0].get('hero')} - [{data_players_dire[0].get('kills')}/{data_players_dire[0].get('deaths')}/{data_players_dire[0].get('assists')}]
{data_players_dire[1].get('hero')} - [{data_players_dire[1].get('kills')}/{data_players_dire[1].get('deaths')}/{data_players_dire[1].get('assists')}]
{data_players_dire[2].get('hero')} - [{data_players_dire[2].get('kills')}/{data_players_dire[2].get('deaths')}/{data_players_dire[2].get('assists')}]
{data_players_dire[3].get('hero')} - [{data_players_dire[3].get('kills')}/{data_players_dire[3].get('deaths')}/{data_players_dire[3].get('assists')}]
{data_players_dire[4].get('hero')} - [{data_players_dire[4].get('kills')}/{data_players_dire[4].get('deaths')}/{data_players_dire[4].get('assists')}]
''')
      
    os.remove(f'{message.text}.json') #Удаление ранее полученного json-файла // Deleting a previously received json file

  except:
    pass


#Обработка команд /findplayer и /findaccount // Handling the /findplayer and /findaccount commands
@router.message(Command('findplayer'))
async def command_findplayer_handler(message, state: FSMContext):
  await state.set_state(Form.account_id)
  await message.answer('Введите ID игрока')

@router.message(Form.account_id)
async def get_account_data(message, state: FSMContext):
  await state.update_data(account_id=message.text)
  try:
    resp = requests.get(f'https://api.opendota.com/api/players/{message.text}') #Отправка запроса на opendota.com API // Sending a request to the opendota.com API
    response = resp.json()

    with open(f'{message.text}.json', 'w') as outfile:
      json.dump(response, outfile) #Сохранение полученного json-файла // Saving received json-file

    with open(f'{message.text}.json', 'r') as outfile:
      result = json.load(outfile) #Чтение полученного json-файла // Reading received json-file

    
    #Обработка и сохранение информации о игроке в переменные // Processing and storing information about the player into variables
    data_account_id = result['profile']['account_id']
    data_steamid = result['profile']['steamid']
    data_personaname = result['profile']['personaname']
    data_avatarfull = result['profile']['avatarfull']
    #Присваеваем значение None, т.к заполнять будем далее // We assign the value None, because we will fill it in later
    data_country = None
    data_country_emoji = None
    data_player_rank = None


    for elem in country["countries"]: #Считываем элементы в с json файла "countries" // Reading elements from the json file "countries"
      if result["profile"]["loccountrycode"] == elem["country_iso_alpha2"]: #Сравниваем код страны, полученный запросом на API с нашим списком // Compare the country code received by the API request with our list
        data_country = elem.get("country") #Если код страны совпадает, то назначиваем название страны в переменную // If the country code matches, then assign the country name to the variable
      else:
        pass
  
    for elem in rank["ranks"]: #Делаем то же самое, но теперь для получения ранга // We do the same thing, but now to gain rank
      if str(result["rank_tier"]) == elem["rank_id"]:
        data_player_rank = elem.get("rank_name")
      else:
        pass


    #Бот отправляет сообщение с результатом // The bot sends a message with the result
    if data_country == None: #Если страна в стиме отсутствует, то не добавляем её в ответ // If the country is not on Steam, then we do not add it to the answer.
      await message.answer_photo(data_avatarfull, caption=f'''ID аккаунта: {data_account_id}\nSteam ID: {data_steamid}\nНикнейм: {data_personaname}
Ранг: {data_player_rank}''')
    else:
      await message.answer_photo(data_avatarfull, caption=f'''ID аккаунта: {data_account_id}\nSteam ID: {data_steamid}\nНикнейм: {data_personaname}
Страна: {data_country}
Ранг: {data_player_rank}''')



    os.remove(f'{message.text}.json') #Удаление ранее полученного json-файла // Deleting a previously received json file

  except:
    pass

@router.message(Command('profile'))
async def command_profile(message):
    user_profile = {}
    connection = sqlite3.connect('main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM users')
    users_info = cursor.fetchall()

    connection.commit()
    connection.close()

    for user in users_info:
        user_profile['id'] = user[0]
        user_profile['predictions_count'] = user[2]
        user_profile['predictions_correct'] = user[3]
        user_profile['predictions_incorrect'] = user[4]
        if user[2] != 0 and user[3] != 0:
            user_profile['predictions_winrate'] =  round(user[3]/user[2]*100, 2)
        else:
            user_profile['predictions_winrate'] = 0
        user_profile['predictions_score'] = user[5]


    await message.answer(f"Информация об аккаунте:\nOpenTracker ID: {user_profile['id']}\nПоставлено прогнозов: {user_profile['predictions_count']}\nВерные прогнозы: {user_profile['predictions_correct']}\nНеверные прогнозы: {user_profile['predictions_incorrect']}\nПроцент угаданных прогнозов: {user_profile['predictions_winrate']}%\nOpenTracker Score: {user_profile['predictions_score']}")


@router.message(Command('cpredict'))
async def tournament_list(message):
    kb = []

    connection = sqlite3.connect('main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM tournaments')
    tournament_info = cursor.fetchall()

    connection.commit()
    connection.close()

    for tournament in tournament_info:
        if tournament[2] == "Live" or tournament[2] == "Upcoming":
            kb.append([InlineKeyboardButton(text=f"{tournament[1]}", callback_data=f"trn.predict_{tournament[1].replace(' ', '_')}")])
        else:
            pass
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    if kb != []:
        await message.answer("Список турниров, на которые можно поставить прогнозы:", reply_markup=keyboard)
    else:
        await message.answer("Нет доступных турниров")


@router.message(Command('closematch'))
async def tournament_list(message):
    if str(message.from_user.id) in os.getenv('ADMINS'):
        kb = []

        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM tournaments')
        tournament_info = cursor.fetchall()

        connection.commit()
        connection.close()

        for tournament in tournament_info:
            if tournament[2] == "Live" or tournament[2] == "Upcoming":
                kb.append([InlineKeyboardButton(text=f"{tournament[1]}", callback_data=f"trn.close_{tournament[1].replace(' ', '_')}")])
            else:
                pass
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        if kb != []:
            await message.answer("Список турниров, матчи которых можно закрыть:", reply_markup=keyboard)
        else:
            await message.answer("Нет доступных турниров")
    else:
       pass


@router.message(Command('closepredicts'))
async def tournament_list(message):
    if str(message.from_user.id) in os.getenv('ADMINS'):
        kb = []

        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM tournaments')
        tournament_info = cursor.fetchall()

        connection.commit()
        connection.close()

        for tournament in tournament_info:
            if tournament[2] == "Live" or tournament[2] == "Upcoming":
                kb.append([InlineKeyboardButton(text=f"{tournament[1]}", callback_data=f"trn.pred.close_{tournament[1].replace(' ', '_')}")])
            else:
                pass
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        if kb != []:
            await message.answer("Список турниров, прогнозы на матчи которых можно закрыть:", reply_markup=keyboard)
        else:
            await message.answer("Нет доступных турниров")
    else:
       pass


@router.callback_query()
async def matches_list(callback: CallbackQuery):
    kb = []
    match_info = {}

    connection = sqlite3.connect('main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM tournaments')
    tournament_info = cursor.fetchall()
    cursor.execute('SELECT * FROM matches')
    matches_info = cursor.fetchall()
    cursor.execute('SELECT * FROM predicts')
    predicts_info = cursor.fetchall()
    cursor.execute('SELECT * FROM users')
    users_info = cursor.fetchall()

    connection.commit()
    connection.close()


    if callback.data.startswith('trn.predict'):
        for matches in matches_info:
            if callback.data.replace('_', ' ') == f'trn.predict_{matches[1]}'.replace('_', ' '):
                if matches[6] == "Upcoming":
                    if (callback.from_user.id, matches[0], 0) in predicts_info or (callback.from_user.id, matches[0], 1) in predicts_info:
                        pass
                    else:
                        kb.append([InlineKeyboardButton(text=f"{matches[2]}"+ " - "+f"{matches[3]}", callback_data=f"match.predict_{matches[0]}")])
                else:
                    pass
            else:
                pass
        else:
            pass

        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        if kb != []:
            await callback.message.edit_text('Хорошо, сейчас доступны следующие матчи для прогнозов:', reply_markup=keyboard)
        else:
            await callback.message.edit_text('Нет доступных матчей')


    elif callback.data.startswith('match.predict'):
        for matches in matches_info:
            if callback.data == f"match.predict_{matches[0]}":
                kb.append([InlineKeyboardButton(text=f"{matches[2]}", callback_data=f"pred_{matches[0]}_a")])
                kb.append([InlineKeyboardButton(text=f"{matches[3]}", callback_data=f"pred_{matches[0]}_b")])
                match_info['tournament_name'] = matches[1]
                match_info['team_a'] = matches[2]
                match_info['team_b'] = matches[3]
                match_info['time'] = matches[4]
                match_info['type'] = matches[5]
                    
            else:
                pass
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await callback.message.edit_text(f'Информация о матче:\nТурнир: {match_info['tournament_name']}\n{match_info['team_a']} - {match_info['team_b']}\nВремя проведения: {match_info['time']}\nТип матча: {match_info['type']}',
                                         reply_markup=keyboard)


    elif callback.data.startswith('pred'):
        for matches in matches_info:
            if callback.data == f"pred_{matches[0]}_a":
                kb.append([InlineKeyboardButton(text="Подтвердить", callback_data=f"cpred_{matches[0]}_a_yes")])
                kb.append([InlineKeyboardButton(text="Отменить", callback_data=f"cpred_{matches[0]}_a_no")])
                match_info['tournament_name'] = matches[1]
                match_info['team_a'] = matches[2]
                match_info['team_b'] = matches[3]
                match_info['time'] = matches[4]
                match_info['type'] = matches[5]
                keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
                await callback.message.edit_text(f'Вы уверены, что хотите сделать прогноз на победу команды {match_info['team_a']}?\nЭто действие будет невозможно отменить',
                                                     reply_markup=keyboard)
            elif callback.data == f"pred_{matches[0]}_b":
                kb.append([InlineKeyboardButton(text="Подтвердить", callback_data=f"cpred_{matches[0]}_b_yes")])
                kb.append([InlineKeyboardButton(text="Отменить", callback_data=f"cpred_{matches[0]}_b_no")])
                match_info['tournament_name'] = matches[1]
                match_info['team_a'] = matches[2]
                match_info['team_b'] = matches[3]
                match_info['time'] = matches[4]
                match_info['type'] = matches[5]
                keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
                await callback.message.edit_text(f'Вы уверены, что хотите сделать прогноз на победу команды {match_info['team_b']}?\nЭто действие будет невозможно отменить',
                                                 reply_markup=keyboard)
            else:
                pass
            
                    
    elif callback.data.startswith('cpred'):
        for matches in matches_info:
            if callback.data == f"cpred_{matches[0]}_a_yes":
                match_info['tournament_name'] = matches[1]
                match_info['team_a'] = 0
                match_info['match_id'] = matches[0]

                connection = sqlite3.connect('main.db')
                cursor = connection.cursor()

                cursor.execute('INSERT INTO predicts (tid, match_id, predict) VALUES (?, ?, ?)', (callback.from_user.id, match_info['match_id'], match_info['team_a']))
                cursor.execute('UPDATE users SET predictions_count = predictions_count + ? WHERE tid == ?', (1, callback.from_user.id))
                
                connection.commit()
                connection.close()

                await callback.answer('Прогноз успешно записан!')
                await callback.message.delete()

            elif callback.data == f"cpred_{matches[0]}_b_yes":
                match_info['tournament_name'] = matches[1]
                match_info['team_b'] = 1
                match_info['match_id'] = matches[0]

                connection = sqlite3.connect('main.db')
                cursor = connection.cursor()

                cursor.execute('INSERT INTO predicts (tid, match_id, predict) VALUES (?, ?, ?)', (callback.from_user.id, match_info['match_id'], match_info['team_b']))
                cursor.execute('UPDATE users SET predictions_count = predictions_count + ? WHERE tid == ?', (1, callback.from_user.id))

                connection.commit()
                connection.close()

                await callback.answer('Прогноз успешно записан!')
                await callback.message.delete()

            elif callback.data == f"cpred_{matches[0]}_a_no":
                await callback.answer('Действие отменено.')
                await callback.message.delete()

            elif callback.data == f"cpred_{matches[0]}_b_no":
                await callback.answer('Действие отменено.')
                await callback.message.delete()


    elif callback.data.startswith('trn.close'):
        for matches in matches_info:
            if callback.data.replace('_', ' ') == f'trn.close_{matches[1]}'.replace('_', ' '):
                if matches[6] == "Upcoming" or matches[6] == "Live":
                    kb.append([InlineKeyboardButton(text=f"{matches[2]}"+ " - "+f"{matches[3]}", callback_data=f"match.close_{matches[0]}")])
                else:
                    pass
            else:
                pass
        else:
            pass

        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        if kb != []:
            await callback.message.edit_text('Доступные для закрытия матчи:', reply_markup=keyboard)
        else:
            await callback.message.edit_text('Нет доступных матчей для закрытия')


    elif callback.data.startswith('match.close'):
        for matches in matches_info:
            if callback.data == f"match.close_{matches[0]}":
                kb.append([InlineKeyboardButton(text=f"{matches[2]}", callback_data=f"match.win_{matches[0]}_a")])
                kb.append([InlineKeyboardButton(text=f"{matches[3]}", callback_data=f"match.win_{matches[0]}_b")])
                match_info['tournament_name'] = matches[1]
                match_info['team_a'] = matches[2]
                match_info['team_b'] = matches[3]
                match_info['time'] = matches[4]
                match_info['type'] = matches[5]
                    
            else:
                pass
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await callback.message.edit_text('Укажите победителя матча', reply_markup=keyboard)
    
    elif callback.data.startswith('match.win'):
        for matches in matches_info:
            if callback.data == f"match.win_{matches[0]}_a":
                connection = sqlite3.connect('main.db')
                cursor = connection.cursor()

                cursor.execute('UPDATE matches SET (team_a_win, team_b_win) = (?, ?) WHERE match_id == ?', (1, 0, matches[0]))
                cursor.execute('UPDATE matches SET match_status = ? WHERE match_id == ?', ("Finished", matches[0]))

                if (callback.from_user.id, matches[0], 0) in predicts_info:
                    cursor.execute('UPDATE users SET (predictions_correct, predictions_score) = (predictions_correct + ?, predictions_score + ?) WHERE tid == ?', (1, matches[9], callback.from_user.id))

                elif (callback.from_user.id, matches[0], 1) in predicts_info:
                    cursor.execute('UPDATE users SET predictions_incorrect = predictions_incorrect + ? WHERE tid == ?', (1, callback.from_user.id))

                else:
                    pass

                connection.commit()
                connection.close()

            elif callback.data == f"match.win_{matches[0]}_b":

                connection = sqlite3.connect('main.db')
                cursor = connection.cursor()

                cursor.execute('UPDATE matches SET (team_a_win, team_b_win) = (?, ?) WHERE match_id == ?', (0, 1, matches[0]))
                cursor.execute('UPDATE matches SET match_status = ? WHERE match_id == ?', ("Finished", matches[0]))
                
                if (callback.from_user.id, matches[0], 1) in predicts_info:
                    cursor.execute('UPDATE users SET (predictions_correct, predictions_score) = (predictions_correct + ?, predictions_score + ?) WHERE tid == ?', (1, matches[9], callback.from_user.id))

                elif (callback.from_user.id, matches[0], 0) in predicts_info:
                    cursor.execute('UPDATE users SET predictions_incorrect = predictions_incorrect + ? WHERE tid == ?', (1, callback.from_user.id))

                else:
                    pass

                connection.commit()
                connection.close()
                
            await callback.answer('Матч закрыт')
            

    
    elif callback.data.startswith('trn.pred.close'):
        for matches in matches_info:
            if callback.data.replace('_', ' ') == f'trn.pred.close_{matches[1]}'.replace('_', ' '):
                if matches[6] == "Upcoming":
                    kb.append([InlineKeyboardButton(text=f"{matches[2]}"+ " - "+f"{matches[3]}", callback_data=f"match.pred.close_{matches[0]}")])
                else:
                    pass
            else:
                pass
        else:
            pass
    
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        if kb != []:
            await callback.message.edit_text('Хорошо, сейчас доступны следующие матчи для закрытия прогнозов:', reply_markup=keyboard)
        else:
            await callback.message.edit_text('Нет доступных матчей')
 

    elif callback.data.startswith('match.pred.close'):
        for matches in matches_info:
            if callback.data == f"match.pred.close_{matches[0]}":
                connection = sqlite3.connect('main.db')
                cursor = connection.cursor()

                cursor.execute(f'UPDATE matches SET match_status = "Live" WHERE match_id == {matches[0]}')

                connection.commit()
                connection.close()

            await callback.answer('Матч закрыт для прогнозов.')



async def main():

    dp = Dispatcher()

    dp.include_router(router)

    # Start event dispatching
    await dp.start_polling(bot)




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())