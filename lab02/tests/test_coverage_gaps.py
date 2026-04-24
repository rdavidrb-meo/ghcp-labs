import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from order_processor import (
    NOTIFICATION_URL,
    get_db_connection,
    load_order,
    notify_customer,
    save_order,
)


def test_get_db_connection_returns_sqlite_connection():
    conn = get_db_connection(":memory:")
    try:
        assert isinstance(conn, sqlite3.Connection)
    finally:
        conn.close()


@patch("order_processor.get_db_connection")
def test_save_order_uses_internal_connection_and_closes_it(mock_get_db_connection, make_order):
    order = make_order()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    result = save_order(order)

    assert result is True
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("order_processor.get_db_connection")
def test_load_order_returns_row_and_closes_internal_connection(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("ORD-001", "test@example.com", 20.0, "2026-04-24T10:00:00")
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    result = load_order("ORD-001")

    assert result == {
        "order_id": "ORD-001",
        "customer_email": "test@example.com",
        "total": 20.0,
        "created_at": "2026-04-24T10:00:00",
    }
    mock_conn.close.assert_called_once()


@patch("order_processor.get_db_connection")
def test_load_order_returns_none_when_missing_and_closes_internal_connection(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    result = load_order("MISSING")

    assert result is None
    mock_conn.close.assert_called_once()


@pytest.mark.asyncio
@patch("order_processor.aiohttp.ClientSession")
async def test_notify_customer_creates_and_closes_session_when_not_provided(mock_client_session, make_order):
    order = make_order()
    mock_session = MagicMock()
    mock_session.close = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_session.post.return_value = mock_context_manager
    mock_client_session.return_value = mock_session

    result = await notify_customer(order, "Order confirmed")

    assert result is True
    mock_session.post.assert_called_once_with(
        f"{NOTIFICATION_URL}/send",
        json={"to": "test@example.com", "body": "Order confirmed", "ref": "ORD-001"},
    )
    mock_session.close.assert_awaited_once()
