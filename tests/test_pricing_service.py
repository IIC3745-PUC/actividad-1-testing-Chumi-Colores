import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):
	
	def testQtyNegative(self):
		ps = PricingService()
		with self.assertRaises(PricingError, msg="qty must be > 0"):
			ps.subtotal_cents([CartItem("item1", 1000, -1)])

	def testApplyCouponSave10(self):
		ps = PricingService()
		self.assertEqual(ps.apply_coupon(10000, "SAVE10"), 9000)

	def testApplyCouponClp2000(self):
		ps = PricingService()
		self.assertEqual(ps.apply_coupon(15000, "CLP2000"), 13000)
		self.assertEqual(ps.apply_coupon(1500, "CLP2000"), 0)
	
	def testApplyCouponInvalid(self):
		ps = PricingService()
		with self.assertRaises(PricingError, msg="invalid coupon"):
			ps.apply_coupon(10000, "INVALID")

	def testTaxCentsEU(self):
		ps = PricingService()
		self.assertEqual(ps.tax_cents(10000, "EU"), 2100)

	def testTaxCentsUS(self):
		ps = PricingService()
		self.assertEqual(ps.tax_cents(10000, "US"), 0)
	
	def testTaxCentsError(self):
		ps = PricingService()
		with self.assertRaises(PricingError, msg="unsupported country"):
			ps.tax_cents(10000, "XX")
	
	def testShippingCentsUs(self):
		ps = PricingService()
		self.assertEqual(ps.shipping_cents(10000, "US"), 5000)

	def testInvalidShippingCountry(self):
		ps = PricingService()
		with self.assertRaises(PricingError, msg="unsupported country"):
			ps.shipping_cents(10000, "XX")