"""
Конфигурация pytest для тестирования Telegram бота
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Chat, Message, CallbackQuery

# Импорты для тестирования
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers import command, callback_query
from utils import All_States, FindTeacher, FindGroup, FindClass
from EduAPI.types import Group, Teacher, Lesson, Audience


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для всех тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user():
    """Создает мок пользователя"""
    user = User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser"
    )
    return user


@pytest.fixture
def mock_chat():
    """Создает мок чата"""
    chat = Chat(
        id=123456789,
        type="private"
    )
    return chat


@pytest.fixture
def mock_message(mock_user, mock_chat):
    """Создает мок сообщения"""
    class MockMessage:
        def __init__(self):
            self.message_id = 1
            self.from_user = mock_user
            self.chat = mock_chat
            self.date = datetime.now()
            self.text = "test message"
            self.delete = AsyncMock()
            self.answer = AsyncMock()
            self.edit_text = AsyncMock()
    
    return MockMessage()


@pytest.fixture
def mock_callback_query():
    cb = MagicMock()                       # no strict spec
    cb.message = MagicMock()               # no strict spec -> can assign any attrs
    cb.message.message_id = 123
    cb.message.edit_text = AsyncMock()     # key: present and awaitable
    return cb


@pytest.fixture
def mock_state():
    """Создает мок FSMContext"""
    state = AsyncMock(spec=FSMContext)
    state.get_data.return_value = {"last_bot_message_id":1234}
    state.set_data.return_value = None
    state.update_data.return_value = None
    state.clear.return_value = None
    state.set_state.return_value = None
    return state


@pytest.fixture
def mock_bot():
    """Создает мок бота"""
    bot = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.send_message = AsyncMock()
    return bot


@pytest.fixture
def sample_group():
    """Создает образец группы для тестов"""
    return Group(
        id=1,
        name="ИВТ-21",
        course=2,
        year="2024"
    )


@pytest.fixture
def sample_teacher():
    """Создает образец преподавателя для тестов"""
    return Teacher(
        id=1,
        name="Иванов Иван Иванович",
        department="Кафедра информатики"
    )


@pytest.fixture
def sample_lesson():
    """Создает образец урока для тестов"""
    return Lesson(
        id=1,
        дисциплина="Программирование",
        преподаватель="Иванов И.И.",
        группа="ИВТ-21",
        аудитория="2-805",
        начало="08:30",
        конец="10:15",
        дата="2024-01-15T08:30:00",
        день_недели="Понедельник",
        типНедели=1
    )


@pytest.fixture
def sample_audience():
    """Создает образец аудитории для тестов"""
    return Audience(
        id=1,
        name="2-805",
        building="2",
        floor=8,
        capacity=30
    )


@pytest.fixture
def mock_db_pool():
    """Создает мок пула соединений с БД"""
    pool = AsyncMock()
    connection = AsyncMock()
    cursor = AsyncMock()
    
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.execute = AsyncMock()
    
    connection.cursor.return_value.__aenter__.return_value = cursor
    connection.cursor.return_value.__aexit__.return_value = None
    connection.commit = AsyncMock()
    
    pool.acquire.return_value.__aenter__.return_value = connection
    pool.acquire.return_value.__aexit__.return_value = None
    
    return pool


@pytest.fixture
def mock_edu_api():
    """Создает мок для EduAPI методов"""
    with patch.multiple(
        'EduAPI.methods',
        getGroups=AsyncMock(return_value=[]),
        getTeachers=AsyncMock(return_value=[]),
        getRaspGroup=AsyncMock(return_value=[]),
        getRaspTeacher=AsyncMock(return_value=[]),
        getAudlist=AsyncMock(return_value=[]),
        getRaspAudlist=AsyncMock(return_value=[]),
        listYear=AsyncMock(return_value={"years": ["2024"]}),
        currentYear=AsyncMock(return_value="2024")
    ) as mocks:
        yield mocks


@pytest.fixture
def mock_utils_cache():
    """Создает мок кэша утилит"""
    cache = {
        "EduAlive": True,
        "last_update": 0,
        "group": {},
        "teacher": {}
    }
    return cache


# Патчи для изоляции тестов
@pytest.fixture(autouse=True)
def mock_db_manager(mock_db_pool):
    """Автоматически патчит db_manager для всех тестов"""
    with patch('db_manager.get_pool', return_value=mock_db_pool), \
         patch('db_manager.connect', AsyncMock()), \
         patch('db_manager.set_user', AsyncMock()):
        yield


@pytest.fixture(autouse=True)
def mock_utils_cache_patch(mock_utils_cache):
    """Автоматически патчит кэш утилит"""
    with patch('utils.cache', mock_utils_cache):
        yield


@pytest.fixture(autouse=True)
def mock_bot_patch(mock_bot):
    """Автоматически патчит бота"""
    with patch('create_bot.bot', mock_bot):
        yield
