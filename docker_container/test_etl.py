import unittest
from unittest.mock import patch
import os
import datetime
import module
import pandas as pd

initial_outcome = 'R$ 300.000,00'
investment_day = '26/06/2020'

 
class TestETL(unittest.TestCase):

    def setUp(self):
        assets = module.import_csv('Ativos.csv', [0, 1, 2])
        initial_outcome_val_exp = 300000
        investment_day_date_exp = datetime.date(2020, 6, 26)
        initial_outcome_val = module.str_to_float(initial_outcome)
        investment_day_date = module.str_to_date(investment_day)
        cf = module.cash_flow(initial_outcome_val, investment_day_date, assets)
        cf.remove(cf[0])  # To remove header from cf list
        self.expected = ['Ativo', 'preco', 'vencimento']
        self.result = assets[0]
        self.initial_outcome_result = module.str_to_float(initial_outcome)
        self.investment_day = investment_day
        self.cf_1st_row_expected = ['Initial Outcome', -1*initial_outcome_val_exp, investment_day_date_exp]
        self.cf_1st_row_result = cf[0]

    def test_csv_filename(self):
        filename = os.path.join(os.path.dirname(__file__), 'Ativos.csv')
        pd.read_csv(filename)

    def test_list_eq(self):
        self.assertListEqual(self.result, self.expected)  # Both lists with headers itens and order should match

    def test_initial_outcome(self):
        assert self.initial_outcome_result >= 0
        assert self.initial_outcome_result == 300000

    def test_date_format(self):     # Testing exceptions
        with self.assertRaises(ValueError):
            module.str_to_date('06/26/2020')

    def test_str_to_float(self):
        with self.assertRaises(ValueError):
            module.str_to_float('300,000.00')

    def test_calculate_irr(self):
        # Both lists 1st rows itens and order should match
        self.assertListEqual(self.cf_1st_row_result, self.cf_1st_row_expected)

    # def test_request_bcb(self):
    #
    #     """Function to test BACEN's API availability to request Selic rate values from public service."""
    #
    #     with patch('module.requests.get') as mocked_get:
    #         mocked_get.return_value.ok = True
    #         mocked_get.return_value.text = 'Success'
    #
    #         imported_data = self.investment.module.request_bcb(11, 1, None, None)
    #         mocked_get.assert_called_with('http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json')
    #         self.assertEqual(imported_data, 'Success')
    #
    #         # mocked_get.return_value.ok = True
    #         # mocked_get.return_value.text = 'Success'


if __name__ == '__main__':
    unittest.main()
