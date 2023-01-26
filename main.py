import os
import telebot
import tweepy
import schedule
import time
from threading import Thread

twitter_token = ""
telegram_token = ""
bot = telebot.TeleBot(telegram_token)

def get_last_tweets():
    with open('users.txt', 'r') as original: data = original.read()

    for user_name in data.splitlines():
        try:
            auth = tweepy.OAuth2BearerHandler(twitter_token)
            api = tweepy.API(auth)

            tweets_list = api.user_timeline(screen_name=user_name)
            tweet = tweets_list[0]
            with open('posts.txt', 'r') as orginal_post: post = orginal_post.read()
            if str(tweet.id) in post.splitlines() and tweet != None:
                #print("tweet contains")
                continue
            else:
                string_result = ""
                if post[:2] == "\n":
                    string_result = post + "\n" + str(tweet.id)
                else:
                    string_result = post + str(tweet.id) + "\n"
                with open('posts.txt', 'w') as post_modified: post_modified.write(string_result)
                bot.send_message(1098617221, "https://twitter.com/" + str(user_name) + "\n\n" + str(tweet.text) + "\n\n" + "https://twitter.com/twitter/statuses/" + str(tweet.id))
        except tweepy.errors.NotFound:
            users = data.splitlines()
            users.remove(user_name)
            final = ""
            for line in users:
                if final[:2] == "\n":
                    final = final + "\n" + line
                else:
                    final = final + line + "\n"
            with open('users.txt', 'w') as modified: modified.write(final)
            bot.send_message(1098617221, "Пользователь " + user_name + " не существует. Он удален из вашего списка.")
        except IndexError:
            continue
        except tweepy.errors.Unauthorized:
            users = data.splitlines()
            users.remove(user_name)
            final = ""
            for line in users:
                if final[:2] == "\n":
                    final = final + "\n" + line
                else:
                    final = final + line + "\n"
            with open('users.txt', 'w') as modified: modified.write(final)
            bot.send_message(1098617221, "Пользователь " + user_name + " в бане. Он удален из вашего списка.")


@bot.message_handler(commands=["start"])
def handle_text(message):
    bot.send_message(1098617221, 'Добро пожаловать в бота!')


@bot.message_handler(commands=["add"])
def handle_text(message):
    with open('users.txt', 'r') as original:
        data = original.read()
    if message.text[5:] in data.splitlines():
        bot.send_message(1098617221,
                         'Пользователь ' + message.text[5:] + " уже добавлен!")
    else:   
        string_result = ""
        if data[:2] == "\n":
            string_result = data + "\n" + message.text[5:]
        else:
            string_result = data + message.text[5:] + "\n"
        with open('users.txt', 'w') as modified: modified.write(string_result)
        bot.send_message(1098617221, 'Вы добавили: ' + message.text[5:])


@bot.message_handler(commands=["remove"])
def handle_text(message):
    with open('users.txt', 'r') as original: data = original.read()
    if message.text[8:] not in data.splitlines():
        bot.send_message(
            1098617221, 'Пользователя ' + message.text[8:] + " нет в вашем списке.")
    else:
        users = data.splitlines()
        users.remove(message.text[8:])
        final = ""
        for line in users:
            if final[:2] == "\n":
                final = final + "\n" + line
            else:
                final = final + line + "\n"
        with open('users.txt', 'w') as modified: modified.write(final)
        bot.send_message(1098617221, 'Вы удалили: ' + message.text[8:])


@bot.message_handler(commands=["mylist"])
def handle_text(message):
    with open('users.txt', 'r') as original:
        data = original.read()
    mylist = data.splitlines()
    if not mylist:
        bot.send_message(1098617221, "Ваш список пуст.")
    else:
        bot.send_message(1098617221, 'Ваш список отслеживания: \n' + data)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(1098617221, 'Неизвестная команда')


def do_schedule():
    schedule.every(60).seconds.do(get_last_tweets)

    while True:
        schedule.run_pending()
        time.sleep(1)


def main_loop():
    thread = Thread(target=do_schedule)
    thread.start()
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main_loop()
