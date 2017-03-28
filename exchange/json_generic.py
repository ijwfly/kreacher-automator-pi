# http://treyhunner.com/2013/09/singledispatch-json-serializer/
import json
from functools import singledispatch


class _CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONSerializibleMixin):
            return obj.json_serializible()
        return super(_CustomEncoder, self).default(obj)


def encode(obj, **kwargs):
    return json.dumps(obj, cls=_CustomEncoder, **kwargs)


def decode(obj_json, **kwargs):
    obj = json.loads(obj_json, **kwargs)
    if type(obj) == dict and "__obj__" in obj:
        return JSONSerializibleMixin.from_json(obj)
    return obj


class JSONSerializibleMixin(object):

    @staticmethod
    def _get_children(cls):
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    def json_serializible(self):
        return {
            "__obj__": True,
            "class_name": str(self.__class__.__name__),
            "obj_dict": self.__dict__
        }

    @staticmethod
    def from_json(obj_dict):
        if "__obj__" not in obj_dict:
            return obj_dict
        subclasses = JSONSerializibleMixin._get_children(JSONSerializibleMixin)
        cls = [cls for cls in subclasses if cls.__name__ == obj_dict["class_name"]]
        if not cls:
            raise ValueError("Object not imported.")
        obj = cls[0]()
        for key in obj_dict["obj_dict"]:
            value = obj_dict["obj_dict"].get(key, None)
            if type(value) == list:
                value = [JSONSerializibleMixin.from_json(el) for el in value]
            elif type(value) == dict:
                value = JSONSerializibleMixin.from_json(value)
            setattr(obj, key, value)
        return obj

