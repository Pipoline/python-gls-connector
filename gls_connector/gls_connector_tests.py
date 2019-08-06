from datetime import date

import unittest

from .gls_connector import GlsConnectorConfig
from .gls_connector import GlsConnector
from .gls_connector import PackageSender
from .gls_connector import PackageRecipient
from .gls_connector import PackageOrder

import logging
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


class TestGlsConnectorMethods(unittest.TestCase):

    def test_calculate_hash(self):
        config = GlsConnectorConfig(user_name='gls_user', password='gls_pass', sender_id='2334')

        sender = PackageSender(name='Some company, s.r.o.', street='Street 20', city='Košice', zip_code='04001',
                               country_code='SK', contact='Jozef Mrkva', phone='0910xxxxxx', mail='info@company.com')
        recipient = PackageRecipient(name='Peter Customer', street='Hlavná 23', city='Košice',
                                     zip_code='04001', country_code='SK', contact='Peter Customer',
                                     mail='peter.customer@mail.me', phone='0900xxxxxx')
        order = PackageOrder(sender=sender, recipient=recipient, pick_up_date=date(2018, 11, 19), count_of_parcels=1,
                             client_reference='124', cod_amount='99', cod_reference='codref')

        hashed_data: str = GlsConnector.calculate_hash(config=config, order=order).__str__()
        self.assertEqual('30e784ac681bf4603c884d38535d71892ce804c6', hashed_data)

    @unittest.skip("needs be mocked gls server response")
    def test_print_label(self):
        config = GlsConnectorConfig(user_name='gls_user', password='gls_pass', sender_id='xxx')

        sender = PackageSender(name='Some company, s.r.o.', street='Street 20', city='Košice', zip_code='04001',
                               country_code='SK', contact='Jozef Mrkva', phone='0910xxxxxx', mail='info@company.com')
        recipient = PackageRecipient(name='Peter Customer', street='Hlavná 23', city='Košice',
                                     zip_code='04001', country_code='SK', contact='Peter Customer',
                                     mail='peter.customer@mail.me', phone='0900xxxxxx')
        order = PackageOrder(sender=sender, recipient=recipient, pick_up_date=date(2018, 11, 19), count_of_parcels=1,
                             client_reference='124', cod_amount='99', cod_reference='codref',)

        connector = GlsConnector(configuration=config)
        tracking_code = connector.print_label(order=order)
        self.assertIsNotNone(tracking_code)


if __name__ == '__main__':
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    unittest.main()