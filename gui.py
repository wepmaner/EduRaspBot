from datetime import timedelta

from aiogram.utils.keyboard import InlineKeyboardBuilder

import utils


def student_teacher():
    kb = InlineKeyboardBuilder()
    kb.button(text="Я студент", callback_data="student")
    kb.button(text="Я преподаватель", callback_data="teacher")
    kb.adjust(2)
    return kb.as_markup()


def choice_day(current, edu_id, type_id):
    day_keyboard = InlineKeyboardBuilder()
    previous_day = current - timedelta(days=1)
    day_keyboard.button(
        text="Назад",
        callback_data=utils.ChoiceDay(
            edu_id=edu_id, type_id=type_id, current=previous_day.strftime("%Y-%m-%d")
        ),
    )
    next_day = current + timedelta(days=1)
    day_keyboard.button(
        text="Далее",
        callback_data=utils.ChoiceDay(
            edu_id=edu_id, type_id=type_id, current=next_day.strftime("%Y-%m-%d")
        ),
    )
    day_keyboard.button(
        text="По неделям",
        callback_data=utils.ChoiceWeek(
            edu_id=edu_id, type_id=type_id, current=current.strftime("%Y-%m-%d")
        ),
    )
    day_keyboard.adjust(2, repeat=False)
    return day_keyboard.as_markup()


def choice_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Изменить данные", callback_data="change")
    return keyboard.as_markup()


def cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Отмена", callback_data="cancel")
    return keyboard.as_markup()
