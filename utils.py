from datetime import datetime

import emoji
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.state import State, StatesGroup

from EduAPI import types as EduTypes
from EduAPI.methods import *


class ChoiceDay(CallbackData, prefix="ChoiceDay"):
    edu_id: int
    type_id: int
    current: str


class ChoiceWeek(CallbackData, prefix="ChoiceWeek"):
    edu_id: int
    type_id: int
    current: str


class All_States(StatesGroup):
    change = State()  # Смена группы или преподавателя
    set_group = State()
    set_teacher = State()
    teacher_choice = State()

    date = State()  # Отправка расписания по дате
    find = State()  # Поиск преподавателя
    find_choice = State()  # Выбор преподавателя из списка
    admin = State()
    class_info = State()


class FindTeacher(StatesGroup):
    name = State()
    choice_teacher = State()


class FindGroup(StatesGroup):
    name = State()


class FindClass(StatesGroup):
    name = State()


cache = {"EduAlive": True, "last_update": 0, "group": {}, "teacher": {}}


# Получение расписания с Edu
async def get_rasp(edu_id: int, is_teacher: bool):
    if is_teacher:
        rasp = await getRaspTeacher(edu_id)
        cache["teacher"][edu_id] = rasp
    else:
        rasp = await getRaspGroup(edu_id)
        cache["group"][edu_id] = rasp
    return rasp


def rasp_text(lesson: EduTypes.Lesson, type_id: int) -> str:
    """Отрисовка текста с расписанием"""
    lesson_time = {
        "08:30": "1",
        "10:15": "2",
        "12:00": "3",
        "14:15": "4",
        "16:00": "5",
        "17:45": "6",
        "19:30": "7",
    }

    if type_id == 0:
        info = f"{emoji.emojize(':man_teacher:')}Преподаватель: {lesson.преподаватель}"
    elif type_id == 1:
        info = f"{emoji.emojize(':person_raising_hand:')}Группа: {lesson.группа}"
    elif type_id == 2:
        info = f"{emoji.emojize(':person_raising_hand:')}Группа: {lesson.группа}\n{emoji.emojize(':man_teacher:')}Преподаватель: {lesson.преподаватель}"
    else:
        raise ValueError("Invalid type_id. It should be 0, 1, or 2.")

    return (
        f"{emoji.emojize(':open_book:')} Пара № {lesson_time[lesson.начало]}: {lesson.дисциплина}\n"
        f"{info}\n"
        f"Начало в: {lesson.начало} До: {lesson.конец}{emoji.emojize(':person_running:')}\n"
        f"Аудитория: {lesson.аудитория}\n\n"
    )


async def rasp_send(user, date: datetime = None) -> str:
    if user[2] == 2:
        try:
            rasps = await getRaspAudlist(user[1])
        except EduDown:
            text = "Сервер с расписанием не отвечает.\nНевозможно получить расписание"
            return text
    else:
        cache_key = "teacher" if user[2] else "group"
        rasps = cache[cache_key].get(user[1])
        # if rasps is not None:
        #     return 'Ваша группа не найдена. Напишите /change для её смены'
        if rasps is None:
            try:
                rasps = await get_rasp(user[1], user[2])
            except EduDown:
                text = (
                    "Сервер с расписанием не отвечает.\nНевозможно получить расписание"
                )
                return text

    current = datetime.now()

    formatted_date = date.strftime("%d.%m" if current.year == date.year else "%d.%m.%Y")

    filtered_rasps = [
        day
        for day in rasps
        if datetime.strptime(day.дата, "%Y-%m-%dT%H:%M:%S").date() == date.date()
    ]
    text = "".join(rasp_text(day, user[2]) for day in filtered_rasps)

    if text:
        last_day = filtered_rasps[-1]
        type_week = "Нижняя неделя" if last_day.типНедели % 2 == 0 else "Верхняя неделя"
        text = f"{last_day.день_недели} - {formatted_date}\n\n{text}Неделя {emoji.emojize(':backhand_index_pointing_right:')} {type_week}"
    else:
        today_text = (
            "Сегодня"
            if date.day == current.day and date.month == current.month
            else "В этот день"
        )
        text = f"Дата {formatted_date}\n\n{today_text} {'воскресенье, пар нет' if date.weekday() == 6 else 'нет пар, хорошо вам отдохнуть'} {emoji.emojize(':smiling_face_with_sunglasses:')}"
    if not cache["EduAlive"]:
        text = (
            f"⚠️Сервер с расписанием не отвечает, информация может быть не актуальна. Последнее обновление {cache['last_update'] // 60} час назад\n\n"
            + text
        )
    return text
