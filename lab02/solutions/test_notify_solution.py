"""
SOLUTION — Part 3: Async Testing with AsyncMock
=================================================
Tests for notify_customer() using AsyncMock and pytest-asyncio.
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
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
    async def test_non_200_returns_false(self):
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_session.post.return_value.__aenter__.return_value = mock_response

        order = make_test_order()
        result = await notify_customer(order, "Hello", session=mock_session)

        assert result is False

    @pytest.mark.asyncio
    async def test_client_error_returns_false(self):
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.post.side_effect = aiohttp.ClientError()

        order = make_test_order()
        result = await notify_customer(order, "Hello", session=mock_session)

        assert result is False
