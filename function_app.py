import azure.functions as func
import logging
from seleniumwire import webdriver
import json
#from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import requests
import pandas as pd

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:

    def weighted_average(df, values, weights):
        return sum(df[weights] * df[values]) / df[weights].sum()

    def halen_voor_cijfer(df, values, weights, doel, toetsgewicht):
        gewicht_plus_toetsgewicht   = df[weights].sum() + toetsgewicht
        doel_somgewicht             = gewicht_plus_toetsgewicht * doel
        afstand                     = doel_somgewicht - sum(df[weights] * df[values])
        return afstand / toetsgewicht


    logging.info('Python HTTP trigger function processed a request. 11:38')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')


    s = Service(r"/tmp/chromedriver/chromedriver-linux64/chromedriver")


    #try to use the chrome driver
    #
    try:
        #driver = webdriver.Chrome("/usr/local/bin/chromedriver")     
        
        driver = webdriver.Chrome(service=s, options=chrome_options)
        website = "https://rythovius.magister.net"
        driver.implicitly_wait(20)
        driver.get(website)

        inlog = WebDriverWait(driver,40).until(EC.presence_of_element_located((By.XPATH,"//*[@id='username']")))
        inlog.send_keys('simon.vanlaarhoven@rythovius.nl')

        btn = WebDriverWait(driver,40).until(EC.presence_of_element_located((By.XPATH, "//*[@id='username_submit']")))
        btn.click()

        inlog = WebDriverWait(driver,40).until(EC.presence_of_element_located((By.XPATH,"//*[@name='passwd']")))
        inlog.send_keys('5521HH017!!')
        btn = WebDriverWait(driver,40).until(EC.presence_of_element_located((By.XPATH, "//*[@type='submit']")))
        btn.click()
        btn = WebDriverWait(driver,40).until(EC.presence_of_element_located((By.XPATH, "//*[@id='idBtn_Back']")))
        btn.click()
        time.sleep(5)
        for r in driver.requests:
            if 'Authorization' in r.headers:
                print(r.headers['Authorization'])
                au = r.headers['Authorization']
                break

        r=requests.get("https://rythovius.magister.net/api/personen/11279/cijfers/laatste?top=200&skip=0", headers={"Authorization":au})
        result = r.content
        driver.quit()    
        r = json.loads(result)
        df = pd.DataFrame(r['items'])
        df = df[df['waarde'] != 'rood']
        df['vak_Id'] =  df['vak'].apply(lambda x: x['code'])
        df['vak_omschrijving'] =  df['vak'].apply(lambda x: x['omschrijving'])
        df['cijfer'] = df['waarde'].apply(lambda x: float(x.replace(',', '.')))
        gewogen_gemiddelde = df.groupby(['vak_omschrijving', 'vak_Id']).apply(weighted_average, 'cijfer', 'weegfactor')
        halen_voor_df = df.groupby(['vak_omschrijving', 'vak_Id']).apply(halen_voor_cijfer, 'cijfer', 'weegfactor', 5.5, 2).reset_index(name='cijfer')
        sorted_df           = halen_voor_df.sort_values(by=['cijfer'], ascending=False)
        json_records = sorted_df.to_json(orient ='records')


    except Exception as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )
        
    response = func.HttpResponse(
        json_records,
        status_code=200
    )

    # Set CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response
    #return func.HttpResponse(
    #         json_records,
    #         status_code=200
    #)
