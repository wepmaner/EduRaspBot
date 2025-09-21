import pytest
from unittest.mock import patch, AsyncMock
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers import command, callback_query
from utils import All_States, FindTeacher, FindGroup, FindClass
from EduAPI.types import Group

def sample_groups():
    """Список групп для тестов"""
    return [
        Group(id=1, name="ВИ32", course=3, year="2025"),
        Group(id=2, name="ИВТ21", course=2, year="2025"),
        Group(id=3, name="ПИ22", course=1, year="2025"),
    ]


@pytest.mark.asyncio
async def test_command_change_student(mock_callback_query, mock_state):
    """Тест change для студента"""
    await callback_query.start_student(mock_callback_query, mock_state)
    mock_callback_query.message.edit_text.assert_called_once()
    call_args = mock_callback_query.message.edit_text.call_args
    assert "Напишите свою группу" ==  call_args[0][0]

@pytest.mark.asyncio
async def test_command_change_teacher(mock_callback_query, mock_state):
    """Тест change для студента"""
    await callback_query.start_teacher(mock_callback_query, mock_state)
    mock_callback_query.message.edit_text.assert_called_once()
    call_args = mock_callback_query.message.edit_text.call_args
    assert "Напишите свою фамилию" ==  call_args[0][0]

@pytest.mark.asyncio
async def test_command_set_group(mock_message, mock_state):
    """Тест вывода группы для студента"""
    mock_message.text = "ваыа"
    with patch('handlers.command.getGroups', AsyncMock(return_value=sample_groups())), \
         patch('handlers.command.bot.edit_message_text', AsyncMock()) as mock_edit, \
         patch('handlers.command.db.get_user', return_value=["ВИ32",123,0]):
        await command.set_group(mock_message, mock_state)
        mock_edit.assert_called_once()
        mock_message.delete.assert_called_once()
        call_args = mock_edit.call_args
        # Проверяем text из kwargs, так как все аргументы переданы именованными
        assert "Мы не смогли найти группу" in call_args[1]["text"]

@pytest.mark.asyncio
async def test_command_set_group(mock_message, mock_state):
    """Тест вывода группы для студента"""
    mock_message.text = "ВИ32"
    with patch('handlers.command.getGroups', AsyncMock(return_value=sample_groups())), \
         patch('handlers.command.bot.edit_message_text', AsyncMock()) as mock_edit, \
         patch('handlers.command.db.get_user', return_value=["ВИ32",123,0]):
        await command.set_group(mock_message, mock_state)
        mock_edit.assert_called_once()
        mock_message.delete.assert_called_once()
        call_args = mock_edit.call_args
        # Проверяем text из kwargs, так как все аргументы переданы именованными
        assert "Ваша группа была изменена на" in call_args[1]["text"]