import smtplib
import feedparser
import os
import datetime
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver

driver = webdriver.Chrome()

driver.get('https://www.jw.org/en/library/videos/#en/categories/LatestVideos')

os.environ['WDM_LOG_LEVEL'] = '0'

driver.minimize_window()

driver.get('https://www.jw.org/en/library/videos/#en/categories/LatestVideos')

WebDriverWait(driver,100).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "contentArea"))) 

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

videos_list = []
book_list = []
pics_list = []
news_list = []
history = []

try:
    with open('C:\\Python JW News\\history.json') as f:
        history = json.load(f)
except:
    print("File empty") 
                    
for link in soup.find_all("div", {"class":"synopsis lss desc showImgOverlay hasDuration jsLanguageAttributes dir-ltr lang-en ml-E ms-ROMAN"}):
    href = link.a['href']
    text = link.find_all('a', {'class':'jsNoScroll'})[1].text
    image = link.img['src']

    links_dict = {}
    links_dict['Title'] = text
    links_dict['Image'] = image
    links_dict['Link'] = href

    if href not in history:

        videos_list.append(links_dict)
        history.append(href)

        with open('C:\\Python JW News\\history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    else:
        continue

driver.get('https://www.jw.org/en/library/books')

WebDriverWait(driver,100).until(EC.presence_of_element_located(
        (By.ID, "pubsViewResults"))) 

try:
    with open('C:\\Python JW News\\history.json') as f:
        history = json.load(f)
except:
    print("File empty") 

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

for link in  soup.find_all("div", {"class":"publicationDesc"}):
    href = "https://www.jw.org" + link.a['href']
    title = link.text.strip()

    books_dict = {}
    books_dict['Link'] = href
    books_dict['Title'] = title

    if href not in history:

        book_list.append(books_dict)
        history.append(href)

        with open('C:\\Python JW News\\history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    else:
        continue

for pic in soup.find_all("div", {"class":"cvr-wrapper"}):
    image = pic.img['src']

    pics_list.append(image)

d = feedparser.parse('https://www.jw.org/en/whats-new/rss/WhatsNewWebArticles/feed.xml')

try:
   with open('C:\\Python JW News\\history.json') as f:
        history = json.load(f)
except:
    print("File empty")

for entry in d.entries:
    news_dict = {}
    news_title = entry.title
    news_link = entry.link

    news_dict['Link'] = news_link
    news_dict['Title'] = news_title

    try:
        news_img = entry.summary.split('=')[3].split(' ')[0].replace('"', '')
        news_dict['Image'] = news_img
    except:
        news_dict['Image'] = ""

    if news_link not in history:

        news_list.append(news_dict)
        history.append(news_link)

        with open('C:\\Python JW News\\history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    else:
        continue

videos = ""
news = ""
books = ""
reading = ""
none = ""
count = 0

with open("C:\\Python JW News\\bible.txt") as f:
    bible = lines = f.readlines()

with open("C:\\Python JW News\\days.txt") as f:
    reading_links = lines = f.readlines()

x = datetime.datetime.now()

day_of_year = x.strftime("%j")

day_of_year = int(day_of_year)

slice_of_year = day_of_year - 1

day_list = bible[slice_of_year]

script_list = reading_links[slice_of_year]

today = x.strftime("%A, %B, %d")

reading += open("C:\\Python JW News\\reading.html").read().format(Script=script_list, Day=day_list, YearDay=day_of_year, Today=today)

reading = "<tr><td class='content'><h1>Read the Bible Daily</h1>" + reading + "</td></tr>"

for i in videos_list:
    videos += open("C:\\Python JW News\\video.html").read().format(Text1=videos_list[count]['Title'], 
                                            Link1=videos_list[count]['Link'], 
                                            Img1=videos_list[count]['Image'])
    count += 1

count = 0

if videos_list != []:
    videos = "<tr><td class='content'><h1>Latest Videos</h1>" + videos + "</td></tr>"

for i in news_list:
    news += open("C:\\Python JW News\\news.html").read().format(Text2=news_list[count]['Title'], 
                                            Link2=news_list[count]['Link'], 
                                            Img2=news_list[count]['Image'])
    count += 1

count = 0

if news_list != []:
    news = "<tr><td class='content'><h1>Latest News</h1>" + news + "</td></tr>"

for i in book_list:
    books += open("C:\\Python JW News\\books.html").read().format(Text3=book_list[count]['Title'], 
                                            Link3=book_list[count]['Link'], 
                                            Img3=pics_list[count])
    count += 1

count = 0

if book_list != []:
    books = "<tr><td class='content'><h1>Latest Books</h1>" + books + "</td></tr>"



end = open("C:\\Python JW News\\end.html").read()

emails = []
email_list = []

text = open("C:\\Python JW News\\email_list.txt", "r")
emails = text.readlines()

for line in emails:
    email_list.append(line.strip())
    
me = "JW Newsfeed <jworgnewsfeed@gmail.com>"
you = "jworgnewsfeed@gmail.com"
#them = ["camster91@gmail.com"]
them = email_list

msg = MIMEMultipart('alternative')
msg['Subject'] = "JW.ORG Update"
msg['From'] = me
msg['To'] = you

text = "HTML only. Please enable HTML email."
        
html = open("C:\\Python JW News\\main.html").read() + reading + videos + news + books + none + end

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

#if news_list or videos_list or book_list != []:
    
msg.attach(part1)
msg.attach(part2)

mail = smtplib.SMTP('smtp-relay.sendinblue.com:587')

#mail.ehlo()

mail.starttls()

mail.login('camster91@gmail.com', '0h65mJPSk7Iz4Dwn')
mail.sendmail(me, [you] + them, msg.as_string())
mail.quit()

driver.quit()