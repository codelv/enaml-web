"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.

Created on Aug 2, 2018

@author: jrm
"""
import os
import datetime
import sqlalchemy as sa
from functools import wraps
from atom import api
from atom.api import Atom, Int, Dict, Instance
from .base import ModelManager, ModelSerializer, Model, find_subclasses


# kwargs reserved for sqlalchemy table columns
COLUMN_KWARGS = (
    'autoincrement', 'default', 'doc', 'key', 'index', 'info', 'nullable',
    'onupdate', 'primary_key', 'server_default', 'server_onupdate',
    'quote', 'unique', 'system', 'comment'
)


def py_type_to_sql_column(cls, **kwargs):
    """ Convert the python type to an alchemy table column type

    """
    if issubclass(cls, Model):
        name =  f'{cls.__model__}._id'
        return (sa.Integer, sa.ForeignKey(name))
    elif issubclass(cls, str):
        return sa.String(**kwargs)
    elif issubclass(cls, int):
        return sa.Integer(**kwargs)
    elif issubclass(cls, float):
        return sa.Integer(**kwargs)
    elif issubclass(cls, datetime.datetime):
        return sa.DateTime(**kwargs)
    elif issubclass(cls, datetime.date):
        return sa.Date(**kwargs)
    elif issubclass(cls, datetime.time):
        return sa.Time(**kwargs)
    raise NotImplementedError(f"A column for {cls} could not be detected, "
                              "please specifiy it manually by tagging it with "
                              ".tag(column=<sqlalchemy column>)")


def atom_member_to_sql_column(member, **kwargs):
    """ Convert the atom member type to an sqlalchemy table column type

    """
    if isinstance(member, api.Str):
        return sa.String(**kwargs)
    elif isinstance(member, api.Unicode):
        return sa.Unicode(**kwargs)
    elif isinstance(member, api.Bool):
        return sa.Boolean(**kwargs)
    elif isinstance(member, api.Int):
        return sa.Integer(**kwargs)
    elif isinstance(member, api.Long):
        return sa.BigInteger(**kwargs)
    elif isinstance(member, api.Float):
        return sa.Float(**kwargs)
    elif isinstance(member, api.Range):
        # TODO: Add min / max
        return sa.Integer(**kwargs)
    elif isinstance(member, api.FloatRange):
        # TODO: Add min / max
        return sa.Float(**kwargs)
    elif isinstance(member, api.Enum):
        return sa.Enum(*member.items)
    elif isinstance(member, (api.Instance, api.Typed,
                             api.ForwardInstance, api.ForwardTyped)):
        if hasattr(member, 'resolve'):
            value_type = member.resolve()
        else:
            value_type = member.validate_mode[-1]
        if value_type is None:
            raise TypeError("Instance and Typed members must specifiy types")
        return py_type_to_sql_column(value_type, **kwargs)
    elif isinstance(member, (api.List, api.ContainerList, api.Tuple)):
        item_type = member.validate_mode[-1]
        if item_type is None:
            raise TypeError("List and Tuple members must specifiy types")

        # Resolve the item type
        if hasattr(item_type, 'resolve'):
            value_type = item_type.resolve()
        else:
            value_type = item_type.validate_mode[-1]

        if value_type is None:
            raise TypeError("List and Tuple members must specifiy types")
        elif isinstance(value_type, Model):
            name =  f'{value_type.__model__}._id'
            return (sa.Integer, sa.ForeignKey(name))
        return sa.ARRAY(py_type_to_sql_column(value_type, **kwargs))
    elif isinstance(member, api.Bytes):
        return sa.LargeBinary(**kwargs)
    elif isinstance(member, api.Dict):
        return sa.JSON(**kwargs)
    raise NotImplementedError(f"A column for {member} could not be detected, "
                              "please specifiy it manually by tagging it with "
                              ".tag(column=<sqlalchemy column>)")


def create_table_column(member):
    """ Converts an Atom member into a sqlalchemy data type.

    Parameters
    ----------
    member: Member
        The atom member

    Returns
    -------
    column: Column
        An sqlalchemy column

    References
    ----------
    1. https://docs.sqlalchemy.org/en/latest/core/types.html

    """
    metadata = member.metadata or {}

    # If a column is specified use that
    if 'column' in metadata:
        return metadata['column']

    metadata.pop('store', None)

    # Extract column kwargs from member metadata
    kwargs = {}
    for k in COLUMN_KWARGS:
        if k in metadata:
            kwargs[k] = metadata.pop(k)

    args = atom_member_to_sql_column(member, **metadata)
    if not isinstance(args, (tuple, list)):
        args = (args,)
    return sa.Column(member.name, *args, **kwargs)


def create_table(model):
    """ Create an sqlalchemy table by inspecting the Model and generating
    a column for each member.

    """
    if not issubclass(model, Model):
        raise TypeError("Only Models are supported")
    name = model.__model__
    metadata = sa.MetaData()
    members = model.members()
    columns = (create_table_column(members[f]) for f in model.__fields__)
    return sa.Table(name, metadata, *columns)


class SQLModelSerializer(ModelSerializer):
    """ Uses sqlalchemy to lookup the model.

    """
    async def get_object_state(self, obj, _id):
        ModelType = obj.__class__
        result = await ModelType.objects.select('*').where(_id=_id)
        # Convert the result to a dict
        return result

    def _default_registry(self):
        return {m.__model__: m for m in find_subclasses(SQLModel)}


class SQLModelManager(ModelManager):
    """ Manages models via aiopg, aiomysql, or similar libraries supporting
    SQLAlchemy tables. It stores a table for each class

    """
    #: Mapping of model to table used to store the model
    tables = Dict()

    def _default_tables(self):
        """ Create all the tables """
        return {m: create_table(m) for m in find_subclasses(SQLModel)}

    def __get__(self, obj, cls=None):
        """ Retrieve the table for the requested object or class.

        """
        cls = cls or obj.__class__
        if not issubclass(cls, Model):
            return self  # Only return the client when used from a Model
        if cls not in self.tables:
            self.tables[cls] = create_table(cls)
        table = self.tables[cls]
        return SQLClient(manager=self, table=table)


class SQLClient(Atom):
    """ A light wrapper that ensures that a connection to the DB is aquired
    before each transaction.

    """
    #: Engine instance for the given backend
    manager = Instance(SQLModelManager)

    #: Table instance
    table = Instance(sa.Table)

    async def __getattr__(self, attr):
        """ Wrap each query """
        engine = self.manager.database
        async with engine.aquire() as conn:
            return getattr(conn, attr)(*args, **kwargs)


class SQLModel(Model):
    """ A model that can be saved and restored to and from a database supported
    by sqlalchemy.

    """
    #: ID of this object in the database
    _id = Int().tag(primary_key=True)

    #: Use SQL serializer
    serializer = SQLModelSerializer.instance()

    #: Use SQL object manager
    objects = SQLModelManager.instance()

    async def save(self):
        """ Alias to delete this object to the database """
        db  = self.objects
        state = self.__getstate__()
        if self._id is not None:
            return await db.insert({'_id': self._id}, state, upsert=True)
        else:
            r = await db.execute(self.table.insert().values(state))
            self._id = r.inserted_id
            return r

    async def delete(self):
        """ Alias to delete this object in the database """
        db = self.objects
        if self._id:
            return await db.excute(db.table.delete().where(_id=self._id))
