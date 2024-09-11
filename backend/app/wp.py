import base64
import traceback

import requests
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.compat import xmlrpc_client
import datetime
from PIL import Image


from dotenv import load_dotenv
import os

load_dotenv()
def connect():

    wp_url_courses = os.getenv('GG_URL')
    wp_username2 = os.getenv('GG_USER')
    wp_ps2 = os.getenv('GG_PASS')
    wp_c = Client(wp_url_courses, wp_username2, wp_ps2)
    return wp_c







def create_udemy_page(content, imgid, ai_content, youtube_video):
    wp_c = connect()
    # conten_title = ''
    # for item in content['title']:
    #     conten_title = conten_title + item

    title = content["title"]

    price = str(content['Price']) + ' Discount 100% off'
    coupon =content["coupon"]

    wywl = content['wywl']
    url = content['link']
    image = imgid
    author = content['author']
    short = content["headline"]

    post = WordPressPost()
    post.title = title
    post.content = ai_content

    category = ['freecoupons', 'Free courses', 'Udemy Courses free']
    post.terms_names = {
        'category': category

    }
    post.post_type = "udemy_free_course"
    post.thumbnail = image
    post.custom_fields = []
    
    

    post.custom_fields.append({
        'key': 'link',
        'value': url
    })
    post.custom_fields.append({
        'key': 'seo_update_date',
        'value': str(datetime.datetime.now())
    })

    post.custom_fields.append({
        'key': 'udemy_link',
        'value': content['link']
    })

    try:
        yt_video = youtube_video[0]['url']
    except : 
        yt_video = ""
    post.custom_fields.append({
        'key': 'youtube_link',
        'value': yt_video
    })
    
    post.custom_fields.append({
        'key': 'coupon_code',
        'value': coupon
    })
    post.custom_fields.append({
        'key': 'what_you_ll_learn',
        'value': wywl
    })
    post.custom_fields.append({
        'key': 'price',
        'value': price
    })
    post.custom_fields.append({
        'key': 'course-author',
        'value': author
    })

    post.excerpt = content["headline"]

    post.post_status = 'publish'
    x = wp_c.call(posts.NewPost(post))
    y = wp_c.call(posts.GetPost(x))
    print(y.link)
    print("New Post Published")
    return {"Post Link" : y.link, "Status" : "published"}


def upload_new_image( link , title):

    img = Image.open(requests.get(link, stream=True).raw)
    img.save('free udemy course coupon.jpg')

    path = "free udemy course coupon.jpg"

    # API endpoint to create a new media (image) entry
    media_endpoint = "https://geeksgod.com/wp-json/wp/v2/media"


    # Prepare the image data
    files = {'file': open(path, 'rb')}

    # Create the new media entry
    user = os.getenv('GG_USER')
    passw = os.getenv('GG_PASS')
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{user}:{passw}'.encode()).decode()}",
    }
    data = {
        "alt_text": title,
        "title": title
    }
    response = requests.post(media_endpoint, data=data, files=files, headers=headers)

    if response.status_code == 201:
        response_data = response.json()
        print("New image uploaded successfully.")
    else:
        print("Error uploading image:", response.text)
        


    return response_data["id"]





