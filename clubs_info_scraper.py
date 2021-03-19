import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup as BS
import urllib.request
import ssl

# ignore certificate errors
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

### READ DATA from WEB

## data info:
# style: ["year", "matchs played", "wins"]
# interval: 1959-2019

## read bjk club data

# url of the webpage
url = "https://tr.wikipedia.org/wiki/Be%C5%9Fikta%C5%9F_(futbol_tak%C4%B1m%C4%B1)_sezonlar%C4%B1_listesi"

uh = urllib.request.urlopen(url, context=ctx)
html = uh.read()
soup = BS(html, "html.parser")

# find seasons table (3rd table in page)
table = soup.find_all("table")[2]

# extract seasons data
bjk = []
for row in table.find_all("tr")[3:]:
    row_data = []
    # Year
    th = row.find_all("th")[0]
    row_data.append(th.find_all("a")[0].text[:4])
    # matchs played
    tds = row.find_all("td")
    row_data.append(tds[1].text)
    # wins
    row_data.append(tds[2].text)
    
    bjk.append(row_data)

### read gs club data

# url of the webpage
url = "https://en.wikipedia.org/wiki/List_of_Galatasaray_S.K._seasons"

uh = urllib.request.urlopen(url, context=ctx)
html = uh.read()
soup = BS(html, "html.parser")

# find seasons table
table = soup.find_all("table")[2]

# extract seasons data
gs = []
start = False
for row in table.find_all("tr"):
    if not start:
        try:
            year = row.find_all("th")[0].find_all("a")[0].text[:4]
            if year == "1958":
                start = True
            continue
        except:
            continue
            
    row_data = []
    try:
        # Year
        th = row.find_all("th")[0].find_all("a")[0].text[:4]
        row_data.append(th)
        # matchs played
        tds = row.find_all("td")
        row_data.append(tds[2].text)
        # wins
        row_data.append(tds[3].text)

        gs.append(row_data)
    except:
        continue

### read fb club data

# url of the webpage
url = "https://tr.wikipedia.org/wiki/Fenerbah%C3%A7e_(futbol_tak%C4%B1m%C4%B1)_sezonlar%C4%B1_listesi"

uh = urllib.request.urlopen(url, context=ctx)
html = uh.read()
soup = BS(html, "html.parser")

# tables
tables = soup.find_all("table")[:7]

fb = []
for table in tables:
    rows = table.find_all("tr")[1:]
    for row in rows:
        row_data = []
        # year
        row_data.append(row.find_all("a")[0].text[:4])
        # played
        tds = row.find_all("td")
        row_data.append(tds[2].text)
        # wins
        row_data.append(tds[3].text)
        
        fb.append(row_data)
fb = fb[1:]

### PUT THEM TO DFS

bjk_df = pd.DataFrame(bjk, columns=["Year", "Games", "Wins"])
gs_df = pd.DataFrame(gs, columns=["Year", "Games", "Wins"])
fb_df = pd.DataFrame(fb, columns=["Year", "Games", "Wins"])

### clean dfs

## bjk
# cleans newlines and gets rid of some unnecessary "+" signs
bjk_df["Games"] = (bjk_df["Games"]
                   .apply(lambda x: int(x.strip().split("/")[0].split("+")[0])))
bjk_df["Wins"] = (bjk_df["Wins"]
                   .apply(lambda x: int(x.strip().split("/")[0].split("+")[0])))

## gs
# cleans newlines
gs_df["Games"] = (gs_df["Games"]
                   .apply(lambda x: int(x.strip())))
gs_df["Wins"] = (gs_df["Wins"]
                   .apply(lambda x: int(x.strip())))

## fb
# cleans newlines
fb_df["Games"] = (fb_df["Games"]
                   .apply(lambda x: int(x.strip())))
fb_df["Wins"] = (fb_df["Wins"]
                   .apply(lambda x: int(x.strip())))

### add win % columns

bjk_df["Win %"] = bjk_df["Wins"] / bjk_df["Games"] * 100
gs_df["Win %"] = gs_df["Wins"] / gs_df["Games"] * 100
fb_df["Win %"] = fb_df["Wins"] / fb_df["Games"] * 100


### LİNE PLOT of DataFrames

fig, ax = plt.subplots()

plt.title("Win % of 3 Big Turkish Soccer Teams")
plt.xlabel("Year")
plt.ylabel("Win %")

ax.plot(bjk_df["Year"][:-1], np.convolve(bjk_df["Win %"], np.ones(3)/3)[1:-2], color="gray", label="BJK", alpha=0.8)
ax.plot(gs_df["Year"][:-1], np.convolve(gs_df["Win %"], np.ones(3)/3)[1:-2], color="red", label="GS", alpha=0.7)
ax.plot(fb_df["Year"][:-1], np.convolve(fb_df["Win %"], np.ones(3)/3)[1:-2], color="darkblue", label="FB", alpha=0.7)

ax.set_xticks(bjk_df["Year"].values[::6])

plt.legend()
plt.show()