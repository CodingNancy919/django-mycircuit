# memcached
FOLLOWING_PATTERN = 'followings:{user_id}'
# 一般follower会不断更新，并且对于有些人可能有千万级别的粉丝，没有必要缓存 然而following量级不会特别大，也不会频繁更新因此一般缓存following
#redis