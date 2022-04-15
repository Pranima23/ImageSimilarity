import requests
import os
from bs4 import BeautifulSoup

BASE_URL = "https://a-z-animals.com"
PWD = os.path.join(os.getcwd(), "Image Classification")

def list_animals():
    with open(os.path.join(PWD, "animals", "name of the animals.txt")) as f:
        animals = [animal.strip() for animal in f.readlines()]
    return animals

def get_column_maps(soup, _class, name, info, k=1):
    c = soup.find_all("div", attrs={"class": _class})
    i = {}
    if len(c) > 0:
        for _ in range(k):
            for t, n, in zip(c[_].find_all("dt"), c[_].find_all("dd")):
                i[t.text.lower()] = n.text
    info[name] = i
    return c

def get_overview(soup, info, animal):
        """ Animal Classification and Location Information"""

        # Classification
        c, l = get_column_maps(soup, _class="col-lg-6",name="classification", info=info)

        # Conservation Status
        if cs := c.find("ul", attrs={"class": "list-unstyled"}):
            info["conservation-status"] = cs.text

        # Locations
        info["locations"] = [_.text for _ in l.find_all("li") if len(l) > 0]

        img = l.find("img")
        if img:
            img_url = img.get('src')
            r = requests.get(f"{BASE_URL}/{img_url}")
            with open(os.path.join(PWD, "AnimalData", "LocationImages", f"{img_url.split('/')[-1]}"), "wb") as f:
                f.write(r.content)

def get_facts(soup, info):
    """ Animals Facts and Physical Characteristics"""
    
    # Facts
    get_column_maps(soup, "col-md-6", "facts", info, k=2)
    
    # Physical Characteristics
    get_column_maps(soup, "col-lg-4", "physical characteristics", info)

def main():
    # List animals
    animals = list_animals()

    # Create folders
    ad = os.path.join(PWD, "AnimalData")
    if not os.path.exists(ad):
        os.mkdir(ad)
            
    adl = os.path.join(ad, "LocationImages")
    if not os.path.exists(adl):
        os.mkdir(adl)

    # Iterate over animals
    for animal in animals:
        info = {}
        res = requests.get(f"{BASE_URL}/animals/{animal}/")
        soup = BeautifulSoup(res.content, features="html.parser")

        # Check if the animals available
        if not soup.find("div", attrs={"class": "col-lg-6"}):
            print(f"{animal} [X] Not found")
            continue

        print(f"Scraping data: {animal}")
        # Classification
        get_overview(soup, info, animal)        

        # Facts
        get_facts(soup, info)
        
        # Save as a json file
        import json
        with open(os.path.join(ad, f"{animal}.json"), "w") as f:
            json.dump(info, f, indent=4)

if __name__ == "__main__":
    main()
