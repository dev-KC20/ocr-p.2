#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup as bs
import time
import re
import csv



# Conseil Mentor :CM: baisser le délai d'attente car le site est dédié aux étudiants
BE_NICE = 0





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


def scrap_url(url_to_scrap):
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
    response = requests.get(url_to_scrap)
    
    # délai pour ne pas surcharger le site
    time.sleep(BE_NICE)
    # traiter si le site a bien retourné la page
    if response.ok:
        # response.encoding = 'ISO-8859-1'
        soup = bs(response.content,features="html.parser")

        dict_of_info['product_page_url'] = url

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
        site_parts = url_to_scrap.split('/')
        img_parts = img_file["src"].split('/')
        img_sub_url = "/".join(img_parts[2:])
        img_url = "https://" + site_parts[2:3][0] + "/" +(img_sub_url)
        dict_of_info['image_url'] = img_url

    return dict_of_info


# pages en cours de scrap

start = time.time()
url= 'https://books.toscrape.com/catalogue/the-requiem-red_995/index.html'
       
write_csv_file(scrap_url(url), "books.csv", True)
url= 'https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html'
write_csv_file(scrap_url(url), "books.csv", False)
url= 'https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html'
write_csv_file(scrap_url(url), "books.csv", False)
end = time.time()
print(f'Le temps d"execution a été de {end-start} sec.')