from sqlalchemy import (
    Column, Date, Integer,
    MetaData, String, Table
)

from sqlalchemy.types import UserDefinedType

# SQLAlchemy рекомендует использовать единый формат для генерации названий для
# индексов и внешних ключей.
# https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)


# добавлена поддерка типа CUBE
class CUBE(UserDefinedType):
    def get_col_spec(self, **kw):
        return "CUBE"


user_enter_gan = Table(
    'user_data_gan',
    metadata,
    Column('user_id', Integer),
    Column('chat_id', Integer),
    Column('username', String),
    Column('date', Date)
)

user_file_id_status = Table(
    'user_file_id_status',
    metadata,
    Column('user_id', Integer),
    Column('chat_id', Integer),
    Column('username', String),
    Column('file_id', String),
    Column('date', Date),
    Column('status', String)
)

user_audit_gan = Table(
    'user_audit_gan',
    metadata,
    Column('user_id', Integer),
    Column('chat_id', Integer),
    Column('username', String),
    Column('date', Date),
    Column('state_name', String)
)

black_list_gan = Table(
    'black_list_gan',
    metadata,
    Column('user_id', Integer),
    Column('date', Date)
)

white_list_gan = Table(
    'white_list_gan',
    metadata,
    Column('user_id', Integer),
    Column('date', Date)

)

user_model = Table(
    'user_model',
    metadata,
    Column('user_id', Integer),
    Column('model_version', String)
)
