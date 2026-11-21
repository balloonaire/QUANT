"""Offline deterministic gateway tests; no internet required."""
import unittest,unittest.mock,server
class Tests(unittest.TestCase):
 def test_coin_ids(self):
  with unittest.mock.patch.object(server,'get',return_value=([{'id':'solana','symbol':'sol','current_price':10,'price_change_percentage_24h':2,'total_volume':100,'market_cap':1000}],123,False)):
   r=server.market();self.assertEqual(r['data'][0]['symbol'],'SOL');self.assertEqual(r['fetched_at'],'1970-01-01T00:02:03+00:00')
 def test_supply(self):
  obj={'peggedAssets':[{'symbol':'USDT','circulating':{'peggedUSD':200}},{'symbol':'USDC','circulating':{'peggedUSD':100}}]}
  with unittest.mock.patch.object(server,'get',return_value=(obj,123,False)):
   r=server.stablecoins();self.assertEqual(r['data']['total_stablecoin_supply_usd'],300);self.assertAlmostEqual(r['data']['usdt_share_of_stablecoins_pct'],66.6666667)
 def test_dxy_missing(self):self.assertIsNone(server.dxy()['data'])
 def test_bad_address(self):
  with self.assertRaises(ValueError):server.chain('btc','not-a-wallet')
  with self.assertRaises(ValueError):server.chain('eth','0x123')
  with self.assertRaises(ValueError):server.chain('sol','wrong')
 def test_btc(self):
  obj={'chain_stats':{'tx_count':5,'funded_txo_sum':2000,'spent_txo_sum':1000},'mempool_stats':{'tx_count':1}}
  with unittest.mock.patch.object(server,'get',return_value=(obj,123,False)):
   r=server.chain('btc','1BoatSLRHtKNngkdXEeobR76b53LETtpyT');self.assertEqual(r['data']['confirmed_balance_sats'],1000)
if __name__=='__main__':unittest.main()
