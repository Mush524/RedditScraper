import os
import random
import requests
from os import path
from time import sleep
from bs4 import BeautifulSoup

sub = input("Sub to scrape r/")
url = "https://old.reddit.com/r/"+sub

cat = {"top":"/top/?sort=top&t=", "hot":"", "new":"/new/", "controversial":"/controversial/"}
choice = input("Category to scrape [top,hot,new,controversial]: ")   
a = 1
path = list("RedditScraper/"+sub+choice.capitalize())

if choice == "top":
    time = input("Top posts from [day,month,week,year,all]: ")
    url += cat[choice]+time 
    path += time.capitalize()
else: 
    url += cat[choice]

path += str(a)
while os.path.exists("".join(path)):
    a += 1
    path[-1] = str(a)
path = "".join(path)
os.system("mkdir "+path)

print("Scraping "+url)
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"}
cookies = {"over18": "1"}

#Will find the image link depending on the kind of post
def findImage(post):
    if post[-4] == ".":
        return post

    #Advert returns None
    elif "https://alb.reddit.com/" in post:
        return None

    elif "comments/" in post:
        r2 = requests.get("https://old.reddit.com"+post, headers=headers, cookies=cookies)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        if soup2.find("img", {"class":"preview"}):
            #This will replace the link same as with a gallery
            commentLink = soup2.find("img", {"class":"preview"}).get("src")
            return commentLink.replace("preview.redd.it", "i.redd.it").split(".jpg", 1)[0]+".jpg"       
        else:
            return None 

    elif "gallery/" in post:
        gallery = []
        i = 0
        r2 = requests.get(post, headers=headers, cookies=cookies)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        #If the post is a gallery the link will be scraped for each image
        for item2 in soup2.find_all("a", {"target":"_blank"}):
            if "comments/" not in item2.get("href"):
                i += 1
                #preview.redd.it will give error 403 so the link is replaced
                galleryLink = item2.get("href").replace("preview.redd.it", "i.redd.it")
                os.system(f"wget -O {path}/{str(x)}[{str(i)}].jpg {galleryLink}")
                sleep(random.uniform(0.2, 2))

        return "gallery"
        
x = 1
times = int(input("Number of posts to scrape: "))

while x <= times:
    try:
        r = requests.get(url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
    except requests.exceptions.ConnectionError:
        print("\nNo internet connection.")
        break

    #For each post the link will be found with findImage and then saved with wget
    for item in soup.find_all("a", {"data-event-action":"title"}):
        link = findImage(item.get("href"))   

        if link == "gallery":
            x += 1
            if x >= times:
                break

        elif link != None:
            os.system(f"wget -O {path}/{str(x)+link[-4:]} {link}")
            x += 1
            if x >= times:
                break
            sleep(random.uniform(0.2, 2))

    try:
        url = soup.find("a", {"rel":"nofollow next"}).get('href')
    except AttributeError:
        print("All pages have been scraped.")
        break

print(str(x-1)+" images scraped.")