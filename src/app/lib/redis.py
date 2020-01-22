import redis as _redis

pool = _redis.ConnectionPool(host="redis", port=6379)
redis = _redis.StrictRedis(connection_pool=pool)
