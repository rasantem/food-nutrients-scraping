import urllib2
import unicodecsv as csv
import lxml.html
import lxml
import random
import time
import pprint


class crawler:

    def __init__(self, baseUrl):

        self.baseUrl = baseUrl
        self.cUrl = 'openfoodfacts.org'
        self.country_code ='world'
        self.list_food_dict = []
        self.product_links = []

    def ini_load(self):
        html = self.downloadUrl(self.baseUrl, 3)
        n_pages = self.scrap_n_pages(html)

        print "---------------------------------------------------"
        print "     Open food Facts Scraping"
        print "   Web to scrap: ", self.baseUrl
        print "   Number of pages: ", n_pages
        print "---------------------------------------------------\n\n"

        print 'Options: '
        print "1: Scrap all world products (High computational cost)."
        print "2: Scrap products by country.\n\n"

        choice = int(input('Enter your choice (1 or 2):  '))
        # Scrap World
        if choice == 1:
            self.crawl(self.baseUrl)

        # Scrap Country
        elif choice == 2:
            country_dict = self.country_sel(html)
            choice2 = str(raw_input('Enter country code:  ').lower())
            while choice2 not in country_dict:
                choice2 = str(raw_input('Enter country code:  ').lower())

            self.country_code = choice2
            self.crawl(self.country_Url(choice2))

        else:
            print('Invalid choice')

    def crawl(self, url):

            html = self.downloadUrl(url, 3)
            n_pages = self.scrap_n_pages(html)

            print "\n\nScraping web:  " + url
            print "Number of pages: " + str(n_pages)

            self.product_links.extend(self.scrap_product_links(html))

            # Iterate pages
            if n_pages >= 2:
                for page in range(2, n_pages +1):
                    url_p = url + "/" + str(page)
                    html = self.downloadUrl(url_p, 3)
                    self.product_links.extend(self.scrap_product_links(html))

            # Scrap every link products
            for product_l in self.product_links:
                url_prod = url + product_l
                self.scrap_product(url_prod)

            # Save to csv
            self.write_csv(self.list_food_dict)

    # Download url - Return Html
    def downloadUrl(self, url, num_retries, user_agent = 'wswp'):

        headers = {'User-agent': user_agent}
        req = urllib2.Request(url, headers=headers)
        try:
            html = urllib2.urlopen(req).read()
        except urllib2.URLError as e:
            print 'Download error:', e.reason
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    # recursively retry 5xx HTTP errors
                    return self.downloadUrl(url, num_retries-1)
            html = None
        return html

    # Get max. number page
    def scrap_n_pages(self, html):
        tree = lxml.html.fromstring(html)
        pages = tree.cssselect(".pagination > li")  #list of all pages
        return int(pages[-2].text_content())

    # Return product links
    def scrap_product_links (self, html):
        tree = lxml.html.fromstring(html)
        products = tree.cssselect(".products > li > a")  # list of all page elems
        prod_links = [elem.get('href') for elem in products]

        return prod_links

    # Return product nutrients
    def scrap_product(self, url):

        html = self.downloadUrl(url, 3)
        tree = lxml.html.fromstring(html)

        p_elements = tree.cssselect('h1[property="food:name"]')
        name = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:energyPer100g"]')
        energy = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:fatPer100g"]')
        fat = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:saturatedFatPer100g"]')
        s_fat = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:carbohydratesPer100g"]')
        carbohydrate = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:sugarsPer100g"]')
        sugars = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:fiberPer100g"]')
        fiber = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:proteinsPer100g"]')
        proteins = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:saltPer100g"]')
        salt = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:sodiumEquivalentPer100g"]')
        sodium = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:alcoholPer100g"]')
        alcohol = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:zincPer100g"]')
        zinc = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:magnesiumPer100g"]')
        magnesium = self.assing(p_elements)

        p_elements = tree.cssselect('td[property="food:omega-3FatPer100g"]')
        omega3 = self.assing(p_elements)

        p_elements = tree.cssselect('tr#nutriment_nutriscore_tr > .nutriment_value')
        score = self.assing(p_elements)

        self.list_food_dict.append({"Name": name, "Energy": energy, "Fat": fat, "Saturated_fat": s_fat,
                                    "Carbohydrate": carbohydrate, "Sugars": sugars, "Fiber": fiber,"Proteins": proteins,
                                    "Salt": salt, "Sodium": sodium, "Alcohol": alcohol, "Zinc": zinc,
                                    "Magnesium": magnesium, "Omega3": omega3, "Score": score})

    # Assing attribute value
    def assing(self, elems):
        if not elems:
            value = "Na"
        else:
            value = elems[0].text_content()  # .get('content')
        return value

    # Returns country list
    def country_sel(self, html):
        tree = lxml.html.fromstring(html)
        countries = tree.cssselect(".left li select option")  # list of country elems

        country_values = {elem.get('value') : elem.text_content() for elem in countries}
        del country_values[None]
        pprint.pprint(country_values)
        return country_values

    # Returns formatted url
    def country_Url(self, c):
        country_url = 'https://' + c + '.' + self.cUrl
        return country_url

    # Delay time ** Not used ** No scraping restrictions
    def delay(self, seconds):
        elapse = seconds + seconds * random.random()
        time.sleep(elapse)

    # Write results to csv
    def write_csv(self, dict_list):

        csv_name = self.country_code + "_food_nutrients.csv"
        print "\nSaving data to file: " + csv_name
        with open(csv_name, 'wb') as f:
            fnames = ["Name", "Energy", "Fat", "Saturated_fat", "Carbohydrate", "Sugars", "Fiber", "Proteins",
                      "Salt", "Sodium", "Alcohol", "Zinc", "Magnesium", "Omega3", "Score"]
            writer = csv.DictWriter(f, delimiter=',', fieldnames=fnames, encoding='utf-8')
            writer.writeheader()
            writer.writerows(product for product in dict_list)