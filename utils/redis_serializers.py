from django.core import serializers
from utils.json_encoder import JSONEncoder

class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # django serializer input is QuerySet or list type
        # so, we need to convert instance to a list
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # need to add .object to get model type's object.
        # otherwise, the data is not ORM object but a DeserializedObject type
        return list(serializers.deserialize('json', serialized_data))[0].object