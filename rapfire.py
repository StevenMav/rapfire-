#RAPFIRE

# Librairies
import sys
import pymongo
import requests
from elasticsearch import Elasticsearch
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, request, render_template, url_for


#
base_url = 'https://www.hotnewhiphop.com/videos/' #url de base qu'on va utiliser pour le scraping
userAgent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} #user agent pour chaque navigateur excepté edge ou internet explorer 
#timeOut = 10 
chrome_options = Options() #options() va nous permettre de paramétrer le webdriver
chrome_options.add_argument("--headless") # permet de lancer le driver chrome sans entête, cela permet de récuperer le code des éléments d'une page web générés en javascript
chrome = webdriver.Chrome(executable_path=r".\chromedriver_win32\chromedriver", options = chrome_options) #initialisation du driver Chrome
start_time = 0 

# 
def replace_all(text, dic):
    if text == None:
        return None
    else:
        for i, j in dic.items():
            text = text.replace(i, j)
        return text



val = input("\n Please tell me how many pages do you want to scrap: ")
pages = int(val)
# Scrapping hothiphop et youtube
def scrapping(pages):
    print("\n Vous avez choisi de scraper "+pages+"page(s)")
    start_time = time.time()
    artist_list = []
    title_list = []
    date_list = []
    link_list = []
    yt_link_list = []
    d = {'-embed/':".com/watch?v=", "hnhh.co/":"www.", "?show_controls=1&playlist=1&autoplay=":""}
    for i in range(pages):
        url = f'{base_url}{i}'
        response = requests.get(url = url, headers=userAgent)
        page = response.content
        soup = BeautifulSoup(page, "html.parser")
        artists = soup.find_all('div', {'class': 'grid-item-artists'})
        for elt in artists:
            artist_list.append(elt.text.strip().replace('\xa0', " ")) 
        date = soup.find_all('span', {'class': 'grid-item-time song pull-right'})
        for elt in date:
            date_list.append(elt.text.strip())
        a = soup.find_all('a', {'class': 'grid-item-title'}) 
        for elt in a:    
            title_list.append(elt.string.strip())
            link_list.append("https://www.hotnewhiphop.com" + elt['href']) # on ajoute "https://www.hotnewhiphop.com" car on ne récupère que la 2eme partie du lien sur le site, on obtient alors le lien vers l'aticle 
        for link in link_list:
            response2 = requests.get(url=link, headers=userAgent)
            page2 = response2.content
            soup2 = BeautifulSoup(page2, "html.parser")
            links = soup2.find_all('iframe', {'width': '740'}) # trouver tous les éléments html (liens vidéos youtube embarquées) dont le tag est 'iframe' et la valeur de l'attribut width est 740
            for elt in links:
                yt_link_list.append(replace_all(elt['src'], d)) # récupération des liens précédents (dans l'attribut source), nettoyage des données pour obtenir le lien vers la video youtube
    view_count_list = []
    comment_count_list = []
    likes_list = []
    dview = {"\u202f": "", " vues": ""}
    dcom = {'\u202f':'', ' commentaires\nTRIER PAR':''}
    dlike = {
        '\u202f':'',
        '\xa0"J\'aime"':''
    }
    for i in yt_link_list: #pour chaque lien url contenu dans yt_link_list
        url = i  # la variable url prend la valeur de ce lien
        chrome.get(url) # récupération du contenu html de la page youtube correspondante
        chrome.execute_script("window.scrollTo(0, 500);")  # défilement vers le bas de la page 
        time.sleep(5)      # le driver fait une pause dans le défilement
        chrome.execute_script("window.scrollTo(1, 3000);")  #re-défilement (on execute ce défilement de page car les commentaires et certaines données javascript ne sont chargées qu'àprès défilement)
        try:
            views=chrome.find_element_by_class_name("view-count")
            view_count_list.append(replace_all(views.text, dview))
        except NoSuchElementException:
            view_count_list.append(np.nan) #si l'élément n'est pas trouvé, ajouter 'NaN' 
        try:
            comment=chrome.find_element_by_class_name("ytd-comments-header-renderer")
            comment_count_list.append(replace_all(comment.text, dcom))
        except NoSuchElementException:
            comment_count_list.append(np.nan)
        try:
            like=chrome.find_element_by_class_name('ytd-toggle-button-renderer')
            likes_list.append(replace_all(like.find_element_by_css_selector('yt-formatted-string').get_attribute('aria-label'),dlike))  #on récupère l'attribut (texte) contenu dans le selecteur css 'yt-formatted-string'
        except NoSuchElementException:
            likes_list.append(np.nan)
    ddf = {
        'Artistes': artist_list,
        'Titre': title_list,
        'Date de sortie': date_list,
        'Lien Youtube': yt_link_list,
        'Vues': view_count_list,
        'Commentaires': comment_count_list,
        'Likes' : likes_list
    }
    df = pd.DataFrame(ddf, columns = ddf.keys())
    for j in range(len(view_count_list)):
        try:
            df['Vues'][j] = int(df['Vues'][j])
        except ValueError:
            df['Vues'][j] = df['Vues'][j]
    for k in range(len(comment_count_list)):
        try:
            df['Commentaires'][k] = int(df['Commentaires'][k])
        except ValueError:
            df['Commentaires'][k] = df['Commentaires'][k]
    for l in range(len(likes_list)):
        try:
            df['Likes'][l] = int(df['Likes'][l])
        except TypeError:
            df['Likes'][l] = df['Likes'][l]
        except ValueError:
            df['Likes'][l] = df['Likes'][l]
		
    liste1 = []
    l=0
    m=0
    while l < len(df):
        liste1.append(df['Titre'][l].split('"'))  #nettoyage des données,
        l+=1                                      #plus précisément des titres récupérés 
    new_title_list = []                           #pour ne garder que ce dont on a besoin
    while m < len(liste1):                        #c'est à dire le titre du clip qui se trouve entre guillemets
        if len(liste1[m]) > 1 and liste1[m][1]:   #et se débarasser du contenu inutile
            new_title_list.append(liste1[m][1])
        else :
            new_title_list.append(liste1[m][0])
        m+=1
    df_title = pd.DataFrame({'Titre':new_title_list})
    df.update(df_title)                           #mise à jour des titres dans notre dataframe                                                      
    df['Indice de popularité'] = 0                                                                                          #ajout d'une colonne "indice de popularité" selon les conditions du nombre de likes, commentaires et j'zaime
    df.loc[(df['Vues'] > 5000000) & (df['Commentaires'] > 20000) & (df['Likes'] > 400000), 'Indice de popularité'] = '***'  # *** = très populaire, buzz
    df.loc[(df['Vues'] > 1000000) & (df['Commentaires'] > 10000) , 'Indice de popularité'] = '**'                           # ** = moyen
    df.loc[(df['Vues'] < 1000000) & (df['Commentaires'] < 10000) , 'Indice de popularité'] = '*'                            # * = pas très populaire
    return df

print("--- Temps d execution : %s secondes ---" % (time.time() - start_time))


# MongoDb
def mongodb(df):
    client = pymongo.MongoClient() #connexion à mongodb
    db = client['Musique']  #Création et stockage de la database "Musique" dans mongodb
    collection = db['Clips'] #Création de la collection "Clips" dans la database 
    dict_df = df.to_dict('list') # conversion du dataframe en dictionnaire de listes = document
    collection.insert_one(dict_df) # insertion du document dans la collection de la base de données




##Fonction recherche 
def search(requete,df):
    if requete == "":
        return df #si la requête est vide
    else : #requete elasticsearch
        QUERY = {
            "query": { 
                "multi_match":{
                    "query" : requete,
                    "fields": ["Titre","Artistes"]
                } 
            }
        }
        results = es_client.search(index="clips", body=QUERY)
    for hit in results['hits']['hits']:
        df_filtered = df[df['Artistes'] == "{Artistes}".format(**hit['_source'])] #base de données filtrée
    return df_filtered


# Lancement du scrapping, stockage dans Mongo
df=scrapping(pages)
mongodb(df)

#ElasticSearch
es_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
documents = df.fillna("").to_dict(orient="records")
##Indexation du dataframe
for doc in documents:
    res = es_client.index(index="clips", doc_type='clip', id=None, body=doc)
	
print(df.info())

#Interface Flask
app = Flask(__name__)
##Page : utilisation de template 
@app.route('/', methods=[ 'POST'])
def index():
    if request.method == 'POST':
        return render_template('accueil.html',data_frame=search(request.form['requete'],df).to_html())
    return render_template('accueil.html',data_frame=df.to_html())
##Lancement de l'interface
if __name__ == '__main__':
    app.run() 