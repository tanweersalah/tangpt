import requests
from bs4 import BeautifulSoup as BS




def deep(a):
    #a = a.split('?')[0]
    x = a.replace('/', '%2F')
    x = x.replace(':', '%3A')
    x = x.replace('?', '%3F')
    x = x.replace('=', '%3D')
    y = "https://click.linksynergy.com/deeplink?id=KLBDeI3Y*Vs&mid=39197&murl=" + x
    return y


def coupon(url):
    URL = 'https://www.discudemy.com/go/' + url
    page = requests.get(URL.strip())
    soup = BS(page.content, 'html.parser')
    el = soup.find('div', class_="ui segment")
    el2 = el.find('a')
    l = el2['href']
    print('Coupon : ' + l.split('=')[-1])
    return ([l,l.split('=')[-1]])


def links(URL,coupon_count = 1):
    coupon_list = []

    page = requests.get(URL.strip())
    soup = BS(page.content, 'html.parser')
    el = soup.find('article', class_="ui")
    el2 = el.find_all('div', class_='content')
    el3 = el2[0].find('span', style="text-decoration: line-through;color: rgb(33, 186, 69);")
    for i in el2:
        if i.find('span', style="text-decoration: line-through;color: rgb(33, 186, 69);"):

            elem = i.find('a', class_="card-header")
            title = elem.text
            print (str(len(coupon_list)+1)+'. '+title )
            l = elem['href']

            c = coupon(l.split('/')[-1])
            ml = c[0]

            print(c)

            coupon_list.append({
                "title": title,
                "link" : deep(ml),
                "coupon": c[1],
                "mainlink" : ml
            })
        if len(coupon_list)== coupon_count :
            return coupon_list 
    return coupon_list

def search_udemy_coupons(coupon_count= 1):
    ll = 'https://www.discudemy.com/all/'
    con = 'y'
    p = 1
    clist = links(ll + str(p), coupon_count=coupon_count)
    return clist




