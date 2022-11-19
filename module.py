import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
import pandas as pd
import numpy as np
import bs4

#美股前十大市值
def get_usa_top10():
    def vol_change(col):
        k = []
        for i in col:
            if i/1000000000000 >= 1:
                k.append(str(round(i/1000000000000,2)) + '兆')
            elif i/100000000 >= 1:
                k.append(str(round(i/100000000,2)) + '億')
            elif i/10000 >= 1:
                k.append(str(round(i/10000,2)) + '萬')
            else:
                k.append(i)
        return k

    def get_data(url):
        resp = requests.get(url)
        data = resp.json()
        i = data["data"]
        df = pd.json_normalize(i, 'items')
        return df

    def get_dataframe(DF):
        df = DF[['0','200009','6','11','56','800001','700005','700001','700002','700003','700004']]
        columns = ['資訊', '名稱', '最新價', '漲跌', '漲跌%', '成交(股)', '市值(USD)', '本益比', '殖利率', '預估目標值', '預估券商家數']
        df.columns = columns
        df[['country','代碼','type']] = df['資訊'].str.split(':',expand = True)
        df = df.drop(columns=['資訊','country','type'])

        df['市值(USD)'] = df['市值(USD)']*1000000
        tt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        df['Inputtime'] = tt
        dd = time.strftime("%m/%d", time.localtime())
        df['Datetime'] = dd
        df['成交(股)2'] = vol_change(df['成交(股)'])
        df['市值(USD)2'] = vol_change(df['市值(USD)'])
        df = df[['Datetime','代碼', '名稱', '最新價', '漲跌', '漲跌%', '成交(股)2', '成交(股)', '市值(USD)2', '市值(USD)', '本益比', '殖利率', '預估目標值', '預估券商家數','Inputtime']]
        # print(df)
        return df

    Url = 'https://ws.api.cnyes.com/ws/api/v2/universal/quote?type=USMV10&column=H&page=0&limit=10'
    data = get_data(Url)
    DF = get_dataframe(data)
    print(DF)

    df = DF.to_json(orient="records", force_ascii=False)
    print(df)
    return df

#美股大型機構持股名單
def get_usa_stock():
    def get_soup(url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content,'html.parser')
        return soup

    def get_dict(pages_list): 
        all_data={}
        for H in pages_list:
            name = H.text
            if '人氣100' in name:
                continue
            else:
                http = 'https://www.moneybar.com.tw'+H.get('href')
                print(name)
                soup = get_soup(http)
                result = soup.find_all('td', {'class':"text-align-left mobile-adjust-width mobile-adjust-align-left"})

                all_data[name]=[]
                for i in result:
                    t = i.text.strip()
                    all_data[name].append(t)
        all_data = distinct(all_data)
        return all_data

    def distinct(all_data):
        for i in all_data.keys():
            all_data[i] = np.unique(all_data[i]).tolist()
        return all_data

    def count_s(all_data):
        all_no_l=[]
        for i in all_data.keys():
            all_no_l += all_data[i]
        count = Counter(all_no_l)
        return count

    def df_dict(pages_list):
        codes = []
        names = []
        for H in pages_list:
            name = H.text
            if '人氣100' in name:
                continue
            else:
                http = 'https://www.moneybar.com.tw'+H.get('href')
                print(name)
                soup = get_soup(http)
                stock_code = soup.find_all('td', {'class':"text-align-left mobile-hide"})
                stock_name = soup.find_all('td', {'class':"text-align-left mobile-adjust-width mobile-adjust-align-left"})
                
                for i in stock_code:
                    t = i.text.strip()
                    codes.append(t)

                for j in stock_name:
                    t = j.text.strip()
                    names.append(t)

        df = pd.DataFrame(data = codes,columns=['代碼'])    
        df['名稱'] = names
        df_dict = df.set_index('代碼').T.to_dict('list')
        return df_dict

    def get_df(count, all_data, df_dict):
        df = pd.DataFrame.from_dict(count, orient='index').reset_index().rename(columns={'index':'Name',0:'Counts'})
        df = df[df['Counts']!=1].sort_values(by = 'Counts', ascending=False).reset_index(drop=True)
        Code = []
        for stock in df['Name']: 
            for key, value in df_dict.items():
                for j in value:
                    if stock in j:
                        Code.append(key)
        df['Code'] = Code
        df['Source'] = [[i for i in all_data.keys() if n in all_data[i]] for n in df['Name']]
        df['Source'] = [','.join(i) for i in df['Source']]
        tt = time.strftime("%Y-%m-%d", time.localtime())
        dd = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        df['Datetime'] = tt
        df['InputTime'] = dd
        df = df[['Datetime','Name','Code','Source','Counts','InputTime']]
        return df

    Url = 'https://www.moneybar.com.tw/investbar/usstock'
    print('Get {}'.format(Url))
    Soup = get_soup(Url)
    P_list = Soup.find_all('a', {'class':"d-block float-left h5 mb-3"})
    all_dict = get_dict(P_list)
    count_ = count_s(all_dict)
    DF_dict = df_dict(P_list)
    DF = get_df(count_, all_dict, DF_dict)

    df = DF.to_json(orient="records", force_ascii=False)
    print(df)
    return df

#台股股票資訊行事曆
def get_tw_calendar():
    def get_url(url):
        URL = requests.get(url)
        soup = bs4.BeautifulSoup(URL.text,'html.parser')
        return soup

    def get_cal(soup):  #爬取表格並整理成DF  
        table = soup.find('table','tb-stockskd')
        trs = table.find_all('tr')

        dates = list()
        for i in trs:
            dates.append([date.text for date in i.find_all('th')])

        stocks = list()
        for tr in trs:
            stocks.append([stock.text.replace('\xa0\xa0',' ') for stock in tr.find_all('li')])

        def fill_none(mylist):
            for i in mylist:
                if len(i) == 0:
                    i = i.append('無')
        fill_none(stocks)

        df = pd.DataFrame(data = dates,columns=['日期'])
        all_stocks = pd.DataFrame({'stock':stocks})
        "-----------------------------------------------"
        df['stock'] = all_stocks
        
        data = pd.DataFrame()
        dates = []
        stocks = []
        # df['stock'] = [','.join(i) for i in all_stocks['stock']]
        for i ,j in zip(df['日期'],df['stock']):
            for stock in j:
                dates.append(i)
                stocks.append(stock)
        data['dates'] = dates
        data['stocks'] = stocks
        
        data[['code','name','meet']] = data['stocks'].str.split(' ',expand = True)
        data[['date','week_day']] = data['dates'].str.split('星期',expand = True)
        tt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data['Datetime'] = tt
        data = data.drop(columns = ['stocks','dates'])
        data = data.dropna()
        data = data[['code','name','meet','date','week_day','Datetime']]
        return data

    url = 'https://histock.tw/stock/stockskd.aspx?cid=2' 
    Soup = get_url(url)
    DF = get_cal(Soup)

    df = DF.to_json(orient="records", force_ascii=False)
    print(df)
    return df

#台股概念股
def get_concept_stock():
    tt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    def get_url(url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content,'html.parser')
        return soup

    def get_data(soup):
        concept = soup.find('div',{'id':"CONCEPT_STOCK"})
        a_tag = concept.find_all('a')

        categories = []
        for i in a_tag:
            categories.append(i.text)
        
        stock = pd.DataFrame()

        for category in categories:
            url = f'https://tw.stock.yahoo.com/class-quote?category={category}&categoryLabel=概念股'
            if category == '互聯網+':
                url = f'https://tw.stock.yahoo.com/class-quote?category=互聯網%2B&categoryLabel=概念股'
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content,'html.parser')
            number = soup.find('p','Pb(0px) C(#6e7780) Fz(14px) Fz(14px)--mobile Fw(n)')
            nums = number.text.split(" ")
            print(nums[1])
            table = soup.find('div','Pos(r) Ov(h) ClassQuotesTable')
            names = table.find_all('div','Lh(20px) Fw(600) Fz(16px) Ell')
            name = []
            code = []
            for i in names:
                name.append(i.text)
            codes = table.find_all('div','D(f) Ai(c)')
            for i in codes:
                j = i.text.split(".")
                code.append(j[0])

            if int(nums[1]) > 30:
                print(category)
                url = f'https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;category={category};categoryLabel=概念股;categoryName={category};offset=30?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseVersionSwitch%2CuseNewQuoteTabColor&intl=tw&lang=zh-Hant-TW&partner=none&prid=7amdksphccick&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1393&returnMeta=true'
                resp = requests.get(url)
                data = resp.json()
                for i in data['data']['list']:
                    name.append(i['symbolName'])
                    code.append(i['systexId'])

            if int(nums[1]) > 60:
                print(category)
                url = f'https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;category={category};categoryLabel=概念股;categoryName={category};offset=60?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseVersionSwitch%2CuseNewQuoteTabColor&intl=tw&lang=zh-Hant-TW&partner=none&prid=7amdksphccick&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1393&returnMeta=true'
                resp = requests.get(url)
                data = resp.json()
                for i in data['data']['list']:
                    name.append(i['symbolName'])
                    code.append(i['systexId'])

            data = pd.DataFrame()
            data['Name'] = name
            data['Code'] = code
            data['Concept'] = category
            data['Input_Time'] = tt
            print(data)
            stock = stock.append(data)
        print(stock)
        return stock

    URL = 'https://tw.stock.yahoo.com/class'
    DATA = get_url(URL)
    DF = get_data(DATA)

    df = DF.to_json(orient="records", force_ascii=False)
    print(df)
    return df

#台股集團股
def get_consortium_stock():
    tt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    def get_url(url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content,'html.parser')
        return soup

    def get_data(soup):
        concept = soup.find('div',{'id':"CONSORTIUM_STOCK"})
        a_tag = concept.find_all('a')

        categories = []
        for i in a_tag:
            categories.append(i.text)

        stock = pd.DataFrame()

        for category in categories:
            url = f'https://tw.stock.yahoo.com/class-quote?category={category}&categoryLabel=集團股'
            resp = requests.get(url)
            soup = BeautifulSoup(resp.content,'html.parser')
            number = soup.find('p','Pb(0px) C(#6e7780) Fz(14px) Fz(14px)--mobile Fw(n)')
            nums = number.text.split(" ")
            print(nums[1])
            table = soup.find('div','Pos(r) Ov(h) ClassQuotesTable')
            names = table.find_all('div','Lh(20px) Fw(600) Fz(16px) Ell')
            name = []
            code = []
            for i in names:
                name.append(i.text)
            codes = table.find_all('div','D(f) Ai(c)')
            for i in codes:
                j = i.text.split(".")
                code.append(j[0])

            data = pd.DataFrame()
            data['Name'] = name
            data['Code'] = code
            data['Concept'] = category
            data['Input_Time'] = tt
            print(data)
            stock = stock.append(data)
        print(stock)
        return stock

    URL = 'https://tw.stock.yahoo.com/class'
    SOUP = get_url(URL)
    DF = get_data(SOUP)

    df = DF.to_json(orient="records", force_ascii=False)
    print(df)
    return df









