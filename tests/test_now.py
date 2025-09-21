import pytest
from unittest.mock import patch
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers import command
from utils import All_States, FindTeacher, FindGroup, FindClass

@pytest.mark.asyncio
async def test_command_now_new_user(mock_message, mock_state):
    """Тест команды /now для нового пользователя"""
    with patch('db_manager.get_user', return_value=None):
        await command.now(mock_message, mock_state)
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "Укажите кто вы" ==  call_args[0][0]