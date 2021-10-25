# ocr-p.2 Utilisez les bases de Python pour l'analyse de marché

Disclaimer

---

This code is part of the openclassrooms learning adventure split in 13 business alike projects.  
  
  
This one is to scrap a static book reseller site and save book title, price, resume, front cover image etc. in a csv file.  
Some materials or links may have rights to be granted by https://openclassrooms.com. 
The additionnal code follows "CC BY-SA ".
  
** Not to be used for production **  


---
## Objet.  
  
Le script p2-03-all-categories-scrape.py permet de scraper l'ensemble des livres du site https://books.toscrape.com.  

Il enregistre les informations des livres dans un fichier csv dont le nom correspondant à la catégorie à laquelle appartient le livre.  
Ainsi le livre "Unicorn Tracks" qui fait parti de la catégorie "Fantasy" aura ses informations stockées dans le fichier Fantasy.csv.  
Par ailleurs, l'image de la couverture du livre sera stockée dans un fichier image au format jpg dont le nom correspond à celui présent dans la colonne 'image_url' du fichier csv.  

  
Les données stockées dans le fichier sont les suivantes :  

* product_page_url
* universal_ product_code (upc)
* title
* price_including_tax
* price_excluding_tax
* number_available
* product_description
* category
* review_rating
* image_url


## Fonctionnement.

Ce script est développé dans le language Python, en version v3.8.8.  
Les 2 autres scripts sont des scrapeurs partiels, l'un pour un livre et l'autre pour une catégorie.   
Ces informations, url du livre et nom de la catégorie sont à modifier avant l'execution de l'un des deux scripts.  
  

Pour utiliser le script p2-03-all-categories-scrape.py,   
il est conseillé sous le prompt bash python (ici cmd Anaconda3 sous Windows 11):  
1. de cloner l'ensemble du répertoire github dans un répertoire local dédié.  
        ``` git clone https://github.com/dev-KC20/ocr-p.2.git  
2. se déplacer dans le sous répertoire de travail ocr-p.2
        ``` cd ocr-p.2
3. de créer un environnement virtuel python, env  
        ``` python -m venv env  
4. d'activer un environnement virtuel python, env  
        ``` env\scripts\activate.bat  
5. d'installer les paquets requis pour mémoire,   
        ``` pip install -r requirements.txt  
6. d'executer le script  
        ``` python p2-03-all-categories-scrape.py    
  
Les fichiers des images de couverture et les fichiers csv sont déposés au niveau du répertoire d'execution    




