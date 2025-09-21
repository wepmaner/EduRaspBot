import asyncio

import aiomysql

from config import *


async def connect():
    global pool
    loop = asyncio.get_event_loop()
    pool = await aiomysql.create_pool(
        host=host, port=db_port, user=user, password=password, db=db_name, loop=loop
    )


def get_pool():
    return pool


async def get_user(tg_id: int):
    """Возвращает данные пользователя с бд"""
    sql = f"SELECT groupp,number_1,teacher from users where id = {tg_id};"
    async with pool.acquire() as con:
        async with con.cursor() as cur:
            await cur.execute(sql)
            user = await cur.fetchone()
            return user


# Запись пользователя в бд
async def set_user(name_or_fio: str, tg_id: int, EduId: int, is_teacher: bool):
    """Обновить/Записать данные пользователя"""
    user = await get_user(tg_id)

    # Используем параметризованные запросы для безопасности
    if user:
        sql = """
            UPDATE users 
            SET 
                groupp = %s,
                number_1 = %s, 
                teacher = %s
            WHERE id = %s;
        """
        params = (name_or_fio, EduId, is_teacher, tg_id)
    else:
        sql = """
            INSERT INTO users (id, name_or_fio, number_1, teacher) 
            VALUES (%s, %s, %s, %s);
        """
        params = (tg_id, name_or_fio, EduId, is_teacher)

    async with pool.acquire() as con:
        async with con.cursor() as cur:
            await cur.execute(sql, params)
            await con.commit()
