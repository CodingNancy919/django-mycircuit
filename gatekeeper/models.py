from utils.redis_helper import RedisClient


class GateKeeper:

    @classmethod
    def get(cls, gk_name):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        if not conn.exists(name):
            return {
                'percentage': 0,
                'description': ''
            }

        redis_hash = conn.hgetall(name)
        return {
                'percentage': int(redis_hash.get(b'percentage', b'0')),
                'description': str(redis_hash.get(b'description' b''))
            }

    @classmethod
    def set_kv(cls, gk_name, key, value):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        conn.hset(name, key, value)

    @classmethod
    def is_switch_on(cls, gk_name):
        return cls.get(gk_name)['percentage'] == 100

    @classmethod
    def in_gk(cls, gk_name, user_id):
        conn = RedisClient.get_connection()
        name = f'gatekeeper:{gk_name}'
        return user_id % 100 < cls.get(gk_name)['percentage']


