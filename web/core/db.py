"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Jun 12, 2018

@author: jrm
"""
import bson
import traceback
from atom.api import (
    Atom, Property, Instance, Dict, Unicode, Coerced, Value, ForwardInstance,
    Typed
)
from atom.dict import _DictProxy
from enaml.application import Application


def find_subclasses(cls):
    """ Finds subclasses of the given class"""
    classes = []
    for subclass in cls.__subclasses__():
        classes.append(subclass)
        classes.extend(find_subclasses(subclass))
    return classes


class _Scope(Atom):
    """ Handles circular references """
    
    #: Circular references
    guards = Typed(set, ())
    
    #: References
    refs = Dict()


class ModelSerializer(Atom):
    """ Handles serializing and deserializing of Model subclasses. It
    will automatically save and restore references where present.
    
    """
    #: Make a singleton so we can reuse the registry
    _instance = None

    #: Store all registered models
    registry = Dict()
    
    @classmethod
    def instance(cls):
        return cls._instance or cls()

    def __init__(self, *args, **kwargs):
        if self._instance is not None:
            raise RuntimeError("Only one serializer should exist!")
        super(ModelSerializer, self).__init__(*args, **kwargs)
        self.__class__._instance = self

    def flatten(self, v, scope=None):
        """ Convert Model objects to a dict """
        flatten = self.flatten
        scope = scope or _Scope()
        
        # Circular reference
        ref = id(v)
        if ref in scope.guards:
            return {'__ref__': ref}
        else:
            scope.guards.add(ref)
        
        if isinstance(v, Model):
            state =  v.__getstate__()
            _id = state.get("_id")
            return {'_id': _id,
                    '__ref__': ref,
                    '__model__': state['__model__']} if _id else state
        elif isinstance(v, (list, tuple, set)):
            return [flatten(item, scope) for item in v]
        elif isinstance(v, (dict, _DictProxy)):
            return {flatten(k, scope): flatten(item, scope) 
                    for k, item in v.items()}
        return v

    async def unflatten(self, v, scope=None):
        """ Convert a dict object to a Model"""
        unflatten = self.unflatten
        scope = scope or _Scope()
        
        if isinstance(v, dict):
            # Circular reference
            ref = v.get('__ref__')
            if ref is not None:
                if ref in scope.refs:
                    return scope.refs[ref]
                else:
                    v.pop('__ref__')
                    obj = await unflatten(v, scope)
                    scope.refs[ref] = obj
                    return obj
            
            # Create the object
            name = v.get('__model__')
            if name is not None:
                Cls = self.registry.get(name)
                if not Cls:
                    raise ValueError(f"Unknown or unregistered model: {name}")
                obj = Cls()
                _id = v.get('_id')
                if _id is not None:
                    v = await Cls.objects.find_one({'_id':_id})
                    # TODO: What if this returns none?
                await obj.__setstate__(v)
                return obj
            return {await unflatten(k): await unflatten(i) 
                    for k, i  in v.items()}
        elif isinstance(v, (list, tuple)):
            return [await unflatten(item) for item in v]
        return v

    def _default_registry(self):
        return {f'{m.__module__}.{m.__name__}': m
                for m in find_subclasses(Model)}


class ModelManager(Atom):
    """ A descriptor so you can use this somewhat like Django's models.
    Assuming your using motor.
    
    Examples
    --------
    MyModel.objects.find_one({'_id':'someid})
    
    """
    def _get_database(self):
        db =  Application.instance().database
        if db is None:
            raise EnvironmentError("No database set!")
        return db
    
    #: Used to access the database
    database = Property(_get_database)

    def __get__(self, obj, cls=None):
        """ Handle objects from the class that owns the manager """
        name = f'{cls.__module__}.{cls.__name__}' if cls else obj.__model__
        return self.database[name]


class Model(Atom):
    """ An atom model that can be serialized and deserialized to and from 
    MongoDB.
    
    """
    __slots__ = ('__weakref__',)
    
    #: ID of this object in the database
    _id = Instance(bson.ObjectId)

    #: Model type for serialization / deserialization
    __model__ = Unicode()

    #: Fields thare are saved in the db. By default it uses all atom members
    #: that don't start with an underscore and are not taged with store.
    __fields__ = Instance(set, ())
    
    # =========================================================================
    # Defaults 
    # =========================================================================
    def _default___fields__(self):
        """ By default it ignores any pivate members (starting with underscore)
        and any member tagged with store=False.
        """
        return set((m.name for m in self.members().values()
                    if not m.name.startswith("_") and
                        (not m.metadata or m.metadata.get('store', True))))

    def _default___model__(self):
        cls = self.__class__
        return f'{cls.__module__}.{cls.__name__}'

    # ==========================================================================
    # Serialization API
    # ==========================================================================

    #: Handles encoding and decoding
    serializer = ModelSerializer.instance()

    def __getstate__(self):
        state = super(Model, self).__getstate__()
        flatten = self.serializer.flatten
        state = {f: flatten(state[f]) for f in self.__fields__}
        state['__model__'] = self.__model__
        state['__ref__'] = id(self)  # ID for circular references
        if self._id is not None:
            state['_id'] = self._id
        return state

    async def __setstate__(self, state):
        """ Restore an object from the a state from the database. This is
        async as it will lookup any referenced objects from the DB.
        
        """
        unflatten = self.serializer.unflatten
        name = state.get('__model__')

        if name is None:
            raise ValueError("State must contain the __model__ key")
        if name != self.__model__:
            raise ValueError(f"Trying to use {name} state for "
                             f"{self.__model__} object")
        for k, v in state.items():
            if hasattr(self, k):
                try:
                    setattr(self, k, await unflatten(v))
                except Exception as e:
                    exc = traceback.format_exc()
                    Application.instance().logger.error(
                        f"State {self.__model__}.{k} = {v}: {exc}")
    
    # ==========================================================================
    # Database API
    # ==========================================================================
    
    #: Handles database access
    objects = ModelManager()
    
    @classmethod
    async def restore(cls, state):
        """ Restore an object from the database """
        obj = cls()
        await obj.__setstate__(state)
        return obj
    
    async def save(self):
        """ Alias to delete this object to the database """
        db  = self.objects
        state = self.__getstate__()
        if self._id is not None:
            return await db.replace_one({'_id': self._id}, state, upsert=True)
        else:
            r= await db.insert_one(state)
            self._id = r.inserted_id
            return r

    async def delete(self):
        """ Alias to delete this object in the database """
        db = self.objects
        if self._id:
            return await db.delete_one({'_id': self._id})
