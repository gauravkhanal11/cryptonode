from django.shortcuts import render
from django.http import JsonResponse
import requests
from datetime import datetime, timezone
import os

def epoch_date(epoch):
    return datetime.fromtimestamp(epoch, tz=timezone.utc)

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
    top_ten_ids= [coin.get('id') for coin in sliced] 
    #return JsonResponse(top_ten_ids,safe=False)

    each_coin = []
    api_endpoint_ind_coins = "https://api.coinpaprika.com/v1/tickers/{id}"
    for coin_id in top_ten_ids:
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
    'ath_market_cap_date': market_data_json.get('market_cap_ath_date')
    }
    #return JsonResponse(filtered_market_info,safe=False)

#================================================== NEWS BOARD =================================================
    try:
        news_api_key = "DAFF19F7BF06ED8BB5EA361A3EE4A4E0"
        news_api_endpoint = f"https://api.thenewsapi.net/crypto?apikey={news_api_key}"
        news_response = requests.get(url=news_api_endpoint)
    except:
        news_response = {}

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

    context = {
        'coins': card_detail,
        'market': filtered_market_info,
        'news_board': news_json_filtered
    }
    return render(request,'dashboard/coin_list.html',context)