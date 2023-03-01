import telebot
import openai
import requests
from settings import *


bot = telebot.TeleBot(API_TOKEN) #Токен для телеграма
openai.api_key = OPENAI_KEY #Ключ для OpenAI
model = "gpt-3.5-turbo"

@bot.message_handler(commands=["start"])
def start(message):
    """Начало, реагирует на /start"""
    bot.send_message(message.chat.id,
                     'Привет! Это бот-прослойка для работы с ChatGPT, задай мне вопрос. \n'
                     'Также я могу сгенерировать изображение, для этого напишите "imagine" '\
            'и далее опишите картинку, которую хотите получить.')

@bot.message_handler(content_types=['text'])
def chatgpt(message):
        """
        Реагируем на любое отправленное сообщение,
        Делаем запрос к OpenAI API,
        Возвращаем ответ нейросети
        """
        bot.send_message(message.chat.id, '⌛') #Песочные чатики для юзера, чтобы не подумал, что все сломалось
        if message.text[0:7] == "imagine" or message.text[0:7] == "Imagine": #Pic, если сообщение начинается с imagine
                response = openai.Image.create(
                        prompt= message.text, #Запрос к нейросети
                        n=1,
                        size="1024x1024" #Размер картинки
                )
                image_url = response['data'][0]['url'] #Получаем ссылку на сгенерированную картинку
                bot.delete_message(message.chat.id, message.message_id + 1) #Удаляем временное сообщение с часами
                bot.send_photo(message.chat.id, image_url) #Отправляем картинку юзеру
        else:
                text_input = str(message.text) #Принимаем текст из сообщения, преобразуем в строку
                text_input = text_input.strip() #Убираем лишние пробелы

                prompt = text_input #Запрос

                json_data = {
                        "model": model, #Модель (GPT3.5-Turbo
                        "messages": [
                                {
                                        "role": "user",
                                        "content": prompt
                                }
                        ]
                }

                response = requests.post(
                        "https://api.openai.com/v1/chat/completions", #Запрос к API
                        headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {openai.api_key}"
                        },
                        json=json_data
                )

                if response.status_code == 200: #Если есть положительный ответ от сервера
                        output = response.json()

                        if "choices" in output:
                                for choice in output["choices"]:
                                        if "message" in choice and "content" in choice["message"]:
                                                answer = choice["message"]["content"]

                                        else:
                                                bot.send_message(message.chat.id, 'Нет ответа от разума')
                        else:
                                bot.send_message(message.chat.id, 'Ошибка!')


                bot.delete_message(message.chat.id, message.message_id + 1) #Удаляем временное сообщение с часами
                bot.send_message(message.chat.id, answer.strip()) #Отправляем ответ пользователю

bot.polling(none_stop=True) #Постоянно принимаем сообщения