import pytest
from unittest.mock import patch, AsyncMock
import sys
import os
from EduAPI.exceptions import EduDown
from utils import ChoiceWeek
# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers import command, callback_query
from utils import All_States, FindTeacher, FindGroup, FindClass
from EduAPI.types import Group


@pytest.mark.asyncio
async def test_choice_week_inline_callback_EduDown(mock_callback_query):
    """Тест EduDown для разных типов пользователей"""
    
    # Тест для группы (type_id=0)
    with patch('handlers.callback_query.utils.get_rasp', side_effect=EduDown("API Error")), \
        patch('handlers.callback_query.utils.cache', {'teacher': {}, 'group': {}}):
        choice_week = ChoiceWeek(edu_id=1, type_id=0, current="2025-01-01")
        await callback_query.ChoiceWeek_inline(mock_callback_query, choice_week)
        assert mock_callback_query.message.edit_text.call_args[0][0] == "Сервер с расписанием не отвечает.\nНевозможно получить расписание"

    # Тест для преподавателя (type_id=1)
    with patch('handlers.callback_query.utils.get_rasp', side_effect=EduDown("API Error")), \
        patch('handlers.callback_query.utils.cache', {'teacher': {}, 'group': {}}):
        choice_week = ChoiceWeek(edu_id=1, type_id=1, current="2025-01-01")
        await callback_query.ChoiceWeek_inline(mock_callback_query, choice_week)
        assert mock_callback_query.message.edit_text.call_args[0][0] == "Сервер с расписанием не отвечает.\nНевозможно получить расписание"
    
    # Сброс мока для следующего теста
    mock_callback_query.message.edit_text.reset_mock()
     
    # Тест для аудитории (type_id=2)
    with patch('handlers.callback_query.getRaspAudlist', side_effect=EduDown("API Error")):
        choice_week = ChoiceWeek(edu_id=1, type_id=2, current="2025-01-01")
        await callback_query.ChoiceWeek_inline(mock_callback_query, choice_week)
        assert mock_callback_query.message.edit_text.call_args[0][0] == "Сервер с расписанием не отвечает.\nНевозможно получить расписание"

    # Сброс мока для следующего теста
    mock_callback_query.message.edit_text.reset_mock()

    # Тест для аудитории (type_id=2)
    with patch('handlers.callback_query.getRaspAudlist', side_effect=EduDown("API Error")):
        choice_week = ChoiceWeek(edu_id=1, type_id=2, current="2025-01-01")
        await callback_query.ChoiceWeek_inline(mock_callback_query, choice_week)
        assert mock_callback_query.message.edit_text.call_args[0][0] == "Сервер с расписанием не отвечает.\nНевозможно получить расписание"

# @pytest.mark.asyncio
# async def test_choice_week_inline_callback_group_rasp_send(mock_callback_query):
#     with patch('handlers.callback_query.utils.get_rasp', side_effect=EduDown("API Error")), \
#          patch('handlers.callback_query.utils.cache', {'teacher': {}, 'group': {1:}}):
#         choice_week = ChoiceWeek(edu_id=1, type_id=1, current="2025-01-01")
#         await callback_query.ChoiceWeek_inline(mock_callback_query, choice_week)
#         assert mock_callback_query.message.edit_text.call_args[0][0] == "Сервер с расписанием не отвечает.\nНевозможно получить расписание"
    