#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup as bs
import time
import sys
import warnings

print(sys.version_info[1])
if sys.version_info[0] < 3:
    warnings.warn("Must be using Python 3")
if sys.version_info[1] < 10:
    warnings.warn("Match inst. of Release 10 of Python 3")

# délai d'attente en 1sec
be_nice = 1





def convert_line_table(table_soup_tag):
    """ recoit un élément Tag de soup issu d'un tableau pour retourner la liste [clé, valeur]
        'tr' identifie les lignes
        'td' identifie les clés et 'th' les valeurs
    
    """ 
    liste_key_value = []
    if type(table_soup_tag) is None:
        return ['wrong input type']
    for tp in table_soup_tag.findAll("tr"): 
    	nouvelle_line = [] 
    	for cell in tp.findAll(["td", "th"]): 
    		nouvelle_line.append(cell.get_text().strip()) 
    	liste_key_value.append(nouvelle_line) 
    return liste_key_value


def write_csv_file(liste_to_write, file_name, sep, write_header):
    """ recoit une liste_to_write, liste de liste, dont le contenu doit être écrit dans un fichier csv nommé file_name dont le séparateur est sep
            et selon write_header ajout d'un entête de column
    """
    # join values with commas once more, removing newline characters
    if sep is None:
        sep = ";"
           
    data_line = [(li[2]).strip('\n') for li in liste_to_write]
    data_to_write = (sep.join(data_line)) 
#    print(f'data to write  {data_to_write}')
    # écrire dans le fichier en ajoutant 'append'
    with open(file_name, "a", encoding='utf-8') as file:
    # création de l'entête
        if write_header:
            col_header = [(li[1]).strip('\n') for li in liste_to_write]
            header_to_write = sep.join(col_header)  
            file.write(header_to_write) 
            file.write('\n') 
        file.write(data_to_write) 
        file.write('\n') 
    return


def scrap_url(url_to_scrap):
    # liste des champs à récupérer : id, col, valeur
    list_of_info=[
            ['url',"product_page_url",''],
            ['UPC',"universal_product_code [upc]",''],
            ["title","title",''],
            ["Price (incl. tax)","price_including_tax",''],
            ["Price (excl. tax)","price_excluding_tax",''],
            ["Availability In stock","number_available",''],
            ["product_description","product_description",''],
            ["category","category",''],
            ["review_rating","review_rating",''], 
            ["image_url","image_url",'']
            ]
# accéder et charger la page
    response = requests.get(url_to_scrap)
    # délai pour ne pas surcharger le site
    time.sleep(be_nice)
    # traiter si le site a bien retourner la page
    if response.ok:
    
        soup = bs(response.text,features="html.parser")
        title = soup.find(class_="col-sm-6 product_main").h1
        
        product_description = soup.find(id="content_inner").find_next('h2').find_next('p')
        star_rating = soup.find(class_="col-sm-6 product_main").find_next('p').find_next('p').find_next('p').attrs
        category_crumb = soup.find(class_="breadcrumb").find_all('li')
        category_book = []
        for cc in category_crumb[1:]:
            if cc.text != title.text:
                category_book.append(cc.text.strip())
        category = category_book[1:2][0]
        table_prod =  soup.find(class_="table table-striped")
    
        tableau_page = convert_line_table(table_prod)
        table_info = [[]]
    
        for info in tableau_page:
            if info[0] in ['UPC', 'Price (excl. tax)', 'Price (incl. tax)', 'Availability']:
                table_info.append([info[0],info[1]])
        img_file = soup.find(class_="item active").find('img')
        site_parts = url_to_scrap.split('/')
        img_parts = img_file["src"].split('/')
    
        img_sub_url = "/".join(img_parts[2:])
    
        img_url = "https://" + site_parts[2:3][0] + "/" +(img_sub_url)
    
        for line in list_of_info:
    # pour tester la nouvelle version 3.10 de python (à vérifier lors de l'execution si update python fait en local!)
            if sys.version_info[1] >= 10:
                match line[0]:
                    case 'url':
                        line[2] = url_to_scrap
                    case 'UPC':
                        line[2] = table_info[1][1]
                    case 'title':
                        line[2] = title.text
                    case 'Price (incl. tax)':
                        line[2] = table_info[2][1]
                    case 'Price (excl. tax)':
                        line[2] = table_info[3][1]
                    case 'Availability In stock':
                        line[2] = table_info[4][1]
                    case 'product_description':
                        line[2] = product_description.text
                    case 'category':
                        line[2] = category
                    case 'review_rating':
                        line[2] = list(star_rating.values())[0][1]
                    case 'image_url':
                        line[2] = img_url
            else:
                if line[0] == 'url':
                    line[2] = url_to_scrap
                elif line[0] == 'UPC':
                    line[2] = table_info[1][1]
                elif line[0] == 'title':
                    line[2] = title.text
                elif line[0] == 'Price (incl. tax)':
                    line[2] = table_info[2][1]
                elif line[0] == 'Price (excl. tax)':
                    line[2] = table_info[3][1]
                elif line[0] == 'Availability In stock':
                    line[2] = table_info[4][1]
                elif line[0] == 'product_description':
                    line[2] = product_description.text
                elif line[0] == 'category':
                    line[2] = category
                elif line[0] == 'review_rating':
                    line[2] = list(star_rating.values())[0][1]
                elif line[0] == 'image_url':
                    line[2] = img_url


    return list_of_info


# page en cours de scrap

start = time.time()
url= 'https://books.toscrape.com/catalogue/the-requiem-red_995/index.html'
       
write_csv_file(scrap_url(url), "books.csv", ";", True)
url= 'https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html'
write_csv_file(scrap_url(url), "books.csv", ";", False)
end = time.time()
print(f'Le temps d"execution a été de {end-start} sec.')