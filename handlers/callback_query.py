from datetime import datetime, timedelta

import emoji
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

import gui
import utils
from EduAPI.exceptions import EduDown
from EduAPI.methods import *

router = Router()


@router.callback_query(F.data == "student", utils.All_States.change)
async def start_student(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите свою группу")
    await state.update_data(last_bot_message_id=callback.message.message_id)
    await state.set_state(utils.All_States.set_group)


# start - choice выбор преподаватель
@router.callback_query(F.data == "teacher", utils.All_States.change)
async def start_teacher(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите свою фамилию")
    await state.update_data(last_bot_message_id=callback.message.message_id)
    await state.set_state(utils.All_States.set_teacher)


# Кнопки назад далее выбор дня
@router.callback_query(utils.ChoiceDay.filter())
async def ChoiceDay_inline(
    callback: types.CallbackQuery, callback_data: utils.ChoiceDay
):
    date_current = datetime.strptime(callback_data.current, "%Y-%m-%d")
    send = await utils.rasp_send(
        [0, callback_data.edu_id, callback_data.type_id], date=date_current
    )
    keyboard = gui.choice_day(date_current, callback_data.edu_id, callback_data.type_id)
    await callback.message.edit_text(send, reply_markup=keyboard)


# Кнопки назад далее выбор недели
@router.callback_query(utils.ChoiceWeek.filter())
async def ChoiceWeek_inline(
    callback: types.CallbackQuery, callback_data: utils.ChoiceWeek
):
    if callback_data.type_id == 2:
        try:
            rasps = await getRaspAudlist(callback_data.edu_id)
        except EduDown:
            await callback.message.edit_text(
                    "Сервер с расписанием не отвечает.\nНевозможно получить расписание"
                )
            return
    else:
        cache_key = "teacher" if callback_data.type_id else "group"
        rasps = utils.cache[cache_key].get(callback_data.edu_id)
        if not rasps:
            try:
                rasps = await utils.get_rasp(
                    callback_data.edu_id, callback_data.type_id
                )
            except EduDown:
                await callback.message.edit_text(
                    "Сервер с расписанием не отвечает.\nНевозможно получить расписание"
                )
                return
    date_current = datetime.strptime(callback_data.current, "%Y-%m-%d")

    current_day_of_week = date_current.weekday()
    start_of_week = date_current - timedelta(days=current_day_of_week)
    end_of_week = start_of_week + timedelta(days=6)

    next_week = start_of_week + timedelta(days=7)
    previous_week = start_of_week - timedelta(days=7)
    type_week = "Неизвестно"
    days_keyboad = []
    days_week = []
    for rasp in rasps:
        rasp_data = datetime.strptime(rasp.дата, "%Y-%m-%dT%H:%M:%S")
        if (
            rasp_data >= start_of_week
            and rasp_data <= end_of_week
            and not rasp_data in days_week
        ):
            #callback_text = f"ChoiceDay:{callback_data.edu_id}:{callback_data.type_id}:{rasp_data.strftime('%Y-%m-%d')}"
            #print(rasp_data.strftime('%Y-%m-%d'))
            days_keyboad.append(
                types.InlineKeyboardButton(
                    text=rasp.день_недели,
                    callback_data=utils.ChoiceDay(
                        edu_id=callback_data.edu_id,
                        type_id=callback_data.type_id,
                        current=rasp_data.strftime('%Y-%m-%d')
                    ).pack()
                )
            )
            days_week.append(rasp_data)
            type_week = "Нижняя неделя" if rasp.типНедели % 2 == 0 else "Верхняя неделя"

    kb = [days_keyboad[i : i + 2] for i in range(0, len(days_keyboad), 2)]
    kb += [
        [
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=utils.ChoiceWeek(
                    edu_id=callback_data.edu_id,
                    type_id=callback_data.type_id,
                    current=previous_week.strftime('%Y-%m-%d')
                ).pack()
            ),
            types.InlineKeyboardButton(
                text="Далее",
                callback_data=utils.ChoiceWeek(
                    edu_id=callback_data.edu_id,
                    type_id=callback_data.type_id,
                    current=next_week.strftime('%Y-%m-%d')
                ).pack()
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="По дням",
                callback_data=utils.ChoiceDay(
                    edu_id=callback_data.edu_id,
                    type_id=callback_data.type_id,
                    current=date_current.strftime('%Y-%m-%d')
                ).pack()
            )
        ],
    ]
    text = f"Неделя с {start_of_week.day}.{start_of_week.month} по {end_of_week.day}.{end_of_week.month}\nНеделя {emoji.emojize(':backhand_index_pointing_right:')} {type_week}"
    await callback.message.edit_text(
        text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.callback_query(F.data == "change")
async def change(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(utils.All_States.change)
    await callback.message.edit_text(
        f"Укажите кто вы", reply_markup=gui.student_teacher()
    )


@router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено")
