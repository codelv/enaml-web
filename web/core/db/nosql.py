"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jun 12, 2018

@author: jrm
"""
import bson
from atom.api import Instance
from .base import ModelManager, ModelSerializer, Model, find_subclasses


class NoSQLModelSerializer(ModelSerializer):
    """ Handles serializing and deserializing of Model subclasses. It
    will automatically save and restore references where present.

    """
    async def get_object_state(self, obj, _id):
        ModelType = obj.__class__
        return await ModelType.objects.find_one({'_id': _id})

    def _default_registry(self):
        return {m.__model__: m for m in find_subclasses(NoSQLModel)}


class NoSQLModelManager(ModelManager):
    """ A descriptor so you can use this somewhat like Django's models.
    Assuming your using motor or txmongo.

    Examples
    --------
    MyModel.objects.find_one({'_id':'someid})

    """
    def __get__(self, obj, cls=None):
        """ Handle objects from the class that owns the manager """
        cls = cls or obj.__class__
        if not issubclass(cls, Model):
            return self  # Only return the collection when used from a Model
        return self.database[cls.__model__]


class NoSQLModel(Model):
    """ An atom model that can be serialized and deserialized to and from
    MongoDB.

    """

    #: ID of this object in the database
    _id = Instance(bson.ObjectId)

    #: Handles encoding and decoding
    serializer = NoSQLModelSerializer.instance()

    #: Handles database access
    objects = NoSQLModelManager.instance()

    async def save(self):
        """ Alias to delete this object to the database """
        db = self.objects
        state = self.__getstate__()
        if self._id is not None:
            return await db.replace_one({'_id': self._id}, state, upsert=True)
        else:
            r = await db.insert_one(state)
            self._id = r.inserted_id
            return r

    async def delete(self):
        """ Alias to delete this object in the database """
        db = self.objects
        if self._id:
            return await db.delete_one({'_id': self._id})
