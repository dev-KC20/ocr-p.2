#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup as bs
import time
import re
import csv


# def initialisation():

# :CM: baisser le délai d'attente car le site est dédié aux étudiants
BE_NICE = 0
# url de home page du site dont les categories sont à scraper
BASE_URL = 'https://books.toscrape.com/'
CSV_FILE = 'catbooks.csv'
# écrire l'entête une seule fois
column_written = False


# construire le dictionnaire des urls de category
# accéder et charger la page
response = requests.get(BASE_URL)
# délai pour ne pas surcharger le site
time.sleep(BE_NICE)
# traiter si le site a bien retourné la page
if response.ok:
    soup = bs(response.content,features="html.parser")
    DICT_CAT_URL = {}
    # se positionner dans le sous menu de navigation de la home page
    list_category = soup.find_all(class_="nav nav-list")
    # collecte des urls des catégory de la home page
    for line in list_category[0].li.ul.find_all(href=True):
    #for sub_line in line:
        # print(f' category: {(line.string.strip())} @ {line.get("href")} ')
        DICT_CAT_URL[line.string.strip()] = BASE_URL + line.get("href")
    # return




def convert_line_table(table_soup_tag):
    """ recoit un élément Tag de soup issu d'un tableau pour retourner un dict {clé, valeur} du livre
        'tr' identifie les lignes
        'td' identifie les clés et 'th' les valeurs
    
    """ 
    if type(table_soup_tag) is None:
        return ['wrong input type']
        # Best Practise :BP: éviter les boucles for imbriquées 
    dict_info_livre = {}
    for tp in table_soup_tag.findAll("tr"): 
        inter = tp.find_all(["td", "th"])
        dict_info_livre[inter[0].text] = inter[1].text

    return dict_info_livre


def write_csv_file(dict_to_write, file_name):
    """ recoit un dict_to_write et en écrit le contenu dans un fichier csv file_name 

            dict_to_write est un dict colonne:valeur
            sep précise le séparateur du fichier csv
            write_header permet l'écriture d'une ligne d'entête de colonne
    """
           
    data_line = [li for li in dict_to_write.values()]
    global column_written
    try:
        with open(file_name, "a", newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=dict_to_write.keys(),delimiter=';',
                            doublequote=True)
            if not column_written:
                writer.writeheader()
                column_written = True
            writer.writerow(dict_to_write)
    except IOError:
        print(f" une erreur est survenue à l'écriture du fichier {file_name} : {IOError}")            
    
    return


def scrape_url(url_to_scrape):
    """ recoit une url du site books.toscrape et retourne un dict des données trouvées pour le livre 
    
    liste des champs récupérés : col, valeur
    
    """
    dict_of_info = {
            "product_page_url":'',
            "universal_product_code [upc]":'',
            "title":'',
            "price_including_tax":'',
            "price_excluding_tax":'',
            "number_available":'',
            "product_description":'',
            "category":'',
            "review_rating":'',
            "image_url":''
    }
    # conversion alpha anglais en entier alpha
    dict_of_rating = {
        "One":'1', 
        "Two":'2', 
        "Three":'3', 
        "Four":'4', 
        "Five":'5', 
        }
# accéder et charger la page
    response = requests.get(url_to_scrape)
    
    # délai pour ne pas surcharger le site
    time.sleep(BE_NICE)
    # traiter si le site a bien retourné la page
    if response.ok:
        # response.encoding = 'ISO-8859-1'
        soup = bs(response.content,features="html.parser")

        dict_of_info['product_page_url'] = url_to_scrape

        title = soup.find(class_="col-sm-6 product_main").h1
        dict_of_info['title'] = title.text

        product_description = soup.find(id="content_inner").find_next('h2').find_next('p')
        dict_of_info['product_description'] = product_description.text
        # :CM: evt. transformer valeur alpha "Five" en numérique "5"
        star_rating = soup.find(class_="col-sm-6 product_main").find_next('p').find_next('p').find_next('p').attrs
        dict_of_info['review_rating'] = dict_of_rating[list(star_rating.values())[0][1]]
        
        category_crumb = soup.find(class_="breadcrumb").find_all('li')
        category_book = []
        for cc in category_crumb[1:]:
            if cc.text != title.text:
                category_book.append(cc.text.strip())
        category = category_book[1:2][0]
        dict_of_info['category'] = category
        
        table_prod =  soup.find(class_="table table-striped")

        dict_tableau = convert_line_table(table_prod)
        dict_of_info['universal_product_code [upc]'] = dict_tableau['UPC']
        # on admet que la devise n'est pas utile dans un champ numérique car aucun champ pour la stocker sauf à choisir type alphanumérique
        dict_of_info['price_excluding_tax'] = re.sub("[a-zA-Z£()\s]+", "",dict_tableau['Price (excl. tax)'][1:])
        dict_of_info['price_including_tax'] = re.sub("[a-zA-Z£()\s]+", "", dict_tableau['Price (incl. tax)'][1:])
        dict_of_info['number_available'] = re.sub("[a-zA-Z()\s]+", "", dict_tableau['Availability'])
        img_file = soup.find(class_="item active").find('img')
        site_parts = url_to_scrape.split('/')
        img_parts = img_file["src"].split('/')
        img_sub_url = "/".join(img_parts[2:])
        img_url = "https://" + site_parts[2:3][0] + "/" +(img_sub_url)
        dict_of_info['image_url'] = img_url

    return dict_of_info

def scrape_category_page(url_page):
    """ recoit l'url d'une catégorie de livre et retourne la liste des urls de livre associés et event. l'url page suivante
    
    Keywords:
    url_page: l'url d'une page de livre à scraper
    list_url_of_book : liste d'url de livre correspondant à la category_to_search
    next_page_url: retourne l'url de la page suivante, vide si dernière page
    
    """
    list_url_of_book = []
    next_page_url = ''
    base_url_page = ''
    # constitution de l'url de base de la category par ex. "https://books.toscrape.com/catalogue/category/books/fantasy_19/"
    if url_page != '':
        # manually parsing url
        url_parts = url_page.split('/')
        base_url_page = "https://" + "/".join(url_parts[2:7]) + "/"

        # accéder et charger la page
        response = requests.get(url_page)

        # délai pour ne pas surcharger le site
        time.sleep(BE_NICE)
        # traiter si le site a bien retourné la page
        if response.ok:
            soup = bs(response.content,features="html.parser")
#           collecte des urls des livres de la page
            list_book_page1 = soup.find_all(class_="image_container")
            for book in list_book_page1:
                list_url_of_book.append(BASE_URL + 'catalogue/' + book.find(href=True)['href'].replace('../',''))

            # y a t-il une autre/next page dans la soup actuelle ?
            next_page = soup.find_all(class_="next")
#           collecte de l'url de la page de category suivante si elle existe
            if next_page is not None and len(next_page) != 0:
                next_page_short_url = next_page[0].find(href=True)["href"]
                next_page_url = base_url_page + next_page_short_url
            # else:            
                # next_page_url = ''
        
    return list_url_of_book, next_page_url


def scrape_category(category_url_index):
    """ recoit l'url d'une catégorie de livre et retourne la liste des urls de livre associés
    
    Keywords:
    category_url_index : url de l'index de la catégorie cherchée
    list_url_of_book : liste d'url de livre correspondant à la category_to_search
    
    """
    list_url_of_book = []
    if category_url_index != '':
        go_find = scrape_category_page(category_url_index)
        if go_find[0] != '':
            list_url_of_book.extend(go_find[0])
            if go_find[1] != '':
                while go_find[1] != '':
                    # cherche les livres de l'url next
                    go_find = scrape_category_page(go_find[1])
                    if go_find[0] != '':
                           list_url_of_book.extend(go_find[0])

        # print(f' # books in {category_to_search} category: {len(list_url_of_book)} ')
    return list_url_of_book

def get_category_url(category_to_search):
    """ recoit le nom d'une category et retourne l'url de cette catégorie de livre 
    
    Keywords:
    category_to_search: nom de la catégorie cherchée
    category_url_index : url de l'index de la catégorie cherchée
    
    """
  
    category_url_index = ''
    if category_to_search != '':
        category_url_index = DICT_CAT_URL[category_to_search]

        
    return category_url_index

def main():

    # initialisation()
    # temps d'execution = end-start
    start = time.time()
    # pour chaque livre trouvé dans la category, ecrire dans le fichier csv
    for book in scrape_category(get_category_url('Fantasy')):
        write_csv_file(scrape_url(book), CSV_FILE)

    end = time.time()
    print(f'Le temps d"execution a été de {end-start} sec.')

    return


if __name__ == "__main__":
    main()

# DONE: écrire dans csv entête de colonne s'il n'existe pas déja
