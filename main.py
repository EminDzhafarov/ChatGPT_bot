import telebot
import openai
from settings import *


bot = telebot.TeleBot(API_TOKEN) #Токен для телеграма
openai.api_key = OPENAI_KEY #Ключ для OpenAI

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

                response = openai.Completion.create(
                        engine="text-davinci-003", #Модель нейросети
                        prompt= text_input, #Сам запрос
                        temperature=0.3, #Параметр от 0 до 2, от более конкретной выдачи до полета фантазии
                        max_tokens=1200, #Количество токенов, которое вернет нейросеть
                        top_p=0.5, #Процент самых вероятных от возвращенных токенов
                        frequency_penalty=0.2, #Снижает вероятность повторного использования слова в ответе нейросети
                        presence_penalty=0, #Увеличивает вероятность использования слов из запроса в ответе
                )

                answer = response["choices"][0]["text"] + "\n" #Получаем ответ от нейросети
                bot.delete_message(message.chat.id, message.message_id + 1) #Удаляем временное сообщение с часами
                bot.send_message(message.chat.id, answer.strip()) #Отправляем ответ пользователю

bot.polling(none_stop=True) #Постоянно принимаем сообщения