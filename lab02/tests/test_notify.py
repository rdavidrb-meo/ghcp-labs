"""
Part 3 — Async Testing with AsyncMock (15 min)
================================================
Goal: Test the async notify_customer() function using AsyncMock
and pytest-asyncio.

Key concepts:
  - AsyncMock (from unittest.mock, Python 3.8+)
  - Mocking async context managers (the `async with session.post(...)` pattern)
  - assert_awaited_once_with() instead of assert_called_once_with()

Hints (try on your own first!):
  - Mock the context manager response:
      mock_session.post.return_value.__aenter__.return_value.status = 200
  - Use @pytest.mark.asyncio on each test
  - Use assert_awaited_once_with() for async verification
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock
from order_processor import Order, OrderItem, notify_customer, NOTIFICATION_URL


def make_test_order():
    return Order(
        order_id="ORD-001",
        customer_email="test@example.com",
        items=[OrderItem("PROD-1", "Widget", 1, 10.00)],
    )


class TestNotifyCustomer:

    @pytest.mark.asyncio
    async def test_successful_notification(self):
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.post.return_value.__aenter__.return_value = mock_response

        order = make_test_order()
        result = await notify_customer(order, "Your order is confirmed!", session=mock_session)

        assert result is True
        mock_session.post.assert_called_once_with(
            f"{NOTIFICATION_URL}/send",
            json={"to": "test@example.com", "body": "Your order is confirmed!", "ref": "ORD-001"},
        )

    @pytest.mark.asyncio
    async def test_failed_notification_non_200(self):
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_session.post.return_value.__aenter__.return_value = mock_response

        order = make_test_order()
        result = await notify_customer(order, "Hello", session=mock_session)

        assert result is False

    @pytest.mark.asyncio
    async def test_network_error_returns_false(self):
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.post.side_effect = aiohttp.ClientError()

        order = make_test_order()
        result = await notify_customer(order, "Hello", session=mock_session)

        assert result is False
