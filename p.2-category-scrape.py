#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup as bs
import time
import re
import csv



# :CM: baisser le délai d'attente car le site est dédié aux étudiants
BE_NICE = 0

# url de home page du site dont les categories sont à scraper
BASE_URL = 'https://books.toscrape.com/'

CSV_FILE = 'catbooks.csv'



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


def write_csv_file(dict_to_write, file_name, write_header):
    """ recoit un dict_to_write et en écrit le contenu dans un fichier csv file_name 

            dict_to_write est un dict colonne:valeur
            sep précise le séparateur du fichier csv
            write_header permet l'écriture d'une ligne d'entête de colonne
    """
           
    data_line = [li for li in dict_to_write.values()]

    try:
        with open(file_name, "a", newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=dict_to_write.keys(),delimiter=';',
                            doublequote=True)
            if write_header:
                writer.writeheader()
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

def scrape_category(category_to_search):
    """ recoit le nom d'une catégorie de livre et retourne la liste des urls de livre associés
    
    Keywords:
    category_to_search nom de la catégorie cherchée
    list_url_of_book : liste d'url de livre correspondant à la category_to_search
    
    """
# v1 : commencons par scraper une page de livre 
    category_url_page1 = 'https://books.toscrape.com/catalogue/category/books/fantasy_19/index.html'
    list_url_of_book = []
    # accéder et charger la page
    response = requests.get(category_url_page1)
    
    # délai pour ne pas surcharger le site
    time.sleep(BE_NICE)
    # traiter si le site a bien retourné la page
    if response.ok:
        # response.encoding = 'ISO-8859-1'
        soup = bs(response.content,features="html.parser")

        list_book_page1 = soup.find_all(class_="image_container")
        for el in list_book_page1:
            # print(el.find('src'))
            list_url_of_book.append(BASE_URL + 'catalogue/' + el.find(href=True)['href'].replace('../',''))
        # print(list_url_of_book)

    return list_url_of_book

def main():
# pages en cours de scrape
    start = time.time()
    # scrape_category('Fantasy')
    for book in scrape_category('Fantasy'):
        write_csv_file(scrape_url(book), CSV_FILE, False)

    end = time.time()
    print(f'Le temps d"execution a été de {end-start} sec.')

    return


if __name__ == "__main__":
    main()


