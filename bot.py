-*- coding: utf-8 -*-
import telebot, random, PIL, sqlite3, os, requests, moviepy, asyncio, time
from PIL import Image, ImageFilter
from telebot import types
from moviepy.editor import *
from moviepy.editor import VideoFileClip
global balance
global vidid
global picid
global chatid
global username
global fname
balance = 0
bot = telebot.TeleBot("token")
db = sqlite3.connect("bot.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS bot (
	shakalov BIGINT)""")

db.commit()
	

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет, отправь мне картинку или видео которое надо зашакалить.')


@bot.message_handler(commands=['help'])
def start_message(message):
	bot.send_message(message.chat.id, 'Это небольшой бот для шакала картинок и видео. С его помощью вы сможете делать постиронию для поднятия настроения.\n\n Мы гарантируем анонимность ваших шакалов т.к. они сразу удаляются после отправления вам. Приятного использования!')

@bot.message_handler(commands=['send'])
def start_message(message):
	try:
		if message.chat.id == adminid:
			msg = bot.send_message(message.chat.id, "Введи айди, сообщение, кол-во раз")
			bot.register_next_step_handler(msg, sendmsg)
		else:
			pass
	except:
		pass

@bot.message_handler(commands=['stats'])
def start_message(message):
	for i in sql.execute("SELECT shakalov FROM bot"):
				balance = i[0]

	bot.send_message(message.chat.id, f"Всего было создано {balance} шакала(-ов)")

def sendmsg(message):
	try:
		message.text = message.text.split(',')
		print(message.text)
		userid = message.text[0]
		msgforuser = message.text[1]
		times = message.text[2]
		times = times.replace(' ', '')

		for i in range(int(times)):
			bot.send_message(userid, msgforuser)
		bot.send_message(message.chat.id, f"Все сообщения отправлены! ({times})")
	except IndexError:
		bot.send_message(message.chat.id, "чета какта нет")

@bot.message_handler(content_types=['photo'])
def getphoto(message):
	global picid
	global balance
	global chatid
	global username
	global fname
	chatid = message.chat.id
	username = message.from_user.username
	fname = message.from_user.first_name

	fileID = message.photo[-1].file_id
	file_info = bot.get_file(fileID)
	picid = message.chat.id
	downloaded_file = bot.download_file(file_info.file_path)
	with open(f"{picid}.jpg", 'wb') as new_file:
		new_file.write(downloaded_file)

	keyboard = types.InlineKeyboardMarkup()
	item1 = types.InlineKeyboardButton("2x", callback_data='pic2')
	item2 = types.InlineKeyboardButton("3x", callback_data='pic3')
	item3 = types.InlineKeyboardButton("5x", callback_data='pic5')
	item4 = types.InlineKeyboardButton("10x", callback_data='pic10')
	item5 = types.InlineKeyboardButton("15x (опасно)", callback_data='pic15')
	keyboard.add(item1, item2, item3, item4, item5)

	bot.send_message(message.chat.id, "Выбери степень шакалистости", reply_markup=keyboard)

@bot.message_handler(content_types=['video'])
def getvideo(message):
	global vidid
	global vidwidth
	global vidheight
	global currentproc

	if message.video.file_size > 20971520:
		bot.send_message(message.chat.id, "Вес видео не должен превышать 20 мегабайт (ограничения телеграма ¯\_(ツ)_/¯)")
	else:
		bot.send_message(message.chat.id, "Загружаем видео...")
		vidwidth = message.video.width
		vidheight = message.video.height
		File_ID = message.video.file_id
		file_info = bot.get_file(File_ID)
		downloaded_file = bot.download_file(file_info.file_path)
		vidid = message.chat.id

		with open(f"{vidid}.mov", 'wb') as new_file:
			new_file.write(downloaded_file)

		print(f'Сохранено видео юзера {vidid}.mp4')

		keyboard = types.InlineKeyboardMarkup()
		item1 = types.InlineKeyboardButton("2x", callback_data='vid2')
		item2 = types.InlineKeyboardButton("3x", callback_data='vid3')
		item3 = types.InlineKeyboardButton("5x (опасно)", callback_data='vid5')
		item4 = types.InlineKeyboardButton("10x (очень опасно)", callback_data='vid10')
		keyboard.add(item1, item2, item3, item4)

		bot.send_message(message.chat.id, "Выбери степень шакалистости", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def sahakal(call):
	global balance
	global chatid
	global username
	global fname
	global vidid
	global picid
	global vidwidth
	global vidheight
	global shakalistost
	global msgid
	global inq
	chatid = call.message.chat.id
	username = call.message.from_user.username
	fname = call.message.from_user.first_name
	msgid = call.message.message_id
	if call.message:
		if call.data[:3] == "pic":
			shakalistost = int(call.data[3:])
			image = Image.open(f"{call.message.chat.id}.jpg")
			comprsw, comprsh = image.size
			image = image.resize((comprsw // shakalistost, comprsh // shakalistost), PIL.Image.ANTIALIAS)
			image = image.resize((comprsw * 1, comprsh * 1), PIL.Image.ANTIALIAS)
			image.save(f'{call.message.chat.id}.jpg', quality=10)

			photo = open(f'{call.message.chat.id}.jpg', 'rb')
			bot.send_photo(chatid, photo)
			photo.close()
			os.remove(f"{call.message.chat.id}.jpg")

			for i in sql.execute("SELECT shakalov FROM bot"):
				balance = i[0]

			sql.execute(f'UPDATE bot SET shakalov = {balance + 1}')
			db.commit()

			print(f'Создан {balance + 1}-ый шакал {call.message.chat.id}.jpg юзером {call.message.chat.username}({call.message.chat.id})')
			bot.edit_message_text(chat_id=chatid, message_id=msgid, text=f"Шакалистость {shakalistost}x", reply_markup=None)
		elif call.data[:3] == "vid":
			shakalistost = int(call.data[3:])
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Шакалистость {shakalistost}x. Ожидайте...", reply_markup=None)
			video = VideoFileClip(f"{call.message.chat.id}.mov")
			vidheight2 = vidheight // shakalistost
			vidheight2 = int(vidheight2)
			clip_resized = video.resize(height=vidheight2)
			clip_resized.write_videofile(f"{call.message.chat.id}.mp4", bitrate='200k', audio_bitrate='20k', fps=20)
			video.close()

			vidfinal = open(f'{call.message.chat.id}.mp4', 'rb')
			bot.send_video(call.message.chat.id, vidfinal)
			vidfinal.close()
			time.sleep(0.5)
			os.remove(f"{call.message.chat.id}.mov")
			os.remove(f"{call.message.chat.id}.mp4")

			for i in sql.execute("SELECT shakalov FROM bot"):
				balance = i[0]

			sql.execute(f'UPDATE bot SET shakalov = {balance + 1}')
			db.commit()

			print(f'Создан {balance + 1}-ый видеошакал {call.message.chat.id}.mp4 юзером {call.message.chat.username}({call.message.chat.id})')
		else:
			pass



print("бот робит")
bot.polling()
