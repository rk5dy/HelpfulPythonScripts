import requests
import os
import bs4

manga = 'Yuragi-Sou-No-Yuuna-San'
os.makedirs(manga, exist_ok=True)
for i in range(1, 42):
    res = requests.get('http://mangaseeonline.net/read-online/{0}-chapter-{1}.html'.format(manga, str(i)))
    res.raise_for_status()
    nostarchSoup = bs4.BeautifulSoup(res.text, 'html.parser')

    table = nostarchSoup.find('div', {"class" : "image-container"})
    pages = table.find_all('img')

    title = 'Chapter-{0}'.format(str(i))
    print(title, " downloading")
    os.makedirs('{0}/{1}'.format(manga, title), exist_ok=True)
    for i, url in enumerate(pages):

        page = open(os.path.join(manga, title, os.path.basename(url['src'])), 'wb')
        imgres = requests.get(url['src'])
        print('Downloading image...')
        res.raise_for_status()

        for chunk in res.iter_content(100000):
            page.write(chunk)
        page.close()
        print(url['src'])

print('done')
