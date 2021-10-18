#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup as bs
import time
import re



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


def write_csv_file(dict_to_write, file_name, sep, write_header):
    """ recoit un dict_to_write et en écrit le contenu dans un fichier csv file_name 

            dict_to_write est un dict colonne:valeur
            sep précise le séparateur du fichier csv
            write_header permet l'écriture d'une ligne d'entête de colonne
    """
    # :BP: utiliser le module csv qui gére nativement les séparateurs
    if sep is None:
        sep = ";"
           
    data_line = [li for li in dict_to_write.values()]
    # écrire dans le fichier en ajoutant 'append'
    # si le fichier existe déja l'ouvrir avec a sinon avec w
    # :CM: inclure dans un try/execpt pour gérer les cas d'erreur fichier
    with open(file_name, "a", encoding='utf-8') as file:
    # création de l'entête
        if write_header:
            col_header = [li for li in dict_to_write.keys()]
            file.write(sep.join(col_header)) 
            file.write('\n') 
        file.write(sep.join(data_line).strip())
        file.write('\n') 
    return


def scrap_url(url_to_scrap):
    """ recoit une url du site books.toscrap et retourne un dict des données trouvées pour le livre 
    
    liste des champs récupérés : col, valeur
    
    """
    # :BP: liste versus dict : ici seules les clés sont immuables, pas les valeurs -> un dict serait une option plus performante
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
    # traiter si le site a bien retourner la page
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
        # :CM: evt. nettoyer les valeurs de Price, Availabilty pour n'avoir que leurs valeurs numériques 
        # on admet que la devise n'est pas utile dans un champ numérique car aucun champ pour la stocker sauf à choisir type alphanumérique
        dict_of_info['price_excluding_tax'] = re.sub("[a-zA-Z£()\s]+", "",dict_tableau['Price (excl. tax)'][1:])
        dict_of_info['price_including_tax'] = re.sub("[a-zA-Z£()\s]+", "", dict_tableau['Price (incl. tax)'][1:])
        dict_of_info['number_available'] = re.sub("[a-zA-Z()\s]+", "", dict_tableau['Availability'])
        img_file = soup.find(class_="item active").find('img')
        site_parts = url_to_scrap.split('/')
        img_parts = img_file["src"].split('/')
        img_sub_url = "/".join(img_parts[2:])
        img_url = "https://" + site_parts[2:3][0] + "/" +(img_sub_url)

    return dict_of_info


# pages en cours de scrap

start = time.time()
url= 'https://books.toscrape.com/catalogue/the-requiem-red_995/index.html'
       
write_csv_file(scrap_url(url), "books.csv", ";", True)
url= 'https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html'
write_csv_file(scrap_url(url), "books.csv", ";", False)
url= 'https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html'
write_csv_file(scrap_url(url), "books.csv", ";", False)
end = time.time()
print(f'Le temps d"execution a été de {end-start} sec.')