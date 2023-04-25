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
    """ 美股市值前10大(鉅亨網) #https://www.cnyes.com/usstock
        --Output :
        [{"Datetime":"11\/13","代碼":"AAPL","名稱":"蘋果","最新價":149.7,"漲跌":2.83,"漲跌%":1.9269,"成交(股)2":"9334.51萬","成交(股)":93345144.0,"市值(USD)2":"2.34兆","市值(USD)":2336420000000.0,"本益比":24.0251,"殖利率":0.612787,"預估目標值":175.304595,"預估券商家數":37,"Inputtime":"2022-11-13 10:47:00"}]

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

#鉅亨網美股資訊
@app.route('/get_USA_stock', methods = ['POST'])
def get_USA_stock():
    """ 爬取美股資訊 
        市值前10大-USMV10   10大明星股-USTOP10   半導體-USSEMI10   ADR中概股-CADR10   ADR台股-TADR10
        --Input :
            {"code":"USMV10"}

        --Output :
            {"Datetime":"04\/24","代碼":"AAPL","名稱":"蘋果","最新價":164.92,"漲跌":-0.1,"漲跌%":-0.0606,"成交(股)2":"665.47萬","成交(股)":6654677.0,"市值(USD)2":"2.61兆","市值(USD)":2610930000000.0,"本益比":28.037,"殖利率":0.557508,"預估目標值":171.410811,"預估券商家數":37,"Inputtime":"2023-04-24 22:28:32","PAGE_TYPE":"市值前10大"}
        ---
        tags:
            - 美股資訊
        
        parameters:
        - in: body
          name: body
          required: true
          schema:
              id: 美股資訊
              required:
                  - code
              properties:
                  code:
                      type: nvarchar
                      example: "USMV10"
                      description: 查找資訊
      
        responses:
            200:
                description: 成功

            500:
                description: 錯誤函數
    """
    code = request.get_json()
    DF = md.get__cnyes_inf(code['code'])
    code_dict = {'USMV10':'市值前10大','USTOP10':'10大明星股','USSEMI10':'半導體','CADR10':'ADR中概股', 'TADR10':'ADR台股'}
    DF['PAGE_TYPE'] = code_dict[code['code']]
    DF = DF.to_json(orient="records", force_ascii=False)
    return DF

@app.route('/get_USA_stock2', methods = ['POST'])
def get_USA_stock2():
    """ 爬取美股資訊 
        USFOCUS-焦點股  TOPETF-ETF龍頭  FIETF-ETF固定收益  PRODETF-ETF商品  USINDEX-美股指數  SBUP-美國公債殖利率
        --Input :
            {"code":"USFOCUS"}

        --Output :
            {"Datetime":"04\/24","代碼":"ARKK","名稱":"ARK 創新 ETF","最新價":37.3,"漲跌":-0.33,"漲跌%":-0.877,"Inputtime":"2023-04-24 22:31:11","PAGE_TYPE":"焦點股"}
        ---
        tags:
            - 美股資訊
        
        parameters:
        - name: body
          in: body
          required: true
          schema:
              id: 美股指標
              required:
                  - code
              properties:
                  code:
                      type: nvarchar
                      example: "USFOCUS"
                      description: 查找資訊       

        responses:
            200:
                description: 成功

            500:
                description: 錯誤函數 
    """
    code = request.get_json()
    DF = md.get__cnyes_inf2(code['code'])
    code_dict = {'USFOCUS':'焦點股','TOPETF':'ETF龍頭','FIETF':'ETF固定收益','PRODETF':'ETF商品', 'USINDEX':'美股指數','SBUP':'美國公債殖利率'}
    DF['PAGE_TYPE'] = code_dict[code['code']]
    DF = DF.to_json(orient="records", force_ascii=False)
    return DF

@app.route('/get_USA_dj30', methods = ['POST'])
def get_USA_dj30():
    """ 爬取美股道瓊30
        第0頁 1-10 第1頁 11-20 第2頁 21-30
        --Input :
            {"code":"USFOCUS"}

        --Output :
            {"Datetime":"04\/24","代碼":"AAPL","名稱":"蘋果","最新價":165.14,"漲跌":0.12,"漲跌%":0.0727,"成交(股)2":"474.32萬","成交(股)":4743250.0,"市值(USD)2":"2.61兆","市值(USD)":2610930000000.0,"本益比":28.037,"殖利率":0.557508,"預估目標值":171.410811,"預估券商家數":37,"Inputtime":"2023-04-24 22:07:37","PAGE_TYPE":"道瓊30"}

        ---
        tags:
            - 美股資訊

        parameters:
        - in: body
          name: body
          required: true
          schema:
              id: 道瓊30
              required:
                  - page
              properties:
                  page:
                      type: int
                      example: "0"
                      description: 查找資訊     

        responses:
            200:
                description: 成功

            500:
                description: 錯誤函數
    """
    page = request.get_json()
    DF = md.get__cnyes_dj(page['page'])
    DF['PAGE_TYPE'] = '道瓊30'
    DF = DF.to_json(orient="records", force_ascii=False)
    return DF


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
