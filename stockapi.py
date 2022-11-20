# coding=utf-8
import random
from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS

import module as md

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

app.config['SWAGGER'] = {
    "title": "股票爬蟲API",
    "description": "透過API來抓取股票資訊",
    "version": "1.0.0",
    "termsOfService": ""
}

CORS(app)
Swagger(app)

@app.route('/home')
def home():
    a = 'hello world!'
    return a

@app.route('/usa_top10') #美股市值前10大
def usa_top10():
    """美股市值前10大(鉅亨網) #https://www.cnyes.com/usstock
          --Output :
          [{"Datetime":"11\/13","代碼":"AAPL","名稱":"蘋果","最新價":149.7,"漲跌":2.83,"漲跌%":1.9269,"成交(股)2":"9334.51萬","成交(股)":93345144.0,
          "市值(USD)2":"2.34兆","市值(USD)":2336420000000.0,"本益比":24.0251,"殖利率":0.612787,"預估目標值":175.304595,
          "預估券商家數":37,"Inputtime":"2022-11-13 10:47:00"}]

          --Output Memo:
            Datetime:日期,
            代碼,
            名稱,
            最新價,
            漲跌,
            漲跌%,
            成交(股)2,
            成交(股),
            市值(USD)2,
            市值(USD),
            本益比,
            殖利率,
            預估目標值,
            預估券商家數,
            Inputtime:抓取時間        
         ---
         tags:
          - 美股資訊

         responses:
           200:
             description: 成功

           500:
             description: 錯誤函數

       """

    jdf = md.get_usa_top10()
    return jdf

@app.route('/usa_stock') #美股大型機構持股名單
def usa_stock():
    """美國大型機構持股名單(moneybar) #https://www.moneybar.com.tw/investbar/usstock
       備註:因為為現爬，需等待
          --Output :
          [{"Datetime":"2022-11-13","Name":"Amazon.com Inc","Code":"AMZN",
          "Source":"Bill Miller Portfolio,JPMORGAN CHASE＆CO投資組合,喬治索羅斯投資組合,巴菲特持股清單,花旗,高盛",
          "Counts":6,"InputTime":"2022-11-13 11:07:26"}]

          --Output Memo:
          Datetime:日期,
          Name:股票名稱,
          Code:股票代號,
          Source:持股機構名單,
          Counts:總持股機構數,
          InputTime:爬取時間        
         ---
         tags:
          - 美股資訊

         responses:
           200:
             description: 成功

           500:
             description: 錯誤函數

       """

    jdf = md.get_usa_stock()
    return jdf

@app.route('/stock_calendar') #近期台股行事曆
def stock_calendar():
    """近期台股行事曆(histock) #https://histock.tw/stock/stockskd.aspx?cid=2
          --Output :
          [{"code":"1526","name":"日馳","meet":"除權息","date":"11\/21","week_day":"一","Datetime":"2022-11-13 11:27:17"}]

          --Output Memo:
          code:股票代號,
          name:股票名稱,
          meet:會議性質,
          date:日期,
          week_day:星期幾,
          Datetime:爬取時間        
         ---
         tags:
          - 台股資訊

         responses:
           200:
             description: 成功

           500:
             description: 錯誤函數

       """

    jdf = md.get_tw_calendar()
    return jdf

@app.route('/concept_stock') #yahoo股市概念股
def concept_stock():
    """yahoo股市概念股 #https://tw.stock.yahoo.com/class
    備註:因為為現爬，需等待

          --Output :
          [{"Name":"百和","Code":"9938","Concept":"Nike供應鏈","Input_Time":"2022-11-19 22:25:26"}]

          --Output Memo:
          Name:股票名稱
          Code:股票代碼
          Concept:概念股
          Input_Time:寫入時間     
         ---
         tags:
          - 台股資訊

         responses:
           200:
             description: 成功

           500:
             description: 錯誤函數

       """

    jdf = md.get_concept_stock()
    return jdf

@app.route('/consortium_stock') #yahoo股市概念股
def consortium_stock():
    """yahoo股市集團股 #https://tw.stock.yahoo.com/class
    備註:因為為現爬，需等待

          --Output :
          [{"Name":"台泥","Code":"1101","Concept":"台泥","Input_Time":"2022-11-19 22:36:07"}]

          --Output Memo:
          Name:股票名稱
          Code:股票代碼
          Concept:集團股
          Input_Time:寫入時間     
         ---
         tags:
          - 台股資訊

         responses:
           200:
             description: 成功

           500:
             description: 錯誤函數

       """

    jdf = md.get_consortium_stock()
    return jdf

'''改成post不同市場''' #11/20
@app.route('/stock_infomation') #上市、上櫃、興櫃 股票代碼
def stock_infomation():
    """上市、上櫃、興櫃 股票代碼 #https://www.twse.com.tw/zh/page/products/stock-code2.html
    備註:因為為現爬，需等待

          --Output :
          [{"股票代碼":"5274","股票名稱":"信驊","市場別":"上櫃","產業別":"半導體業","上市日":"2013\/04\/30","國際證券辨識號碼(ISIN Code)":"TW0005274005","CFICode":"ESVUFR","爬取類型":"上櫃"}]

          --Output Memo:
          股票代碼
          股票名稱
          市場別
          產業別
          上市日
          國際證券辨識號碼(ISIN Code)
          CFICode
          爬取類型  
         ---
         tags:
          - 台股資訊

         responses:
           200:
             description: 成功

           500:
             description: 錯誤函數

       """

    jdf = md.get_stock_infomation()
    return jdf



if __name__ == "__main__":
    try:
        app.run(debug=True, threaded=True, port=7777)
    except:
        app.run(debug=True, threaded=True, port=7777)

    """
    Swagger 首頁
        http://127.0.0.1:7777/apidocs
    """
