PROJET DATA ENGINEERING
=======================
Auteurs : Lucas NGUYEN et Steven MAVOUNGOU


Presentation
************
RapFire est une application qui récupère les informations des nouveaux clips sur hotnewhiphop.com/videos
Il montre leurs popularités en recupérant aussi leurs nombres de vues, de commentaires et de likes de leurs liens youtube.
Ces données sont présentés dans une interface Flask et sont stockés dans une base Mongo.
Il y a aussi une barre de recherche qui effectue des requête ElasticSearch.

Installations à faire au préalable:
***********************************
Packages: - pymongo
          - requests
          - elasticsearch
          - time
          - pandas
          - numpy
		  - bs4
		  - selenium
		  - flask
		  
Logiciels (installer et mettre à la racine du projet): - elasticsearch-6 https://www.elastic.co/fr/products/elasticsearch
                                                       - driver Chrome https://sites.google.com/a/chromium.org/chromedriver/downloads

Instructions 
************
- Tout d'abord, lancer elasticsearch.bat contenu dans le dossier elasticsearch-6.5.4
- Lancer le programme python rapfire.py dans un terminal à l'aide de la commande 'python rapfire.py' en se plaçant dans le répertoire du projet
- Le scrapping se faisant automatiquement, cela prend du temps donc nous avons réduit le scraping à la 1ere page de clips du site seulement (60 vidéos, environ 10-15 min).
- Sur un navigateur, ouvrez l'interface Flask sur http://127.0.0.1:5000/ 

Fonctionnement
**************
- Scraping : Pour créer notre base de données, on scrape des pages du site www.Hotnewhiphop.com (section vidéos) pour récuperer les noms des artistes, les titres des musiques, les liens vers l'article dédidé à cette musique sur site.
  Sur ces liens, on récupère le lien vers la vidéo Youtube. Enfin on scrape ces liens youtube pour récuperer le nombre de vues, de likes et de commentaires de chaque vidéo.  
  Enfin, après un nettoyage des données on les récupère dans un dataframe
- On stocke la base de donnée sur Mongo grâce a la fonction mongo db
- On initialise une connexion à elastic search ( port 9200)
- On transforme la base de donnée en dictionnaire pour pouvoir mettre chaque ligne dans ElasticSearch
- Parrallelement, on crée une fonction search() qui filtre la base de donnée grâce aux requêtes ElasticSearch qui cherche le mot passé en argument dans tous les titres de clips et dans tous les artistes. 
- On  crée l'application Flask, il n'y a qu'une seule page situé à la racine / qui autorise les methodes POST
- On utilise un template avec render_template() avec comme argument la base de donnée qu'on va afficher dedans
- Si l'utilisateur utilise la barre de recherche situé dans le template , la requpete post sera détecté et on affichera la base de donnée filtré grace à la fonction search() avec le terme que l'utilisateur a rentré.
