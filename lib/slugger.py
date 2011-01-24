from google.appengine.ext import db
import random

CHARS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

class SluggerShard(db.Model):
    """Shards for the counter"""
    count = db.IntegerProperty(required=True, default=0)

def base58_encode(number):
  """Encode a number in base58"""
  base58 = ''
  bc = len( CHARS )
  while number >= bc:
    div, mod = divmod( number, bc )
    base58 = CHARS[ mod ] + base58
    number = int( div )
  return CHARS[ number ] + base58
  
def get_slug():
    """Return a unique slug for every call"""
    namespace = random.choice( list(CHARS) )
    def txn():
        shard_name = 'shard_' + namespace
        shard = SluggerShard.get_by_key_name(shard_name)
        if shard is None:
            shard = SluggerShard(key_name=shard_name)
        shard.count += 1
        shard.put()
        return shard.count
    count = db.run_in_transaction(txn)
    return namespace + base58_encode( count )