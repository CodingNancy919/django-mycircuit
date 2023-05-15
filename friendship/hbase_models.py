from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    """
    存储 from_user_id follow 了哪些人，row_key 按照 from_user_id + created_at 排序
    可以支持查询：
     - A 关注的所有人按照关注时间排序
     - A 在某个时间段内关注的人有哪些
     - A 在某个时间点之后/之前关注的前 X 个人是谁
    """
    from_user_id = models.IntegerField(reversed=True, is_required=True)
    to_user_id = models.IntegerField()
    created_at = models.TimestampField(auto_now_add=True, column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')