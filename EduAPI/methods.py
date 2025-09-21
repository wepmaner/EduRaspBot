import logging
from asyncio import sleep
from typing import List

import aiohttp

from .exceptions import EduDown
from .types import Audience, Group, Lesson, Teacher

logger = logging.getLogger("EduApi-methods")


async def method(url, **params):
    # max_attempts = 5

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result["data"] is None and result["state"] == -1:
                            return []
                        elif result["data"] is None:
                            logger.info(f"Retry in 5 seconds....")
                            await sleep(5)
                        else:
                            return result["data"]
                    else:
                        error_txt = f"Error {response.status} - {response.url}"
                        logger.info(error_txt)
                        raise EduDown("EduDown")
        except Exception as e:
            logger.exception(f"Error sending the request: {e}")
            raise EduDown("EduDown")


count = 0


async def listYear() -> list:
    global count
    """Список доступных годов"""
    result = await method("https://edu.donstu.ru/api/Rasp/ListYears")
    return result["years"]


async def currentYear() -> str:
    """Текущий год"""
    result = await method("https://edu.donstu.ru/api/Rasp/ListYears")
    return result["years"][-1]


async def getGroups(year: str = None) -> List[Group]:
    """Список групп"""
    if year is None:
        year = await currentYear()
    groups = await method("https://edu.donstu.ru/api/raspGrouplist", year=year)
    return [Group(**group) for group in groups]


async def getRaspGroup(idGroup: int, sdate: str = "") -> List[Lesson]:
    """Расписание группы"""
    rasps = await method("https://edu.donstu.ru/api/Rasp", idGroup=idGroup, sdate=sdate)
    if rasps is None or rasps == []:
        return None
    return [Lesson(**rasp) for rasp in rasps["rasp"]]


async def getTeachers(year: str = None):
    """Список преподавателей"""
    if year is None:
        year = await currentYear()
    teachers = await method(f"https://edu.donstu.ru/api/raspTeacherlist", year=year)
    return [Teacher(**teacher) for teacher in teachers]


async def getRaspTeacher(idTeacher: int, sdate: str = "") -> List[Lesson]:
    """Расписание преподавателя"""
    rasps = await method(
        f"https://edu.donstu.ru/api/Rasp", idTeacher=idTeacher, sdate=sdate
    )
    return [Lesson(**rasp) for rasp in rasps["rasp"]]


async def getAudlist(year: str = None) -> List[Audience]:
    """Список аудиторий"""
    if year is None:
        year = await currentYear()
    Audiences = await method(f"https://edu.donstu.ru/api/raspAudlist", year=year)
    return [Audience(**audience) for audience in Audiences]


async def getRaspAudlist(idAudLine: int, sdate: str = "") -> List[Lesson]:
    """Расписание аудитории"""
    rasps = await method(
        f"https://edu.donstu.ru/api/Rasp", idAudLine=idAudLine, sdate=sdate
    )
    return [Lesson(**rasp) for rasp in rasps["rasp"]]
