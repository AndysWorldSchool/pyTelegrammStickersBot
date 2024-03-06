# -*- coding: cp1251 -*-
import json
import random
from socket import INADDR_MAX_LOCAL_GROUP
import telebot
import io
import time
import re
from telebot import types

#FILENAME = "/data/todo.json" if "AMVERA" in os.environ else "todo.json"

#-----------------------------------------------------------------------
bot = telebot.TeleBot('7115737994:AAEx5r5gXPy6Ek1-E-LxSNGZEezBVKPeH6s')
#-----------------------------------------------------------------------
# ���� � �����

JSON_FILE = './files/config.json'


#-----------------------------------------------------------------------
# �������� ������ � Json �����
def getJsonData(dataName):
    # ��������� ���� JSON � ��������� ������
    with io.open(JSON_FILE, 'r', encoding='utf-8') as config_file:
        config_data = json.load(config_file)

    # �������� ������ �� ����������� ������
    data = config_data.get(dataName, {})

    return data


# �������� ������ �� ����� JSON
def loadData(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}


# ���������� ������ � ���� JSON
def saveData(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
#-----------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handlingStandar(message):   
    markup = types.ReplyKeyboardMarkup()
    btnVoice = types.KeyboardButton('\U0001F381 �������� ������� ����� �����!')
    markup.add(btnVoice)
    bot.send_message(message.chat.id, "<b>������!</b>\n��� � ���� ����?", reply_markup=markup, parse_mode='HTML', protect_content=True)
    
@bot.message_handler(commands=['allstickers'])
def outputAllStickersInStickerpack(message):
    jsonData = loadData(JSON_FILE)
    stickersPackName = jsonData['stickersPacksName']
    
    for stickerPack in stickersPackName:
        pack = bot.get_sticker_set(stickerPack)
        
        stickers = pack.stickers
        
        indSticker = 1

        for sticker in stickers:
            bot.send_message(message.chat.id, str(indSticker))
          
            bot.send_sticker(message.chat.id, sticker.file_id)
                
            print(str(indSticker) + "   " + sticker.file_id + "\n\n")
            indSticker += 1
        
        if stickerPack != stickersPackName[-1]:
            bot.send_message(message.chat.id, "��������� ������ 10 ������, ��� �������� ����������")
            time.sleep(10)

@bot.message_handler(commands=['addexcludedstickers'])
def excludedStickers(message):
    
    bot.send_message(message.chat.id, "�������� ����� ������� ������ ��������, ������� �� ������ ���������.", protect_content=True)
    
    bot.register_next_step_handler(message, selectExcludedStickers)
    
def selectExcludedStickers(message):
    
    stickersNumber = re.sub(r'\s+', '', message.text).split(',')
    
    jsonData = loadData(JSON_FILE)
    stickerPackName = jsonData['stickersPacksName'][0]
    stickerPack = bot.get_sticker_set(stickerPackName)
    stickers = stickerPack.stickers
    
    for item in stickersNumber:
        if not item.isdigit():
            stickersNumber.remove(item)
        
    stickersNumber = list(map(int, stickersNumber))
    
    excludedStickers = []
    
    for item in stickersNumber:
        excludedStickers.append(str(stickers[item - 1].file_unique_id))


    
    addExcludedStickersToJson(excludedStickers)

def addExcludedStickersToJson(excludedStickers : list):
    jsonData = loadData(JSON_FILE)
    
    jsonData['excludedStickers'] = excludedStickers
    
    saveData(jsonData, JSON_FILE)

def voiceRecordingProcessing(message):
    bot.send_message(message.chat.id, "������ ��������� ���������!", protect_content=True)
    
    bot.register_next_step_handler(message, voiceMessageProcessing)
    
def voiceMessageProcessing(message):
    if message.content_type != 'voice':
        bot.reply_to(message, "*** ��-�� ***!\n��� �� ��������� ���������! \U0001F614", parse_mode='HTML', protect_content=True)
        voiceRecordingProcessing(message)
        return

    markup = types.InlineKeyboardMarkup()
    btnYes = types.InlineKeyboardButton('��', callback_data='voice_correct')
    btnNo = types.InlineKeyboardButton('���', callback_data='voice_not_correct')
    markup.row(btnYes, btnNo)
    bot.reply_to(message, "�� �����?", reply_markup=markup, parse_mode='HTML', protect_content=True)

def dropSticker(message):
    jsonData = loadData(JSON_FILE)
    stickerPackName = jsonData['stickersPacksName']
    stickerPack = bot.get_sticker_set(stickerPackName[0])
    stickers = stickerPack.stickers

    bot.send_message(message.chat.id, "�� �������!\n��� ���� �������:", protect_content=True)
    
    correctSticker = False
    while not correctSticker:
        randomNumberSticker = random.randint(0, len(stickers) - 1)
        stickerUID = stickers[randomNumberSticker].file_unique_id
        
        if stickerUID not in loadData(JSON_FILE)['excludedStickers']:
            sticker = stickers[randomNumberSticker]
            correctSticker = True
            
    bot.send_sticker(message.chat.id, sticker.file_id, protect_content=True)

@bot.callback_query_handler(func=lambda callback: True)    
def buttonListener(callback):
    if callback.data == 'voice_correct':
        dropSticker(callback.message)
    elif callback.data == 'voice_not_correct':
        bot.send_message(callback.message.chat.id, "��������� �������, ����������.", protect_content=True)
        voiceRecordingProcessing(callback.message)
        
@bot.message_handler()
def  commandProcessing(message):
    
    if message.text == '\U0001F381 �������� ������� ����� �����!' or message.text == '�������� ������� ����� �����!':
        voiceRecordingProcessing(message)
        
bot.infinity_polling()