#!/usr/bin/env python3
"""楽天市場商品検索(2026年新API・ichibams)。①リサーチAIが実データで商品を選定するための補助スクリプト。
使い方: python3 scripts/rakuten_search.py "キーワード" [--min-reviews 100] [--min-rating 4.3] [--max-price 15000] [--hits 10]
.env(RAKUTEN_APPLICATION_ID / RAKUTEN_ACCESS_KEY / RAKUTEN_AFFILIATE_ID)を読み込んで使用する。
"""
import argparse
import os
import sys
import urllib.parse
import urllib.request
import json

def load_env(path=".env"):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def search(keyword, min_reviews=100, min_rating=4.3, max_price=None, min_price=None, hits=10, referer="https://github.com/ikeda5505-ops/rakutenroom"):
    env = load_env()
    app_id = env.get("RAKUTEN_APPLICATION_ID") or os.environ.get("RAKUTEN_APPLICATION_ID")
    access_key = env.get("RAKUTEN_ACCESS_KEY") or os.environ.get("RAKUTEN_ACCESS_KEY")
    affiliate_id = env.get("RAKUTEN_AFFILIATE_ID") or os.environ.get("RAKUTEN_AFFILIATE_ID")
    if not app_id or not access_key:
        print("エラー: .envにRAKUTEN_APPLICATION_ID / RAKUTEN_ACCESS_KEYが必要です", file=sys.stderr)
        sys.exit(1)

    params = {
        "applicationId": app_id,
        "accessKey": access_key,
        "keyword": keyword,
        "hits": min(hits * 3, 30),  # 絞り込みで減る分、多めに取得
        "sort": "-reviewCount",
        "formatVersion": 2,
    }
    if affiliate_id:
        params["affiliateId"] = affiliate_id

    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Referer": referer})
    with urllib.request.urlopen(req) as res:
        data = json.load(res)

    results = []
    for item in data.get("Items", []):
        review_count = item.get("reviewCount", 0) or 0
        review_avg = item.get("reviewAverage", 0) or 0
        price = item.get("itemPrice", 0) or 0
        if review_count < min_reviews or review_avg < min_rating:
            continue
        if max_price and price > max_price:
            continue
        if min_price and price < min_price:
            continue
        results.append({
            "name": item.get("itemName", "")[:60],
            "price": price,
            "reviewCount": review_count,
            "reviewAverage": review_avg,
            "shop": item.get("shopName", ""),
            "url": item.get("itemUrl", ""),
        })
        if len(results) >= hits:
            break
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword")
    parser.add_argument("--min-reviews", type=int, default=100)
    parser.add_argument("--min-rating", type=float, default=4.3)
    parser.add_argument("--max-price", type=int, default=None)
    parser.add_argument("--min-price", type=int, default=None)
    parser.add_argument("--hits", type=int, default=10)
    args = parser.parse_args()

    results = search(args.keyword, args.min_reviews, args.min_rating, args.max_price, args.min_price, args.hits)
    if not results:
        print(f"条件(レビュー{args.min_reviews}件以上・評価{args.min_rating}以上)を満たす商品が見つかりませんでした。")
    for r in results:
        print(f"[{r['reviewCount']}件/★{r['reviewAverage']}] {r['price']}円 {r['name']} ({r['shop']})")
        print(f"  {r['url']}")
