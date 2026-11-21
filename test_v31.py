import unittest,sys
sys.path.insert(0,'/mnt/data/4q_v31')
import server
from unittest.mock import patch
class TestCandles(unittest.TestCase):
 def test_valid(self):
  with patch.object(server,'get',return_value=([[1700000000000,'1','3','0.5','2','42']]*60,1700000000,False)):
   r=server.candles('SOL','1h');self.assertEqual(len(r['data']),60);self.assertEqual(r['data'][0]['close'],2)
 def test_bad_coin(self):
  with self.assertRaises(ValueError):server.candles('FAKE','1h')
 def test_bad_interval(self):
  with self.assertRaises(ValueError):server.candles('BTC','2h')
if __name__=='__main__':unittest.main()
