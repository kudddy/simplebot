from sqlalchemy import select, and_, desc, func, delete, update
from datetime import datetime

from plugins.pg.tables import user_file_id_status, \
    user_audit_gan, black_list_gan, \
    white_list_gan, user_enter_gan, \
    user_model


def give_me_file_id_in_queen():
    query = select([user_file_id_status.c.file_id]).where(user_file_id_status.c.status == "PENDING")
    return query


def insert_date_to_audit(user_id: int,
                         chat_id: int,
                         username: str,
                         state_name: str):
    query = user_audit_gan.insert().values(
        user_id=user_id,
        chat_id=chat_id,
        username=username,
        date=datetime.now(),
        state_name=state_name
    )
    return query


def get_last_init_session(user_id: int):
    query = select([user_audit_gan.c.date]) \
        .where(and_(user_audit_gan.c.user_id == user_id,
                    user_audit_gan.c.state_name == "hello_message")) \
        .order_by(desc(user_audit_gan.c.date)).limit(1)
    return query


def get_count_call_state_photo(user_id: int):
    # TODO баг, проверяем только в рамках одной сессии, нужно сделать глобальную проверку

    query = select([user_audit_gan.c.user_id, func.count(user_audit_gan.c.user_id).label('counter')]) \
        .where(and_(user_audit_gan.c.date > get_last_init_session(user_id),
                    user_audit_gan.c.state_name == "processor_photo",
                    user_audit_gan.c.user_id == user_id)).group_by(user_audit_gan.c.user_id)

    return query


def check_user_in_black_list(user_id: int):
    query = select([black_list_gan.c.user_id]).where(black_list_gan.c.user_id == user_id)
    return query


def add_user_to_black_list(user_id: int):
    query = black_list_gan.insert().values(
        user_id=user_id,
        date=datetime.now()
    )

    return query


def delete_user_from_black_list(user_id: int):
    query = delete(black_list_gan).where(black_list_gan.c.user_id == user_id)
    return query


def add_user_to_white_list(user_id: int):
    query = white_list_gan.insert().values(
        user_id=user_id,
        date=datetime.now()
    )
    return query


def check_user_in_white_list(user_id: int):
    query = select([white_list_gan.c.user_id]).where(white_list_gan.c.user_id == user_id)
    return query


def select_all_user():
    query = select([user_audit_gan.c.chat_id]).distinct()
    return query


def select_chats_id_from_legacy():
    query = select([user_enter_gan.c.chat_id]).distinct()
    return query


def select_user_model(user_id: int):
    query = select([user_model.c.model_version]).where(user_model.c.user_id == user_id)
    return query


def update_user_model(user_id: int, model_version: str):
    query = update(user_model).where(user_model.c.user_id == user_id).values(model_version=model_version)
    return query


def insert_user_model(user_id: int, model_version: str):
    query = user_model.insert().values(
        user_id=user_id,
        model_version=model_version
    )
    return query


def delete_data_from_user_id_status():
    query = delete(user_file_id_status)
    return query
