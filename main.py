# Import all the required libraries.
import requests
import bs4
import random
import time
import pandas as pd


# Function to perform the scraping
def scrape(page_no):
    # headers and proxies to bypass the website scurity 
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    proxies_list = ["128.199.109.241:8080","113.53.230.195:3128","125.141.200.53:80","125.141.200.14:80","128.199.200.112:138","149.56.123.99:3128","128.199.200.112:80","125.141.200.39:80","134.213.29.202:4444"]
    proxies = {'https': random.choice(proxies_list)}
    time.sleep(0.5 * random.random())

    # url of the website
    url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}'.format(page_no)
    result = requests.get(url,headers=headers,proxies=proxies)

    # BeautifulSoup to parse the HTML
    soup = bs4.BeautifulSoup(result.content,'lxml')

    # Get all the search results.
    all_products = soup.findAll('div', attrs={'class':'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'})
    
    for product in all_products:
        # Name of the product
        product_name = product.find('span', attrs={'class':'a-size-medium a-color-base a-text-normal'}).text

        # Product URL
        product_url = product.find('a', attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})['href']

        # Rating
        product_rating = product.find('span', attrs={'class':'a-icon-alt'}).text

        # Total no. of users that have rated the product
        users_rated = product.find('span', attrs={'class':'a-size-base s-underline-text'}).text

        # Price of the product
        price = product.find('span', attrs={'class':'a-price-whole'}).text

        # Product Description
        product_description = product.find('div', attrs={'id':'productDescription'})

        # Product ASIN
        product_ASIN = product['data-asin']

        #{ Logic to extract maufacturer
        product_page = requests.get("https://www.amazon.in{}".format(product_url),headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"})
        prod_soup = bs4.BeautifulSoup(product_page.content,'lxml')
        product_manufacturer = ''

        # if Product Details is present in the page
        product_details = prod_soup.find("div", attrs={'id':'detailBullets_feature_div'})
        if product_details is not None:
            for d in product_details.findAll("span", attrs={'class':'a-text-bold'}):
                if('Manufacturer' in d.text):
                    name = d.find_next_sibling("span").text
                    if(len(name)>len(product_manufacturer)):
                        product_manufacturer = name

        # else if Technical Details table is present in the page
        elif product_details is None: 
            details_table = prod_soup.find("table", attrs={'id':'productDetails_techSpec_section_1'})
            if details_table is not None:
                for row in details_table.findAll("th", attrs={'class':'a-color-secondary a-size-base prodDetSectionEntry'}):
                    if('Manufacturer' in row.text):
                        name = row.find_next_sibling("td").text.strip()
                        if(len(name)>len(product_manufacturer)):
                            product_manufacturer = name
            else:
                product_manufacturer = 'NA'



        # Append all the details in the single product list
        single_product_list = []
        
        if product_name is not None:
            single_product_list.append(product_name)
        else:
            single_product_list.append('NA')

        single_product_list.append('https://www.amazon.in/'+product_url)

        if product_rating is not None:
            single_product_list.append(product_rating)
        else:
            single_product_list.append('NA')

        if users_rated is not None:
            single_product_list.append(int(users_rated.replace("(","").replace(")","").replace(',','')))
        else:
            single_product_list.append(0)

        if price is not None:
            single_product_list.append(int(price.replace(',','')))
        else:
            single_product_list.append(0)

        single_product_list.append(product_ASIN)

        if product_description is not None:
            single_product_list.append(product_description.text.strip().replace('\n',''))
        else:
            single_product_list.append('NA')

        if product_manufacturer is not None:
            single_product_list.append(product_manufacturer.strip().replace('\u200e',''))
        else:
            single_product_list.append('NA')

        return single_product_list

if __name__ == 'main':
    no_of_pages = 20 # Number of pages in the search result

    all_products_list = [] # List to store all the products

    for i in range(1, no_of_pages+1):
        all_products_list.append(scrape(i)) # Fill the all_product_list
    
    # Make a csv file from the collected data
    flatten = lambda l: [item for sublist in l for item in sublist]
    df = pd.DataFrame(flatten(all_products_list),columns=['Product Name','Product URL','Product Rating','Users Rated', 'Price', 'ASIN', 'Product Description', 'Product Manufacturer'])
    df.to_csv('amazon_products.csv', index=False, encoding='utf-8')
        
    