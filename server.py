#!/usr/bin/env python3
"""4Q research-only optional public-data gateway. Python 3.10+, standard library."""
import json, os, time, threading, urllib.request, urllib.parse, http.server, socketserver, re, csv, io, datetime
PORT=int(os.getenv('PORT','8787'))
CACHE={}; LOCK=threading.Lock()
UA={'User-Agent':'4Q-Research-Lab/3.1 (public market research; no execution)','Accept':'application/json'}

def get(url, ttl=90):
    now=time.time()
    with LOCK:
        cached=CACHE.get(url)
        if cached and now-cached[0]<ttl: return cached[1],cached[0],False
    try:
        req=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(req,timeout=12) as resp:
            if resp.status!=200: raise ValueError('upstream status '+str(resp.status))
            body=resp.read(3_000_000)
        obj=json.loads(body)
        with LOCK: CACHE[url]=(now,obj)
        return obj,now,False
    except Exception:
        if cached: return cached[1],cached[0],True
        raise

def result(data, timestamp, stale=False, source=None, caveat=None):
    return {'data':data,'fetched_at':datetime.datetime.fromtimestamp(timestamp,datetime.timezone.utc).isoformat(),'stale':stale,'source':source,'caveat':caveat}

def market():
    ids='bitcoin,ethereum,solana,arbitrum,aster,avalanche-2,polkadot,injective-protocol,celestia,arkham,filecoin'
    url='https://api.coingecko.com/api/v3/coins/markets?'+urllib.parse.urlencode({'vs_currency':'usd','ids':ids,'price_change_percentage':'24h','per_page':20,'page':1})
    o,t,s=get(url,90)
    return result([{'id':x.get('id'),'symbol':x.get('symbol','').upper(),'price':x.get('current_price'),'change_24h':x.get('price_change_percentage_24h'),'volume_24h':x.get('total_volume'),'market_cap':x.get('market_cap')} for x in o],t,s,'CoinGecko public API','CoinGecko rate limits and token mappings may vary; quotes are snapshots')

def stablecoins():
    o,t,s=get('https://stablecoins.llama.fi/stablecoins?includePrices=true',300)
    rows=o.get('peggedAssets',[])
    def circ(x):
        v=x.get('circulating',{}).get('peggedUSD',0)
        return v if isinstance(v,(float,int)) else 0
    total=sum(circ(x) for x in rows)
    usdt=next((x for x in rows if x.get('symbol')=='USDT'),{})
    return result({'total_stablecoin_supply_usd':total,'usdt_supply_usd':circ(usdt),'usdt_share_of_stablecoins_pct':(circ(usdt)/total*100 if total else None),'asset_count':len(rows)},t,s,'DefiLlama stablecoins','USDT share of stablecoins is NOT USDT dominance of total crypto capitalization; supply is not exchange inflow')

def globalcap():
    o,t,s=get('https://api.coingecko.com/api/v3/global',300)
    d=o.get('data',{})
    return result({'total_crypto_market_cap_usd':d.get('total_market_cap',{}).get('usd'),'btc_dominance_pct':d.get('market_cap_percentage',{}).get('btc'),'eth_dominance_pct':d.get('market_cap_percentage',{}).get('eth')},t,s,'CoinGecko global API','Dominance metrics use provider estimates')

def dxy():
    # Stooq may not offer a reliable DXY quote. Fail visibly rather than substituting a USD proxy.
    return result(None,time.time(),False,'Not configured','DXY requires a licensed or verified feed. No DXY value is fabricated.')

def candles(coin, interval):
    """Public Binance OHLCV snapshots. May be unavailable by geography or symbol."""
    allowed={'BTC','ETH','SOL','ARB','ASTER','AVAX','DOT','INJ','TIA','ARKM','FIL'}
    frames={'1m','5m','15m','1h','4h','1d','1w'}
    if coin not in allowed or interval not in frames: raise ValueError('Unsupported coin or interval')
    url='https://data-api.binance.vision/api/v3/klines?'+urllib.parse.urlencode({'symbol':coin+'USDT','interval':interval,'limit':300})
    raw,t,stale=get(url,30)
    if not isinstance(raw,list): raise ValueError('Invalid exchange candle response')
    data=[]
    for row in raw:
        if not isinstance(row,list) or len(row)<6: continue
        item={'time':int(row[0])//1000,'open':float(row[1]),'high':float(row[2]),'low':float(row[3]),'close':float(row[4]),'volume':float(row[5])}
        if item['close']<=0 or item['high']<item['low']: continue
        data.append(item)
    if not data: raise ValueError('No supported exchange candles for '+coin)
    return result(data,t,stale,'Binance public market-data endpoint','Up to 300 candles; latest bar may be incomplete; availability and CORS vary; not a tradeable quote')

def chain(chain,address):
    if chain=='btc':
        if not re.fullmatch(r'(bc1[a-z0-9]{11,87}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})',address): raise ValueError('Invalid BTC address format')
        o,t,s=get('https://mempool.space/api/address/'+urllib.parse.quote(address),45)
        chainstats=o.get('chain_stats',{}); mem=o.get('mempool_stats',{})
        return result({'address':address,'chain':'BTC','confirmed_tx_count':chainstats.get('tx_count'),'mempool_tx_count':mem.get('tx_count'),'funded_sats':chainstats.get('funded_txo_sum'),'spent_sats':chainstats.get('spent_txo_sum'),'confirmed_balance_sats':chainstats.get('funded_txo_sum',0)-chainstats.get('spent_txo_sum',0)},t,s,'mempool.space public API','Address-level stats only; not proof of exchange or whale ownership')
    if chain=='eth':
        if not re.fullmatch(r'0x[a-fA-F0-9]{40}',address): raise ValueError('Invalid ETH address format')
        key=os.getenv('ETHERSCAN_API_KEY','')
        if not key: raise ValueError('ETHERSCAN_API_KEY not configured')
        url='https://api.etherscan.io/v2/api?'+urllib.parse.urlencode({'chainid':'1','module':'account','action':'balance','address':address,'tag':'latest','apikey':key})
        o,t,s=get(url,90)
        if o.get('status')!='1': raise ValueError('Etherscan returned no valid balance')
        return result({'address':address,'chain':'ETH','balance_eth':int(o['result'])/1e18},t,s,'Etherscan API V2','ETH native balance only, excludes ERC-20 and other networks')
    if chain=='sol':
        if not re.fullmatch(r'[1-9A-HJ-NP-Za-km-z]{32,44}',address): raise ValueError('Invalid Solana address format')
        rpc=os.getenv('SOLANA_RPC_URL','https://api.mainnet-beta.solana.com')
        # No user-provided URLs: RPC is controlled only by server environment.
        payload=json.dumps({'jsonrpc':'2.0','id':1,'method':'getBalance','params':[address,{'commitment':'confirmed'}]}).encode()
        req=urllib.request.Request(rpc,data=payload,headers={'Content-Type':'application/json',**UA})
        with urllib.request.urlopen(req,timeout=12) as response: o=json.load(response)
        if 'error' in o: raise ValueError('Solana RPC rejected query')
        return result({'address':address,'chain':'SOL','balance_sol':o['result']['value']/1e9,'slot':o['result']['context']['slot']},time.time(),False,'Solana JSON-RPC','Native SOL only, no SPL token balance; public RPC may throttle')
    raise ValueError('Unsupported chain')

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass
    def send(self,code,body):
        data=json.dumps(body,allow_nan=False).encode()
        self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Access-Control-Allow-Origin',os.getenv('ALLOWED_ORIGIN','http://localhost:8000')); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers();self.wfile.write(data)
    def do_GET(self):
        p=urllib.parse.urlsplit(self.path); q=urllib.parse.parse_qs(p.query)
        try:
            routes={'/api/market':market,'/api/stablecoins':stablecoins,'/api/global':globalcap,'/api/dxy':dxy}
            if p.path=='/api/health': out={'status':'ok','utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
            elif p.path in routes: out=routes[p.path]()
            elif p.path=='/api/candles': out=candles(q.get('coin',[''])[0].upper(),q.get('interval',[''])[0])
            elif p.path=='/api/wallet': out=chain(q.get('chain',[''])[0].lower(),q.get('address',[''])[0].strip())
            else: return self.send(404,{'error':'Unknown endpoint'})
            self.send(200,out)
        except Exception as exc:
            self.send(502,{'error':str(exc)[:200],'data':None,'fetched_at':None,'stale':True})

if __name__=='__main__':
    with socketserver.ThreadingTCPServer(('127.0.0.1',PORT),Handler) as httpd:
        print('4Q research gateway listening on http://127.0.0.1:'+str(PORT),flush=True)
        httpd.serve_forever()
