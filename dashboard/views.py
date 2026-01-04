from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import requests
from .utilities import num_to_word
import os

market_endpoint="https://api.coinpaprika.com/v1/global"
data = requests.get(url=market_endpoint)
data_json = data.json()
crypto_market_cap = data_json.get('market_cap_usd')


def dashboard(request):

#======================================GETTING THE COIN DETAILS=================================================
    api_endpoint_rank = "https://api.coinpaprika.com/v1/coins"
    try:
        response = requests.get(url=api_endpoint_rank,timeout=30)
        data = response.json()
    except:
        data=[]
    filtered_data = [
    {
        "id": item.get('id'),
        "rank": item.get('rank')
    } 
    for item in data
    if item.get('rank') >=1 
    ]
    filtered_data.sort(key=lambda x: x['rank'])
    sliced = filtered_data[:20]
    top_ids= [coin.get('id') for coin in sliced] 
    #return JsonResponse(top_ten_ids,safe=False)

    each_coin = []
    api_endpoint_ind_coins = "https://api.coinpaprika.com/v1/tickers/{id}"
    for coin_id in top_ids:
        try:
            url = api_endpoint_ind_coins.format(id=coin_id)
            coin_details = requests.get(url=url)
            each_coin.append(coin_details.json())
        except:
            continue
    #return JsonResponse(each_coin,safe=False) 

    card_detail = [
    {
        "id": card.get('id'),
        "name": card.get('name'),
        "symbol": card.get('symbol'),
        "rank": card.get('rank'),
        "trading_price": card.get('quotes').get('USD').get('price'),
        "market_cap_amount": card.get('quotes',{}).get('USD',{}).get('market_cap',{}),
        "market_cap_percent": round((card.get('quotes',{}).get('USD',{}).get('market_cap',{}) / crypto_market_cap) * 100,2),
        "charts": {
            "fifteen_min": card.get('quotes',{}).get('USD',{}).get('percent_change_15m',0),
            "thirty_min": card.get('quotes',{}).get('USD',{}).get('percent_change_30m',0),
            "one_hour": card.get('quotes',{}).get('USD',{}).get('percent_change_1h',0),
            "six_hour": card.get('quotes',{}).get('USD',{}).get('percent_change_6h',0),
            "twelve_hour": card.get('quotes',{}).get('USD',{}).get('percent_change_12h',0),
            "twentyfour_hour": card.get('quotes',{}).get('USD',{}).get('percent_change_24h',0)
        }
    }
    for card in each_coin
    ]
    #return JsonResponse(card_detail,safe=False)

# ================================================= PIE CHART =======================================================
    pie_chart_raw_data= card_detail[:5]
    pie_chart = [
        {
            "name": data.get('name'),
            "market_cap_percent": data.get('market_cap_percent'),
            "market_cap_amount": data.get('market_cap_amount')
        }
    for data in pie_chart_raw_data
    ]
    pie_chart.append(
        {
            "name": "Others",
            "market_cap_percent": round(100 - sum(record['market_cap_percent'] for record in pie_chart),2),
            "market_cap_amount": crypto_market_cap - sum(record['market_cap_amount'] for record in pie_chart)
        }
    )
    #return JsonResponse(pie_chart,safe=False)

#===================================================MARKET CAP DETAILS==============================================

    try:
        market_data=requests.get(url=market_endpoint)
        market_data_json=market_data.json()
    except: 
        market_data_json={}

    filtered_market_info= {
    "today_market_cap":crypto_market_cap, 
    "today_market_cap_percent": (crypto_market_cap / market_data_json.get('market_cap_ath_value')) * 100, #Bar 1
    "today_movement": market_data_json.get('volume_24h_usd'),
    "last_updated": market_data_json.get('last_updated'),
    "ath_market_cap": market_data_json.get('market_cap_ath_value'), #Bar 2
    "ath_market_cap_date": market_data_json.get('market_cap_ath_date').split("T")[0],
    "today_market_cap_amount_word": num_to_word(crypto_market_cap),
    "ath_market_cap_amount_word": num_to_word(market_data_json.get('market_cap_ath_value')),
    "total_cryptos": market_data_json.get('cryptocurrencies_number'),
    "market_cap_change_24h": market_data_json.get('market_cap_change_24h')
    }
    #return JsonResponse(filtered_market_info,safe=False)

#================================================== NEWS BOARD =================================================
    try:
        news_api_endpoint = f"https://api.thenewsapi.net/crypto?apikey={settings.NEWS_API_KEY}"
        news_response = requests.get(url=news_api_endpoint)
    except:
        news_response={}


    news_json = news_response.json()
    articles = news_json.get("data",{}).get("results",{})

    news_json_filtered = [
    {
        "id": article.get('article_id',{}),
        "url": article.get('url',{}),
        "thumbnail_link": article.get('thumbnail',{}),
        "title": article.get('title',{}),
        "description": article.get('description',{}),
        "published_at": article.get('published_at',{})
    }
    for article in articles
    ]
    news_json_filtered.sort(key=lambda x: x['published_at'], reverse=True)
    #return JsonResponse(news_json_filtered,safe=False)
 
#================================================== FINAL PAGE RENDERING ======================================================
    context = {
        'coins': card_detail,
        'market': filtered_market_info,
        'pie_chart': pie_chart,
        'news_board': news_json_filtered
    }
    return render(request,'dashboard/coin_list.html',context)