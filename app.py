from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get('https://news.mifx.com/kurs-valuta-asing?kurs=JPY')
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('table', class_='centerText newsTable2') 
    tr = table.find_all('tr') 

    temp = [] #initiating a tuple

    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
        #use the key to take information here
        #name_of_object = row.find_all(...)[0].text
        date = row.find_all('td')[0].text
        date = date.strip().replace(u'\xa0',' ')
    
        ask = row.find_all('td')[1].text
        ask = ask.strip()

        bid = row.find_all('td')[2].text
        bid = bid.strip()


        temp.append((date,ask,bid)) #append the needed information 
    
    temp = temp[::-1] #remove the header

    df = pd.DataFrame(temp, columns = ('date','ask','bid')) #creating the dataframe
   #data wranggling -  try to change the data type to right data type
    df['date'] = pd.to_datetime(df['date'])
    df['ask'] = df['ask'].str.replace(',','.').astype('float64')
    df['bid'] = df['bid'].str.replace(',','.').astype('float64')
    df = df.set_index('date').sort_index(ascending=False)
   #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('https://news.mifx.com/kurs-valuta-asing?kurs=JPY') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run(debug=True, port=5000)
