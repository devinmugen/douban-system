import time
from pymongo import MongoClient
mongua = MongoClient()


def timestamp():
    return int(time.time())


def next_id(name):
    query = {
        'name': name,
    }
    update = {
        '$inc': {
            'seq': 1
        }
    }
    kwargs = {
        'query': query,
        'update': update,
        'upsert': True,
        'new': True,
    }
    # 存储数据的 id
    doc = mongua.db['data_id']
    # find_and_modify 是一个原子操作函数
    new_id = doc.find_and_modify(**kwargs).get('seq')
    return new_id


class Mongua(object):
    __fields__ = [
        '_id',
        # (字段名, 类型, 值)
        ('id', int, -1),
        ('type', str, ''),
        ('deleted', bool, False),
        ('created_time', int, 0),
        ('updated_time', int, 0),
    ]

    @classmethod
    def has(cls, **kwargs):
        return cls.find_one(**kwargs) is not None

    def mongos(self, name):
        return mongua.db[name]._find()

    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v) for k, v in self.__dict__.items())
        return '<{0}: \n  {1}\n>'.format(class_name, '\n  '.join(properties))

    @classmethod
    def new(cls, form=None, **kwargs):
        name = cls.__name__
        m = cls()
        fields = cls.__fields__.copy()
        fields.remove('_id')
        if form is None:
            form = {}
        for f in fields:
            k, t, v = f
            if k in form:
                setattr(m, k, t(form[k]))
            else:
                setattr(m, k, v)
        for k, v in kwargs.items():
            if hasattr(m, k):
                setattr(m, k, v)
            else:
                raise KeyError
        m.id = next_id(name)
        ts = int(time.time())
        m.created_time = ts
        m.updated_time = ts
        m.type = name.lower()
        #
        m.save()
        return m

    @classmethod
    def _new_with_bson(cls, bson):
        m = cls()
        fields = cls.__fields__.copy()
        fields.remove('_id')
        for f in fields:
            k, t, v = f
            if k in bson:
                setattr(m, k, bson[k])
            else:
                # 设置默认值
                setattr(m, k, v)
        setattr(m, '_id', bson['_id'])
        # 这一句必不可少，否则 bson 生成一个新的_id
        # FIXME, 因为现在的数据库里面未必有 type
        # 所以在这里强行加上
        # 以后洗掉db的数据后应该删掉这一句
        m.type = cls.__name__.lower()
        return m

    @classmethod
    def all(cls):
        return cls._find()

    # TODO, 还应该有一个函数 find(name, **kwargs)
    @classmethod
    def _find(cls, **kwargs):
        name = cls.__name__
        # TODO 过滤掉被删除的元素
        # kwargs['deleted'] = False
        flag_sort = '__sort'
        sort = kwargs.pop(flag_sort, None)
        ds = mongua.db[name].find(kwargs)
        if sort is not None:
            ds = ds.sort(sort)
        l = [cls._new_with_bson(d) for d in ds]
        return l

    @classmethod
    def _find_raw(cls, **kwargs):
        name = cls.__name__
        ds = mongua.db[name]._find(kwargs)
        l = [d for d in ds]
        return l
        # 直接 list() 就好了
        # return list(l)

    @classmethod
    def _clean_field(cls, source, target):

        ms = cls._find()
        for m in ms:
            v = getattr(m, source)
            setattr(m, target, v)
            m.save()

    @classmethod
    def find_by(cls, **kwargs):
        return cls.find_one(**kwargs)

    @classmethod
    def find_all(cls, **kwargs):
        return cls._find(**kwargs)

    @classmethod
    def find(cls, id):
        return cls.find_one(id=id)

    @classmethod
    def get(cls, id):
        return cls.find_one(id=id)

    @classmethod
    def find_one(cls, **kwargs):
        """
        """
        # TODO 过滤掉被删除的元素
        # kwargs['deleted'] = False
        # print('cls', cls)
        # print('in ---')
        # print('kwargs', kwargs)
        l = cls._find(**kwargs)
        # print('out ---')
        # print('find one debug', kwargs, l)
        if len(l) > 0:
            return l[0]
        else:
            return None

    @classmethod
    def upsert(cls, query_form, update_form, hard=False):
        ms = cls.find_one(**query_form)
        if ms is None:
            query_form.update(**update_form)
            ms = cls.new(query_form)
        else:
            ms.update(update_form, hard=hard)
        return ms

    def update(self, form, hard=False):
        for k, v in form.items():
            if hard or hasattr(self, k):
                setattr(self, k, v)
        # self.updated_time = int(time.time()) fixme
        self.save()

    def save(self):
        name = self.__class__.__name__
        # print('mongo save self', self)
        # print('mongo save', name)
        mongua.db[name].save(self.__dict__)

    def delete(self):
        name = self.__class__.__name__
        query = {
            'id': self.id,
        }
        mongua.db[name].delete_one(query)


    def blacklist(self):
        b = [
            '_id',
        ]
        return b

    def json(self):
        _dict = self.__dict__
        d = {k: v for k, v in _dict.items() if k not in self.blacklist()}
        # TODO, 增加一个 type 属性
        return d

    def data_count(self, cls):

        name = cls.__name__
        # TODO, 这里应该用 type 替代
        fk = '{}_id'.format(self.__class__.__name__.lower())
        query = {
            fk: self.id,
        }
        count = mongua.db[name]._find(query).count()
        return count

    def get_created_time(self):
        t = self.created_time
        strt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        return strt
