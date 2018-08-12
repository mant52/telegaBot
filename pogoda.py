import time
import telepot
import requests
import json
import math
from telepot.loop import MessageLoop
from gtts import gTTS
import psycopg2
from urllib.request import urlretrieve

def database_connection():
    try:
        # connection = psycopg2.connect("dbname='spreadsheets' user='antonmelbardis' host='localhost'")
        connection = psycopg2.connect(database='logs', user='mant', password="ninjas52",
        host='telegabotlogs.cpkdiexltofo.eu-west-1.rds.amazonaws.com', port='5432')
    except:
        print ("I am unable to connect to the database")

    connection.set_session(autocommit=True)
    return connection

db = database_connection()
cur = db.cursor()

def handle(msg):

    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'photo':
        print('photo nah')
        bot.download_file(msg['photo'][-1]['file_id'], './file.png')

    # only log the stuff posted on channels
    if 'title' in msg['chat']:
        logGroups(msg)
    # do not log stuff posted in private msgs
    else:
        print('no need for private chats logging')

    if 'text' in msg:
        chat_id = msg['chat']['id']
        query = msg['text']

        query_length = len(query.split())
        if query_length > 1:
            command = query.split(' ', 1)[0]
            text = query.split(' ', 1)[1]
        else:
            command = query

        # print ('Got command: %s' % command)

        if command =='/pogodka':
            bot.sendMessage(chat_id, get_weather(text))
        elif command == '/sendaudio':
            send_audio(text)
            f = open('voice.mp3', 'rb')  # some file on local disk
            bot.sendVoice(chat_id, f)
        elif command == '/nagovoril':
            # get_logs_on_user(msg)
            bot.sendMessage(chat_id, get_logs_on_user(msg))

    else:
        print('Lol')

bot = telepot.Bot('535668550:AAEHj47Ui_MNz3-emYJSOvZDuVt7cZk_0Gw')

MessageLoop(bot, handle).run_as_thread()
print ('I am listening ...')

def get_weather(city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q='+city+'&APPID=ee67652b7c4173586e0d36a6a9052b35&units=metric'
    try:
        response = requests.get(url, stream=True)
        json_data = json.loads(response.text)
        wind = int(float(json_data['wind']['deg']))
        direction = get_wind_direction(wind)
        weather =  str(json_data['weather'][0]['main']) + ' in ' + city + '. Temperature is ' + str(math.ceil(json_data['main']['temp'])) + ' degrees Celsius. Wind is blowing from ' + direction + ' directions at ' + str(json_data['wind']['speed']) + ' m/s.'
        return weather
    except:
        return 'No weather data available for ' + city + '. Try another city.'

def send_audio(text):
    lang = text.split(' ', 1)[0]
    text = text.split(' ', 1)[1]

    tts = gTTS(text=text, lang=lang)
    tts.save('voice.mp3')

def get_wind_direction(wind):
    if wind > int(float(112.5)) & wind < int(float(157.5)):
        wind = 'South East'
    elif wind > int(float(157.5)) & wind < int(float(202.5)):
        wind = 'South'
    elif wind > int(float(202.5)) & wind < int(float(247.5)):
        wind = 'South West'
    elif wind > int(float(247.5)) & wind < int(float(292.5)):
        wind = 'West'
    elif wind > int(float(292.5)) & wind < int(float(337.5)):
        wind = 'North West'
    elif wind > int(float(337.5)) & wind < int(float(360)):
        wind = 'North'
    elif wind > int(float(0)) & wind < int(float(22.5)):
        wind = 'North'
    return wind

def logGroups(msg):
    try:
        text_to_log = msg['text']
        user_id = msg['from']['id']
        first_name = msg['from']['first_name']
        chat_id = msg['chat']['id']
        chat_title = msg['chat']['title']
        message_date = msg['date']
        # SQL to log the message
        cur.execute("""
        INSERT INTO logs (userid, first_name, chatid, chat_title, date, text)
        VALUES (%s, %s, %s, %s, %s, %s);
        """, (user_id, first_name, chat_id, chat_title, message_date, text_to_log))
    except KeyError:
        print ('non-text message')

def get_logs_on_user(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    first_name = msg['from']['first_name']

    sql = "SELECT count(*) from logs WHERE chatid = '%s' AND userid = '%s';" % (chat_id, user_id)
    # print(sql)
    cur.execute(sql)
    results = cur.fetchone()
    return first_name + ' тут нахуячил ' + str(results[0]) + ' сообщений'

while 1:
    time.sleep(10)
