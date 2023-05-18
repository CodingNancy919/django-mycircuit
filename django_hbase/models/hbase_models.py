from django.conf import settings
from django_hbase.client import HBaseClient
from django_hbase.models import HBaseField, IntegerField, TimestampField
import time


class BadRowKeyError(Exception):
    pass


class EmptyColumnError(Exception):
    pass


class HBaseModel:

    class Meta:
        table_name = None
        row_key = ()

    @classmethod
    def get_table(cls):
        conn = HBaseClient.get_connection()
        table_name = cls.get_table_name()
        return conn.table(name=table_name, use_prefix=None)

    @classmethod
    def get_table_name(cls):
        if not cls.Meta.table_name:
            raise NotImplementedError("missing table name in HBaseModel meta class")
        if settings.TESTING:
            return "test_{}".format(cls.Meta.table_name)
        return cls.Meta.table_name

    @classmethod
    def drop_table(cls):
        if not settings.TESTING:
            raise Exception("you can not drop table in PRO environment")
        conn = HBaseClient.get_connection()
        conn.delete_table(cls.get_table_name(), True)

    @classmethod
    def create_table(cls):
        if not settings.TESTING:
            raise Exception("you can not create table in PRO environment")
        conn = HBaseClient.get_connection()
        tables = [table.decode('UTF-8') for table in conn.tables]
        if cls.get_table_name() in tables:
            return
        column_families = {
            field.column_family: dict()
            for key, field in cls.get_field_hash().items()
            if field.column_family is not None
        }

        conn.create_table(cls.get_table_name(), column_families)



    @classmethod
    def get_field_hash(cls):
        field_hash = {}
        for field in cls.__dict__:
            field_obj = getattr(cls, field)
            if isinstance(field_obj, HBaseField):
                field_hash[field] = field_obj
        return field_hash

    def __init__(self, **kwargs):
        for key, field in self.get_field_hash().items():
            value = kwargs.get(key)
            if isinstance(field, TimestampField) and field.auto_now_add and value is None:
                value = int(time.time() * 1000000)
            setattr(self, key, value)

    @property
    def row_key(self):
        return self.serialize_row_key(self.__dict__)

    @classmethod
    def serialize_row_key(cls, data, is_prefix=False):
        """
       serialize dict to bytes (not str)
       {key1: val1} => b"val1"
       {key1: val1, key2: val2} => b"val1:val2"
       {key1: val1, key2: val2, key3: val3} => b"val1:val2:val3"
       """
        row_key = []
        for key, field in cls.get_field_hash().items():
            if field.column_family:
                continue
            value = data.get(key)
            if value is None:
                if not is_prefix:
                    raise BadRowKeyError(f"{key} is missing in row key")

            value = cls.serialize_field(field, value)
            if ':' in value:
                raise BadRowKeyError(f"{key} should not contain ':' in value: {value}")
            row_key.append(value)

        return bytes(':'.join(row_key), encoding='UTF-8')

    @classmethod
    def deserialize_row_key(cls, row_key):
        """
      "val1" => {'key1': val1, 'key2': None, 'key3': None}
      "val1:val2" => {'key1': val1, 'key2': val2, 'key3': None}
      "val1:val2:val3" => {'key1': val1, 'key2': val2, 'key3': val3}
      """
        data = {}
        if isinstance(row_key, bytes):
            row_key = row_key.decode(encoding='UTF-8')
        row_key = row_key + ':'

        for key in cls.Meta.row_key:
            index = row_key.find(':')
            if index == -1:
                break
            data[key] = cls.deserialize_field(key, row_key[:index])
            row_key = row_key[index+1:]
        return data

    @classmethod
    def serialize_field(cls, field, value):
        value = str(value)
        if isinstance(field, IntegerField):
            # 因为排序规则是按照字典序排序，那么就可能出现 1 10 2 这样的排序
            # 解决的办法是固定 int 的位数为 16 位（8的倍数更容易利用空间），不足位补 0
            while len(value) < 16:
                value = '0' + value
        if field.reversed:
            value = value[::-1]
        return value

    @classmethod
    def deserialize_field(cls, key, value):
        field = cls.get_field_hash()[key]
        if field.reversed:
            value = value[::-1]
        # if isinstance(field, IntegerField) or isinstance(field, TimestampField):
        #     value = int(value)
        if field.field_type in [IntegerField.field_type, TimestampField.field_type]:
            value = int(value)
        return value

    @classmethod
    def serialize_row_data(cls, data):
        row_data = {}
        for key, field in cls.get_field_hash().items():
            if field.column_family:
                value = data.get(key)
                if value is None:
                    continue
                column_key = f"{field.column_family}:{key}"
                column_value = cls.serialize_field(field, value)
                row_data[column_key] = column_value
        return row_data

    def save(self):
        row_data = self.serialize_row_data(self.__dict__)
        # 如果 row_data 为空，即没有任何 column key values 需要存储 hbase 会直接不存储
        # 这个 row_key, 因此我们可以 raise 一个 exception 提醒调用者，避免存储空值
        if len(row_data) == 0:
            raise EmptyColumnError()

        table = self.get_table()
        row_key = self.serialize_row_key(self.__dict__)
        table.put(row_key, row_data)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def get(cls, **kwargs):
        table = cls.get_table()
        row_key = cls.serialize_row_key(kwargs)
        row = table.row(row_key)
        return cls.init_from_row(row_key, row)

    @classmethod
    def init_from_row(cls, row_key, row_data):
        if not row_data:
            return None
        data = cls.deserialize_row_key(row_key)
        for column_key, column_value in row_data.items():
            # remove column family
            column_key = column_key.decode('utf-8')
            key = column_key[column_key.find(':') + 1:]
            data[key] = cls.deserialize_field(key, column_value)
        return cls(**data)

    @classmethod
    def serialize_row_key_from_tuple(cls, row_key_tuple):
        if row_key_tuple is None:
            return None
        row_key = {
            key: value
            for key, value in zip(cls.Meta.row_key, row_key_tuple)
        }
        return cls.serialize_row_key(row_key)

    @classmethod
    def filter(cls, start=None, stop=None, prefix=None, limit=None, reverse=False):
        row_start = cls.serialize_row_key_from_tuple(start)
        row_stop = cls.serialize_row_key_from_tuple(stop)
        row_prefix = cls.serialize_row_key_from_tuple(prefix)

        table = cls.get_table()
        row = table.scan(row_start, row_stop, row_prefix, limit=limit, reverse=reverse)

        results = []
        for row_key, row_data in row:
            instance = cls.init_from_row(row_key, row_data)
            results.append(instance)
        return results


