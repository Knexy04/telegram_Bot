from bs4 import BeautifulSoup as BS
import requests
import telebot
from telebot import types

f = 'https://www.povarenok.ru/recipes/search/'

buk = {
    'а' : 'a',
    'б' : 'b',
    'в' : 'v',
    'г' : 'g',
    'д' : 'd',
    'е' : 'e',
    'ё' : 'e',
    'ж' : 'zh',
    'з' : 'z',
    'и' : 'i',
    'й' : 'y',
    'к' : 'k',
    'л' : 'l',
    'м' : 'm',
    'н' : 'n',
    'о' : 'o',
    'п' : 'p',
    'р' : 'r',
    'с' : 's',
    'т' : 't',
    'у' : 'u',
    'ф' : 'f',
    'х' : 'h',
    'ц' : 'c',
    'ч' : 'ch',
    'ш' : 'sh',
    'щ' : 'sch',
    'ъ' : '',
    'ы' : 'y',
    'ь' : '',
    'э' : 'e',
    'ю' : 'yu',
    'я' : 'ya',
    ' ' : '-',
}

sort = {
    'По рейтингу':'?orderby=rating#searchformtop',
    'По рейтингу автора':'?orderby=owner_rating#searchformtop',
    'По просмотрам':'?orderby=views#searchformtop',
    'По отзывам':'?orderby=reviews#searchformtop',
    'По дате(сначала новые)':'?orderby=dt+desc#searchformtop',
    'По дате(сначала старые)':'?orderby=dt+asc#searchformtop'
}

def download(url):
    download_soup = requests.get(url).content
    format = url.split('/')[-1]
    with open('img/'+format, "wb") as f:
        f.write(download_soup)
        
            
def string_name(name):
    string_new = ''
    for i in range(len(name)):
        el = buk[name[i]]
        string_new+=el
    string_new+='/~1'
    return string_new

def get_info_resipe(el):
    full_resipe_link = el.find('a').get('href')
    title = el.find('h2').text.strip()
    ing_span = el.select('.ings span > a') 
    ing = ''
    count_m = len(ing_span)
    c=0
    for k in ing_span:
        g = k.text.strip()
        if (count_m-c)==1:
            ing+=g
        else:
            ing+=g
            ing+=', '
        c+=1
    img_url = el.find('img').get('src')
    return full_resipe_link, title, ing, img_url

def main(name):
    global array_recipes
    string_new = string_name(name.lower())
    string_new+=sort['По рейтингу'] #это потом доделать в тг боте
    zap = f + string_new
    l = requests.get(zap)
    html_l = BS(l.text, 'lxml')
    resipes = html_l.select('.item-bl')
    array_recipes = [0]*len(resipes)
    for i in range(len(array_recipes)):
        array_recipes[i] = [0]*4
    count_l = 0
    for el in resipes:
        full_resipe_link, title, ing, img_url = get_info_resipe(el)
        download(img_url)
        name_img = img_url.split('/')[-1]
        array_recipes[count_l][0]=title
        array_recipes[count_l][1]=ing
        array_recipes[count_l][2]=name_img
        array_recipes[count_l][3]=full_resipe_link
        count_l+=1
        
def s_trip(f):
    string = f
    new_string = ''
    for i in range(len(string)):
        if i!=0 and i!=(len(string)-1):
            if (string[i]==' ' and string[i-1]==' ') or string[i]=='\n':
                continue
            else:
                if string[i]!='\n':
                    new_string+=string[i]
        else:
            if string[i]!='\n':
                new_string+=string[i]
    return new_string
        
def full_resipe(link):
    zapros = requests.get(link)
    html_zapros = BS(zapros.text, 'lxml')
    array = []
    m_zapros = html_zapros.select('.item-bl > div')[0]
    title = ''
    try:
        title = m_zapros.find('h2').text.strip()
        array.append(title)
    except:
        pass
    ingredients_string = ''
    try:
        block = m_zapros.select('.ingredients-bl')[0]
        try:
            ing_ar = []
            ingredients = block.select('ul li')
            for ing in ingredients:
                ingred = s_trip(ing.text)
                ing_ar.append(ingred)
            for ing in ing_ar:
                ingredients_string+=ing
                ingredients_string+='\n'
        except:
            pass
    except:
        pass
    if (ingredients_string != ''):
        array.append(ingredients_string)
    time=''
    porcii=''
    try:
        time = block.select('p')[0].text
        time = s_trip(time)
        porcii = block.select('p')[1].text
        porcii = s_trip(porcii)
    except:
        pass
    steps_string = ''
    steps = m_zapros.select('ul > .cooking-bl')
    count_step =1
    for step in steps:
        div_step = step.select('div > p')[0].text
        text_step = str(count_step) + ') ' + s_trip(div_step)
        steps_string+=text_step
        steps_string+='\n'
        count_step+=1
    array.append(steps_string)
    if time!='':
        array.append(time)
    if porcii!='':
        array.append(porcii)
    try:
        m_2 = m_zapros.select('div > div > table')[0]
        tr_1 = m_2.select('tr')[2]
        td = tr_1.select('td')[0].text
        gramm_100 = s_trip(td) + ': '
        tr_3 = m_2.select('tr')[3]
        fff = ''
        for td in tr_3:
            td_3 = td.text
            td_3_itog = s_trip(td_3)
            fff+=td_3_itog
            fff+=' '
        fff.strip()
        fff= defic_func(fff)
        itog_100_gramm = s_trip(gramm_100 + ' ' + fff).strip()
        array.append(itog_100_gramm)
    except:
        pass
    return array
    
def defic_func(string):
    new_s = ''
    s = string
    for i in range(len(s)-1):
        if (s[i+1].isdigit()==True and s[i].isdigit()==False and s[i]!='' and s[i]!=' ' and s[i]!='.' and s[i]!=','):
            new_s+=s[i]
            new_s+= ' - '
        else:
            new_s+=s[i]
    return new_s
    

bot = telebot.TeleBot('')#ваш апи бота в телеграмм
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, "Привет, напиши блюдо которое хочешь увидеть")
    
@bot.message_handler(content_types=["photo"])
def bot_message(message):
     bot.send_message(message.chat.id, "Пошел нахуй, введи название блюда на клаве своей конченной")
     
@bot.message_handler(content_types=["voice"])
def bot_message(message):
     bot.send_message(message.chat.id, "Пошел нахуй, введи название блюда на клаве своей конченной")

@bot.message_handler(content_types=["video"])
def bot_message(message):
     bot.send_message(message.chat.id, "Пошел нахуй, введи название блюда на клаве своей конченной")
     
@bot.message_handler(content_types=["document"])
def bot_message(message):
     bot.send_message(message.chat.id, "Пошел нахуй, введи название блюда на клаве своей конченной")
    
@bot.message_handler(content_types=["text"])
def bot_message(message):
    try:
        global count
        global flag
        if (message.text.lower() == 'далее' or message.text.lower() == 'просмотреть рецепты заного'):
            try:
                count+=1
                if count<10:
                    photo = open('img/'+array_recipes[count][2], 'rb')
                    text_1 = array_recipes[count][0]
                    text_2 = array_recipes[count][1]
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn1 = types.KeyboardButton("Далее")
                    btn2 = types.KeyboardButton("Открыть полный рецепт")
                    markup.add(btn1, btn2)
                    bot.send_photo(message.chat.id, photo)
                    bot.send_message(message.chat.id, text_1 + '\n' +text_2, reply_markup=markup)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn2 = types.KeyboardButton("Просмотреть рецепты заного")
                    markup.add(btn2)
                    count = 0
                    bot.send_message(message.chat.id, 'Блюда закончились, введите другое!', reply_markup=markup)
            except Exception as e:
                bot.send_message(message.chat.id, 'Блюда закончились, введите другое!')
        elif (message.text.lower() == 'открыть полный рецепт'):
            try:
                if count<10:
                    full_link = array_recipes[count][3]
                    array = full_resipe(full_link)
                    result = ''
                    for el in array:
                        result += el
                        result += '\n'
                    if len(result) > 4095:
                        for x in range(0, len(result), 4095):
                            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                            btn1 = types.KeyboardButton("Далее")
                            markup.add(btn1)
                            bot.send_message(message.chat.id, text=result[x:x+4095], reply_markup=markup)
                    elif (len(result)<10):
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton("Далее")
                        markup.add(btn1)
                        bot.send_message(message.chat.id, "Нет полного рецепта", reply_markup = markup)
                    else:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        btn1 = types.KeyboardButton("Далее")
                        markup.add(btn1)
                        bot.send_message(message.chat.id, text=result, reply_markup = markup)
                else:
                    bot.send_message(message.chat.id, 'Блюда закончились, введите другое!')
            except Exception as e:
                bot.send_message(message.chat.id, 'Блюда закончились, введите другое!')
        else:
            try:
                count = 1
                text = message.text
                print(text)
                main(text)
                photo = open('img/'+array_recipes[count][2], 'rb')
                text_1 = array_recipes[count][0]
                text_2 = array_recipes[count][1]
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("Далее")
                btn2 = types.KeyboardButton("Открыть полный рецепт")
                markup.add(btn1, btn2)
                bot.send_photo(message.chat.id, photo)
                bot.send_message(message.chat.id, 'Название: ' +text_1 +'\n'+ 'Интгредиенты: ' +text_2, reply_markup=markup)
            except Exception as e:
                bot.send_message(message.chat.id,'Такого блюда нет, введите другое')
    except Exception as e:
        bot.send_message(message.chat.id,'Такого блюда нет, введите другое')
bot.polling(none_stop=True, interval=0)
    