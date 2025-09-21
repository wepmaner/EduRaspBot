import pytest
from unittest.mock import patch
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers import command
from utils import All_States, FindTeacher, FindGroup, FindClass

@pytest.mark.asyncio
async def test_start_command_new_user(mock_message, mock_state):
    """Тест команды /start для нового пользователя"""
    with patch('db_manager.get_user', return_value=None):
        await command.start(mock_message, mock_state)
        
        mock_message.delete.assert_called_once()
        mock_state.set_state.assert_called_once_with(All_States.change)
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "Приветствую ✋\nУкажите кто вы" ==  call_args[0][0]

@pytest.mark.asyncio
async def test_start_command_student(mock_message, mock_state):
    """Тест команды /start для студента"""
    with patch('db_manager.get_user', return_value=["ВИ32",123,0]):
        await command.start(mock_message, mock_state)
        
        mock_message.delete.assert_called_once()
        #mock_state.set_state.assert_called_once_with(All_States.change)
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "Вы вошли как студент группы ВИ32" == call_args[0][0]

@pytest.mark.asyncio
async def test_start_command_teacher(mock_message, mock_state):
    """Тест команды /start для студента"""
    with patch('db_manager.get_user', return_value=["Абоба",123,1]):
        await command.start(mock_message, mock_state)
        
        mock_message.delete.assert_called_once()
        #mock_state.set_state.assert_called_once_with(All_States.change)
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "Вы вошли как преподаватель Абоба" == call_args[0][0]




