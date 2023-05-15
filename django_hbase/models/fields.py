class HBaseField:
    field_type = None

    def __init__(self, reversed=False, column_family=None):
        self.reversed = reversed
        self.column_family = column_family
        # <HOMEWORK>
        # 增加 is_required 属性，默认为 true 和 default 属性，默认 None。
        # 并在 HbaseModel 中做相应的处理，抛出相应的异常信息
        # self.is_required = is_required
        # self.default = default

        # for timestamp field only
        self.auto_now_add = None


class IntegerField(HBaseField):
    field_type = "int"

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)


class TimestampField(HBaseField):
    field_type = "timestamp"

    def __init__(self, *args, auto_now_add=True, **kwargs):
        super(TimestampField, self).__init__(*args, **kwargs)
        self.auto_now_add = auto_now_add
