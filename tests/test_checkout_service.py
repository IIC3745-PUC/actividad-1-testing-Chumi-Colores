import unittest
from unittest.mock import Mock, patch

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
    def testChargeResult(self):
        result = ChargeResult(ok=True, charge_id="aaaaa", reason=None)
        self.assertTrue(result.ok)
        self.assertEqual(result.charge_id, "aaaaa")
        self.assertIsNone(result.reason)

    def testCheckoutServiceHappyPath(self):
        fraud = Mock()
        fraud.score.return_value = 50
        service = CheckoutService(
            payments = Mock(),
            email = Mock(),
            fraud = fraud,
            repo = Mock(),
        )

        self.assertIsInstance(service.payments, Mock)
        self.assertIsInstance(service.email, Mock)
        self.assertIsInstance(service.fraud, Mock)
        self.assertIsInstance(service.repo, Mock)
        self.assertIsInstance(service.pricing, PricingService)
        
        result = service.checkout(
            user_id="aaaa",
            items= [CartItem(sku="bbbb", unit_price_cents=1000, qty=1)],
            payment_token="cccc",
            country="CL",
            coupon_code="",
        )
        self.assertIsInstance(result, str)

    def testInvalidUser(self):
        service = CheckoutService(
            payments = Mock(),
            email = Mock(),
            fraud = Mock(),
            repo = Mock(),
        )

        result = service.checkout(
            user_id="  ",
            items= [CartItem(sku="bbbb", unit_price_cents=1000, qty=1)],
            payment_token="cccc",
            country="CL",
        )

        self.assertIsInstance(result, str)
        self.assertEqual(result, "INVALID_USER")

    def testInvalidCart(self):
        service = CheckoutService(
            payments = Mock(),
            email = Mock(),
            fraud = Mock(),
            repo = Mock(),
        )

        result = service.checkout(
            user_id="aaaa",
            items= [CartItem(sku="bbbb", unit_price_cents=-1000, qty=1)],
            payment_token="cccc",
            country="CL",
        )

        self.assertIsInstance(result, str)
        self.assertEqual(result, "INVALID_CART:unit_price_cents must be >= 0")
    
    def testFraudRejection(self):
        fraud = Mock()
        fraud.score.return_value = 80
        service = CheckoutService(
            payments = Mock(),
            email = Mock(),
            fraud = fraud,
            repo = Mock(),
        )

        result = service.checkout(
            user_id="aaaa",
            items= [CartItem(sku="bbbb", unit_price_cents=1000, qty=1)],
            payment_token="cccc",
            country="CL",
        )

        self.assertEqual(result, "REJECTED_FRAUD")

    def testFailedPayment(self):
        fraud = Mock()
        fraud.score.return_value = 50
        payments = Mock()
        payments.charge.return_value = ChargeResult(ok=False, charge_id=None, reason="card declined")
        service = CheckoutService(
            payments = payments,
            email = Mock(),
            fraud = fraud,
            repo = Mock(),
        )

        result = service.checkout(
            user_id="aaaa",
            items= [CartItem(sku="bbbb", unit_price_cents=1000, qty=1)],
            payment_token="cccc",
            country="CL",
        )

        self.assertEqual(result, "PAYMENT_FAILED:card declined")