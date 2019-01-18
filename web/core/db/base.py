"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jun 12, 2018

@author: jrm
"""
import os
import traceback
from atom.api import (
    Atom, Property, Instance, Dict, Unicode, Coerced, Value, Typed, Bytes
)
from atom.atom import AtomMeta, with_metaclass
from atom.dict import _DictProxy
from web.core.app import WebApplication
from pprint import pformat


def find_subclasses(cls):
    """ Finds subclasses of the given class"""
    classes = []
    for subclass in cls.__subclasses__():
        classes.append(subclass)
        classes.extend(find_subclasses(subclass))
    return classes


class ModelSerializer(Atom):
    """ Handles serializing and deserializing of Model subclasses. It
    will automatically save and restore references where present.

    """
    #: Hold one instance per subclass for easy reuse
    _instances = {}

    #: Store all registered models
    registry = Dict()

    @classmethod
    def instance(cls):
        if cls not in ModelSerializer._instances:
            ModelSerializer._instances[cls] = cls()
        return ModelSerializer._instances[cls]

    def flatten(self, v, scope=None):
        """ Convert Model objects to a dict

        Parameters
        ----------
        v: Object
            The object to flatten
        scope: Dict
            The scope of references available for circular lookups

        Returns
        -------
        result: Object
            The flattened object

        """
        flatten = self.flatten
        scope = scope or {}

        # Handle circular reference
        if isinstance(v, Model):
            ref = v.__ref__
            if ref in scope:
                return {'__ref__': ref, '__model__': v.__model__}
            else:
                scope[ref] = v
            state =  v.__getstate__(scope)
            _id = state.get("_id")
            return {'_id': _id,
                    '__ref__': ref,
                    '__model__': state['__model__']} if _id else state
        elif isinstance(v, (list, tuple, set)):
            return [flatten(item, scope) for item in v]
        elif isinstance(v, (dict, _DictProxy)):
            return {k: flatten(item, scope)
                    for k, item in v.items()}
        # TODO: Handle other object types
        return v

    async def unflatten(self, v, scope=None):
        """ Convert dict or list to Models

        Parameters
        ----------
        v: Dict or List
            The object(s) to unflatten
        scope: Dict
            The scope of references available for circular lookups

        Returns
        -------
        result: Object
            The unflattened object

        """
        unflatten = self.unflatten
        scope = scope or {}

        if isinstance(v, dict):
            # Circular reference
            ref = v.get('__ref__')
            if ref is not None and ref in scope:
                return scope[ref]

            # Create the object
            name = v.get('__model__')
            if name is not None:
                cls = self.registry.get(name)
                if not cls:
                    raise KeyError(f"Unknown or unregistered model: {name}")
                # Use the classes serializer
                return await cls.serializer.unflatten_object(cls, v, scope)
            return {k: await unflatten(i, scope) for k, i in v.items()}
        elif isinstance(v, (list, tuple)):
            return [await unflatten(item, scope) for item in v]
        return v

    def _default_registry(self):
        raise NotImplementedError

    async def unflatten_object(self, cls, state, scope):
        """ Restore the object for the given class, state, and scope.
        If a reference is given the scope should be updated with the newly
        created object using the given ref.

        Parameters
        ----------
        cls: Class
            The type of object expected
        state: Dict
            The state of the object to restore

        Returns
        -------
        result: object or None
            A the newly created object (or an existing object if using a cache)
            or None if this object does not exist in the database.
        """
        _id = state.get('_id')
        ref = state.get('__ref__')

        # Get the object for this id, retrieve from cache if needed
        obj, created = await self.get_or_create(cls, _id)

        # Lookup the object if needed
        if created and _id is not None:
            # If a new object was created lookup the state for that object
            state = await self.get_object_state(obj, _id)
            if state is None:
                return None

        # Child objects may have circular references to this object
        # so we must update the scope with this reference to handle this
        # before restoring any children
        if ref is not None:
            scope[ref] = obj

        # If not restoring from cache update the state
        if created:
            await obj.__setstate__(state, scope)
        return obj

    async def get_or_create(self, cls, _id):
        """ Get a cached object for this _id or create a new one. Subclasses
        should override this as needed to provide object caching if desired.

        Parameters
        ----------
        cls: Class
            The type of object expected
        _id: Object
            The object ID used by this ModelManager

        Returns
        -------
        result: Tuple[object, bool]
            A tuple of the object and a flag stating if it was created or not.

        """
        return (cls.__new__(cls), True)

    async def get_object_state(self, obj,  _id):
        """ Lookup the state needed to restore the given object id and class.

        Parameters
        ----------
        obj: Object
            The object created by `get_or_create`
        _id: Object
            The object ID used by this ModelManager

        Returns
        -------
        result: Dict
            The model state needed to restore this object

        """
        raise NotImplementedError


class ModelManager(Atom):
    """ A descriptor so you can use this somewhat like Django's models.
    Assuming your using motor.

    Examples
    --------
    MyModel.objects.find_one({'_id':'someid})

    """

    #: Stores instances of each class so we can easily reuse them if desired
    _instances = {}

    @classmethod
    def instance(cls):
        if cls not in ModelManager._instances:
            ModelManager._instances[cls] = cls()
        return ModelManager._instances[cls]

    def _get_database(self):
        db = WebApplication.instance().database
        if db is None:
            raise EnvironmentError("No database set!")
        return db

    #: Used to access the database
    database = Property(_get_database)

    def __get__(self, obj, cls=None):
        """ Handle objects from the class that owns the manager. Subclasses
        should override this as needed.

        """
        raise NotImplementedError


class ModelMeta(AtomMeta):
    def __new__(meta, name, bases, dct):
        cls = AtomMeta.__new__(meta, name, bases, dct)

        # Fields that are saved in the db. By default it uses all atom members
        # that don't start with an underscore and are not taged with store.
        if '__fields__' not in dct:
            cls.__fields__ = tuple((
                m.name for m in cls.members().values()
                if not m.name.startswith("_") and
                (not m.metadata or m.metadata.get('store', True))
            ))

        # Model name used so the serializer knows what class to recreate
        # when restoring
        if '__model__' not in dct:
            cls.__model__ = f'{cls.__module__}.{cls.__name__}'
        return cls


class Model(with_metaclass(ModelMeta, Atom)):
    """ An atom model that can be serialized and deserialized to and from
    a database.

    """
    __slots__ = '__weakref__'

    #: ID of this object in the database. Subclasses can redefine this as needed
    _id = Bytes()

    #: A unique ID used to handle cyclical serialization and deserialization
    #: Do NOT use python's id() as these are reused and can cause conflicts
    __ref__ = Bytes(factory=lambda: os.urandom(16))

    # ==========================================================================
    # Serialization API
    # ==========================================================================

    #: Handles encoding and decoding. Subclasses should redefine this to a
    #: subclass of ModelSerializer
    serializer = None

    def __getstate__(self, scope=None):
        state = super(Model, self).__getstate__()
        flatten = self.serializer.flatten

        scope = scope or {}
        ref = self.__ref__
        scope[ref] = self
        state = {f: flatten(state[f], scope) for f in self.__fields__}
        state['__model__'] = self.__model__
        state['__ref__'] = ref # ID for circular references
        if self._id is not None:
            state['_id'] = self._id
        return state

    async def __setstate__(self, state, scope=None):
        """ Restore an object from the a state from the database. This is
        async as it will lookup any referenced objects from the DB.

        State is restored by calling setattr(k, v) for every item in the state
        that has an associated atom member.  Members can be tagged with a
        `setstate_order=<number>` to define the order of setattr calls. Errors
        from setattr are caught and logged instead of raised.

        Parameters
        ----------
        state: Dict
            A dictionary of state keys and values
        scope: Dict or None
            A namespace to use to resolve any possible circular references.
            The __ref__ value is used as the keys.

        """
        unflatten = self.serializer.unflatten
        name = state.get('__model__')

        if name is None:
            raise ValueError("State must contain the __model__ key")
        if name != self.__model__:
            raise ValueError(f"Trying to use {name} state for "
                             f"{self.__model__} object")
        scope = scope or {}
        ref = state.pop('__ref__', None)
        if ref is not None:
            scope[ref] = self
        members = self.members()

        # Order the keys by the members 'setstate_order' if given
        valid_keys = []
        for k in state.keys():
            m = members.get(k)
            if m is not None:
                if m.metadata:
                    order = m.metadata.get('setstate_order', 1000)
                else:
                    order = 1000
                valid_keys.append((order, k))
        valid_keys.sort()

        for order, k in valid_keys:
            v = state[k]
            try:
                obj = await unflatten(v, scope)
                setattr(self, k, obj)
            except Exception as e:
                exc = traceback.format_exc()
                WebApplication.instance().logger.error(
                    f"Error setting state:"
                    f"{self.__model__}.{k} = {pformat(obj)}:"
                    f"\nSelf: {ref}: {scope.get(ref)}"
                    f"\nValue: {pformat(v)}"
                    f"\nScope: {pformat(scope)}"
                    f"\nState: {pformat(state)}"
                    f"\n{exc}"
                )

    # ==========================================================================
    # Database API
    # ==========================================================================

    #: Handles database access. Subclasses should redefine this.
    objects = None

    @classmethod
    async def restore(cls, state):
        """ Restore an object from the database """
        obj = cls.__new__(cls)
        await obj.__setstate__(state)
        return obj

    async def save(self):
        """ Alias to delete this object to the database """
        raise NotImplementedError

    async def delete(self):
        """ Alias to delete this object in the database """
        raise NotImplementedError
