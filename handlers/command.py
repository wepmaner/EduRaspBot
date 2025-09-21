from datetime import datetime, timedelta

import emoji
from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

import db_manager as db
import gui
import utils
from create_bot import bot
from EduAPI.methods import *

router = Router()


@router.message(Command(commands="cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено")


@router.message(F.text, utils.All_States.set_group)
async def set_group(message: types.Message, state: FSMContext):
    group_user = message.text.upper()
    groups = await getGroups()
    data = await state.get_data()
    bot_message_id = data.get("last_bot_message_id")
    for group in groups:
        if group.name == group_user:
            group_id = group.id
            await db.set_user(group.name, message.from_user.id, group_id, 0)
            now = datetime.now()
            user = await db.get_user(message.from_user.id)
            text = await utils.rasp_send(user, now)
            keyboard = gui.choice_day(now, user[1], user[2])
            await message.delete()
            await bot.edit_message_text(
                text=f"Ваша группа была изменена на "
                + emoji.emojize(":backhand_index_pointing_right:")
                + f" {group_user}\n\n{text}",
                chat_id=message.chat.id,
                message_id=bot_message_id,
                reply_markup=keyboard,
            )
            # await message.answer(,)
            await state.clear()
            break
    else:
        await message.delete()
        # await message.answer(f"Мы не смогли найти группу"+emoji.emojize(":backhand_index_pointing_right:")+ f" {group_user}, пожалуйста перепроверьте ввод или напишите /cancel для отмены команды")
        await bot.edit_message_text(
            text=f"Мы не смогли найти группу"
            + emoji.emojize(":backhand_index_pointing_right:")
            + f" {group_user}, пожалуйста перепроверьте ввод",
            chat_id=message.chat.id,
            message_id=bot_message_id,
            reply_markup=gui.cancel(),
        )


@router.message(F.text, utils.All_States.date)
async def date_two(message: types.Message, state: FSMContext):
    try:
        date = datetime.strptime("2024 " + message.text, "%Y %d.%m")
    except:
        await message.answer("Проверьте правильно ли вы ввели дату")
        return
    user = await db.get_user(message.from_user.id)
    text = await utils.rasp_send(user, date)
    keyboard = gui.choice_day(date, user[1], user[2])
    await message.answer(text, reply_markup=keyboard)
    await state.clear()


@router.message(F.text, utils.All_States.set_teacher)
async def set_teacher(message: types.Message, state: FSMContext):
    teachers = await getTeachers()
    matching_teachers = [
        teacher
        for teacher in teachers
        if teacher.name != None and message.text.lower() in teacher.name.lower()
    ]
    await message.delete()
    data = await state.get_data()
    bot_message_id = data.get("last_bot_message_id")
    if not matching_teachers:
        await bot.edit_message_text(
            "Данного преподавателя не удалось найти, проверьте правильность ввода!",
            chat_id=message.chat.id,
            message_id=bot_message_id,
            reply_markup=gui.cancel(),
        )

    elif len(matching_teachers) == 1:
        teacher = matching_teachers[0]
        await db.set_user(teacher.name, message.from_user.id, teacher.id, 1)
        await bot.edit_message_text(
            f"Текущий пользователь - {teacher.name}",
            chat_id=message.chat.id,
            message_id=bot_message_id,
            reply_markup=gui.cancel(),
        )
        await state.clear()
    else:
        text = "Были найдены несколько преподавателей с такими фамилиями.\n"
        for num, teacher in enumerate(matching_teachers):
            text += f"{num + 1}) /teacher_{teacher.id} - {teacher.name}\n"
        await message.answer(text)
        await state.set_state(utils.All_States.teacher_choice)


@router.message(F.text.startswith("/teacher"), utils.All_States.teacher_choice)
async def teacher_choice(message: types.Message, state: FSMContext):
    command = message.text.split("_")
    teacher_id = command[1]

    teachers = await getTeachers()
    for teacher in teachers:
        if str(teacher.id) == teacher_id:
            name = teacher.name
            await db.set_user(name, message.from_user.id, teacher_id, 1)
            await message.answer(f"Текущий пользователь - {name}")
            await state.clear()
            break
    else:
        await message.answer(f"Преподаватель с таким id не найден")


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.delete()
    user = await db.get_user(message.from_user.id)
    if user is None:
        await state.set_state(utils.All_States.change)
        await message.answer(
            f"Приветствую {emoji.emojize(':raised_hand:')}\nУкажите кто вы",
            reply_markup=gui.student_teacher(),
        )
    else:
        text = "Вы вошли как "
        if user[2] == 0:
            text += f"студент группы {user[0]}"
        else:
            text += f"преподаватель {user[0]}"
        await message.answer(text, reply_markup=gui.choice_button())


@router.message(Command(commands=["now"]))
async def now(message: types.Message, state: FSMContext):
    now = datetime.now()
    user = await db.get_user(message.from_user.id)
    if user is None:
        await change(message, state)
        return
    text = await utils.rasp_send(user, now)

    keyboard = gui.choice_day(now, user[1], user[2])
    await message.answer(text, reply_markup=keyboard)


@router.message(Command(commands=["tomorrow"]))
async def tomorrow(message: types.Message):
    user = await db.get_user(message.from_user.id)
    date = datetime.now() + timedelta(days=1)
    text = await utils.rasp_send(user, date)
    keyboard = gui.choice_day(date, user[1], user[2])
    await message.answer(text, reply_markup=keyboard)


@router.message(Command(commands=["date"]))
async def date(message: types.Message, state: FSMContext):
    await state.set_state(utils.All_States.date)
    now = datetime.now()
    await message.answer(
        f"Напишите дату в формате{emoji.emojize(':backhand_index_pointing_right:')} дд.мм, сегодня: {now.day}.{now.month}"
    )


@router.message(Command(commands=["help"]))
async def help(message: types.Message):
    await message.answer(
        "Список команд:\n/change группа"
        + emoji.emojize(":backhand_index_pointing_right:")
        + "чтобы сменить выбранную группу\n/now "
        + emoji.emojize(":backhand_index_pointing_right:")
        + " для отображения расписания на сегодня, для выбранной группы\n/date 00.00 "
        + emoji.emojize(":backhand_index_pointing_right:")
        + " для вывода даты (вместо нулей напишите нужную дату, например 01.01)\n/tomorrow "
        + emoji.emojize(":backhand_index_pointing_right:")
        + " узнать расписание на завтра "
    )


@router.message(Command(commands="change"))
async def change(message: types.Message, state: FSMContext):
    await state.set_state(utils.All_States.change)
    await message.answer(f"Укажите кто вы", reply_markup=gui.student_teacher())


@router.message(Command(commands=["teacher"]))
async def teacher_rasp(message: types.Message, state: FSMContext):
    await message.answer("Напишите фамилию преподавателя")
    await state.set_state(utils.FindTeacher.name)


@router.message(F.text, utils.FindTeacher.name)
async def teacher_send(message: types.Message, state: FSMContext):
    teachers = await getTeachers()
    matching_teachers = [
        teacher
        for teacher in teachers
        if teacher.name != None and message.text.lower() in teacher.name.lower()
    ]
    if not matching_teachers:
        await message.answer(
            "Данного преподавателя не удалось найти, проверьте правильность ввода!\nВы можете написать /cancel для отмены команды"
        )
    elif len(matching_teachers) == 1:
        teacher = matching_teachers[0]
        current = datetime.now()
        text = await utils.rasp_send([0, teacher.id, 1], date=current)
        await message.answer(
            f"Расписание преподавателя - {teacher.name}\n{text}",
            reply_markup=gui.choice_day(current, teacher.id, 1),
        )
        await state.clear()
    else:
        text = "Были найдены несколько преподавателей с такими фамилиями.\n"
        for num, teacher in enumerate(matching_teachers):
            text += f"{num + 1}) /teacher_{teacher.id} - {teacher.name}\n"
        await message.answer(text)
        await state.set_state(utils.FindTeacher.choice_teacher)


@router.message(F.text.startswith("/teacher"), utils.FindTeacher.choice_teacher)
async def choice_teacher(message: types.Message, state: FSMContext):
    command = message.text.split("_")
    teacher_id = command[1]
    current = datetime.now()
    text = await utils.rasp_send([0, teacher_id, 1], date=current)
    await message.answer(
        f"Расписание преподавателя\n{text}",
        reply_markup=gui.choice_day(current, teacher_id, 1),
    )
    await state.clear()


@router.message(Command(commands=["group"]))
async def group(message: types.Message, state: FSMContext):
    await message.answer("Напишите название группы")
    await state.set_state(utils.FindGroup.name)


@router.message(F.text, utils.FindGroup.name)
async def findgroup_name(message: types.Message, state: FSMContext):
    groups = await getGroups()
    current = datetime.now()
    for group in groups:
        if group.name.lower() == message.text.lower():
            text = await utils.rasp_send([0, group.id, 0], date=current)
            await message.answer(
                f"Расписание группы - {group.name}\n{text}",
                reply_markup=gui.choice_day(current, group.id, 0),
            )
            await state.clear()


@router.message(Command(commands=["class"]))
async def class_rasp(message: types.Message, state: FSMContext):
    await state.set_state(utils.FindClass.name)
    await message.answer(
        emoji.emojize(":writing_hand:")
        + "Напишите номер аудитории, номер корпуса напишите через - или пробел, например 2-805 или 2 805"
    )


@router.message(F.text, utils.FindClass.name)
async def findclass_name(message: types.Message, state: FSMContext):
    class_num = message.text.replace(" ", "-")
    audlists = await getAudlist()
    current = datetime.now()
    for audit in audlists:
        if audit.name == class_num:
            text = await utils.rasp_send([0, audit.id, 2], date=current)
            await message.answer(
                f"Расписание аудитории - {audit.name}\n{text}",
                reply_markup=gui.choice_day(current, audit.id, 2),
            )
            await state.clear()
            break
    else:
        await message.answer(
            "Мы не нашли аудиторию"
            + emoji.emojize(":backhand_index_pointing_right:")
            + f"'{class_num}', возможно вы допустили опечатку. Для отмены нажмите на команду /cancel"
        )
