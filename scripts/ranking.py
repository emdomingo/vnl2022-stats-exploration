
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests
import pandas as pd

s = HTMLSession()

division = ['men', 'women']

rankings = []

for div in division:
    url = f'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/standings/{div}/'

    r = s.get(url)
    r.html.render()

    phase = ['pool', 'final']
    
    for i in phase:
        
        if i == 'pool':
            table=r.html.find('div[data-tab="round-p"] table.basic', first=True)
        elif i == 'final':
            table=r.html.find('div[data-tab="round-f"]', first=True)
        
        rows = table.find('tr.vbw-o-table__row')
        rank = 1    
        for row in rows:
            data=[div.title()]
            data.append(i.title())
            data.append(rank)
            data.append(row.find('div.vbw-mu__team__name', first=True).text)
            if i == 'pool':
                data.append(int(row.find('td.matcheswon', first=True).text))
                data.append(int(row.find('td.matcheslost', first=True).text))
                data.append(int(row.find('td.matchpoints', first=True).text))
                data.append(float(row.find('td.setsratio', first=True).text))
                data.append(float(row.find('td.pointsratio', first=True).text))
            
            rankings.append(data)
            rank += 1
        
cols = ['division', 'phase', 'rank', 'team', 'won', 'lost', 'points', 'sets_ratio', 'points_ratio']
df = pd.DataFrame(rankings, columns=cols)
df.to_csv('./data/rankings.csv', index=False)
