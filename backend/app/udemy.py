import traceback
import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse, parse_qs

def get_url_param(url, param_name):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Get the query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Return the value of the specified parameter
    return query_params.get(param_name, [None])[0]

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}


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


def get_udemy_content(url):

    page = requests.get(url.strip())
    soup = BS(page.content, 'html.parser')

    

    s = soup.find('div', class_='clp-lead__headline')
    t = soup.find('h1', class_='clp-lead__title')

    print(t)
    try:
        categ = soup.find('div', {'class': "topic-menu udlite-breadcrumb"})
        categ = categ.text.split("\n")

        categ = [i for i in categ if i != ""]


        lan = soup.find('div', {'class': "clp-lead__element-item clp-lead__locale"})

        lan = lan.text.replace("\n", "")

    except:
        print("exception")
        categ = ""
        lan = ""
    try:

        p = soup.find('meta', {"property":"udemy_com:price"})
        price = p["content"]

        aut = soup.find_all('div', {'data-purpose': "instructor-name-top"})
        description = soup.find('div', {'data-purpose': "course-description"})
        description_string = ""


        if(description):
            description = description.find('div', {'data-purpose': "safely-set-inner-html:description:description"})
            if(description):
                for i in description:
                    try:
                        description_string +="<p>" + i.text + "</p>"
                    except :
                        print(i)
                        traceback.print_exc()


        else:
            description = ""


        auth = aut[0].text[11:]
        auth = "COURSE AUTHOR -\n" + auth
        print(auth)

        #price = (price).split('price')[1]
        print(price)
        d = "100% off"
        '''if len(price) > 7 :
            price = (price).split('Original Price')

            pricel = (price[1]).split('Discount')
            price = pricel[0]
            d = pricel[1]
            print(pricel)

        else:
            d= "100% off"
            '''

    except :
        traceback.print_exc()
        print("Unexpected Error")
    try :
        dsc = soup.find('div', {'data-purpose': 'safely-set-inner-html:description:description'})
        dsc = []#dsc.find_all('p')
        ds = ''
        for i in dsc:
            ds += str(i) + '\n'
    except:
        traceback.print_exc()
        ds = ""
    try :
        w = soup.find_all('div', {'class': "course-landing-page__main-content"})
        if(w):
            wyl = w[3]
        wl = wyl.find_all('div', {'data-purpose' : "objective"})
        wls = ''
        for i, j in enumerate(wl):
            wls += str(i + 1) + ". " + j.text + '\n'
    except:
        traceback.print_exc()
        print(s)
        wls = ""
        print("-----------------------------No what will you learn found----------------------------")


    req = []
    image = soup.find_all('img')

    image_url = image[1]['src'].split("/")
    image_url[-2] = "750x422"
    image_url = "/".join(image_url)

    lp = soup.find_all('div', {'class': 'udlite-text-sm clp-lead'})
    try :
        inclu = soup.find('div', {'data-purpose':"curriculum-stats"}).text.split('lectures')[1][3:]

    except:
        inclu = ""
    if lp != []:

        e = lp[0].find('div', {'data-purpose': "enrollment"})
        r = lp[0].find('span', {'data-purpose': "rating-number"})
        b = lp[0].find('span', {'data-purpose': "badge"})
        b2 = lp[0].find('span', {'data-purpose': "badge-top-rated"})
        try:
            req = soup.find('div', {'class': 'ud-component--course-landing-page-udlite--requirements'})[
                'data-component-props']

            false = ''
            req = eval(req)
            req = req['prerequisites']
        except:
            req = ""
        if b:
            b = b.text[1:-1]
        elif b2:
            b = b2.text[1:-1]
        else:
            b = ''
        try:
            r = (r.text).split()
            rating = [r[1],r[-2][1:]]
        except :
            rating = [0,0]
    Url = url

    reqmn = ""
     
    for i, j in enumerate(req):
        reqmn += str(i + 1) + ". " + j + '\n'
    cdata = {"title" : (t.text) ,
             "headline" : (s.text),
             "Price": price ,
             "discount" : d,
             "author" : auth,
             "wywl": wls,
             "description" : description_string ,
             "requirement" : "",
             "badge" : "",
             "students" : "",
             "rating" : "",
             "included" : inclu,
             "image url" : image_url,
             "link" : Url,
             "category": categ,
             "language": lan,
             "coupon": get_url_param(Url, 'couponCode'),
             "image id" : "",

             }
    # for i in cdata :
    #     print(i,cdata[i])
    # img = Image.open(requests.get(image_url, stream=True).raw)
    # img.save('free udemy course coupon.jpg')

    return cdata

