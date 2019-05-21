from django.test import TestCase

import os

from .models import Company, Contact, SupplierPart, SupplierPriceBreak
from .models import rename_company_image


class CompanySimpleTest(TestCase):

    fixtures = [
        'company',
        'category',
        'part',
        'location',
        'bom',
        'supplier_part',
        'price_breaks',
    ]

    def setUp(self):
        Company.objects.create(name='ABC Co.',
                               description='Seller of ABC products',
                               website='www.abc-sales.com',
                               address='123 Sales St.',
                               is_customer=False,
                               is_supplier=True)

        self.acme0001 = SupplierPart.objects.get(SKU='ACME0001')
        self.acme0002 = SupplierPart.objects.get(SKU='ACME0002')
        self.zerglphs = SupplierPart.objects.get(SKU='ZERGLPHS')
        self.zergm312 = SupplierPart.objects.get(SKU='ZERGM312')

    def test_company_model(self):
        c = Company.objects.get(name='ABC Co.')
        self.assertEqual(c.name, 'ABC Co.')
        self.assertEqual(str(c), 'ABC Co. - Seller of ABC products')

    def test_company_url(self):
        c = Company.objects.get(pk=1)
        self.assertEqual(c.get_absolute_url(), '/company/1/')

    def test_image_renamer(self):
        c = Company.objects.get(pk=1)
        rn = rename_company_image(c, 'test.png')
        self.assertEqual(rn, 'company_images' + os.path.sep + 'company_1_img.png')

        rn = rename_company_image(c, 'test2')
        self.assertEqual(rn, 'company_images' + os.path.sep + 'company_1_img')

    def test_part_count(self):

        acme = Company.objects.get(pk=1)
        appel = Company.objects.get(pk=2)
        zerg = Company.objects.get(pk=3)
        
        self.assertTrue(acme.has_parts)
        self.assertEqual(acme.part_count, 2)

        self.assertTrue(appel.has_parts)
        self.assertEqual(appel.part_count, 1)

        self.assertTrue(zerg.has_parts)
        self.assertEqual(zerg.part_count, 1)

    def test_price_breaks(self):
        
        self.assertTrue(self.acme0001.has_price_breaks)
        self.assertTrue(self.acme0002.has_price_breaks)
        self.assertTrue(self.zerglphs.has_price_breaks)
        self.assertFalse(self.zergm312.has_price_breaks)

        self.assertEqual(self.acme0001.price_breaks.count(), 3)
        self.assertEqual(self.acme0002.price_breaks.count(), 2)
        self.assertEqual(self.zerglphs.price_breaks.count(), 2)
        self.assertEqual(self.zergm312.price_breaks.count(), 0)

    def test_quantity_pricing(self):
        """ Simple test for quantity pricing """

        p = self.acme0001.get_price
        self.assertEqual(p(1), 10)
        self.assertEqual(p(4), 40)
        self.assertEqual(p(11), 82.5)
        self.assertEqual(p(23), 172.5)
        self.assertEqual(p(100), 350)

        p = self.acme0002.get_price
        self.assertEqual(p(1), None)
        self.assertEqual(p(2), None)
        self.assertEqual(p(5), 35)
        self.assertEqual(p(45), 315)
        self.assertEqual(p(55), 68.75)


class ContactSimpleTest(TestCase):

    def setUp(self):
        # Create a simple company
        c = Company.objects.create(name='Test Corp.', description='We make stuff good')

        # Add some contacts
        Contact.objects.create(name='Joe Smith', company=c)
        Contact.objects.create(name='Fred Smith', company=c)
        Contact.objects.create(name='Sally Smith', company=c)

    def test_exists(self):
        self.assertEqual(Contact.objects.count(), 3)

    def test_delete(self):
        # Remove the parent company
        Company.objects.get(pk=1).delete()
        self.assertEqual(Contact.objects.count(), 0)
