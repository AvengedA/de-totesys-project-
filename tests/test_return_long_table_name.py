import pytest
from unittest.mock import patch, Mock
from src.First_util_for_3rd_lambda import return_long_table_name
                                          

def test_return_long_table_name_returns_sales_order():
    # arrange:
    expected = 'facts_sales_order'

    # act:
    result = return_long_table_name('sales_order')
    
    # assert:
    assert result == expected





def test_return_long_table_name_returns_returns_staff():
    # arrange:
    expected = 'dim_staff'

    # act:
    result = return_long_table_name('staff')
    
    # assert:
    assert result == expected
    




def test_return_long_table_name_returns_location():
    # arrange:
    expected = 'dim_location'

    # act:
    result = return_long_table_name('location')
    
    # assert:
    assert result == expected



def test_return_long_table_name_returns_date():
    # arrange:
    expected = 'dim_date'

    # act:
    result = return_long_table_name('date')
    
    # assert:
    assert result == expected





def test_return_long_table_name_returns_currency():
    # arrange:
    expected = 'dim_currency'

    # act:
    result = return_long_table_name('currency')
    
    # assert:
    assert result == expected




def test_return_long_table_name_returns_counterparty():
    # arrange:
    expected = 'dim_counterparty'

    # act:
    result = return_long_table_name('counterparty')
    
    # assert:
    assert result == expected

