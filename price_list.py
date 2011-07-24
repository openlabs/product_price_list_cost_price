# -*- coding: utf-8 -*-
"""
    Product Price List

    :copyright: (c) 2011 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details.
"""
from decimal import Decimal
from trytond.model import ModelView, ModelSQL
from trytond.transaction import Transaction


class PriceList(ModelSQL, ModelView):
    'Price List'
    _name = 'product.price_list'

    def _get_context_price_list_line(self, party, product, unit_price,
            quantity, uom):
        '''
        Add cost_price of the product to price list context

        :param party: the BrowseRecord of the party.party
        :param product: the BrowseRecord of the product.product
        :param unit_price: a Decimal for the default unit price in the
            company's currency and default uom of the product
        :param quantity: the quantity of product
        :param uom: the BrowseRecord of the product.uom
        :return: a dictionary
        '''
        product_obj = self.pool.get('product.product')
        res = super(PriceList, self)._get_context_price_list_line(
            party, product, unit_price, quantity, uom)

        res['cost_price'] = Decimal('0.0')
        if product:
            res['cost_price'] = product.get_cost_price(product)

        return res

PriceList()


class Product(ModelSQL, ModelView):
    'Product'
    _name = 'product.product'

    def get_cost_price(self, product):
        """Returns the validated cost_price against uom, currency and quantity

        :param product: Browse Record of product
        :return: Cost Price of the product
        """
        uom_obj = self.pool.get('product.uom')
        user_obj = self.pool.get('res.user')
        currency_obj = self.pool.get('currency.currency')
        date_obj = self.pool.get('ir.date')

        today = date_obj.today()

        cost_price = product.cost_price

        if Transaction().context.get('uom'):
            uom = uom_obj.browse(Transaction().context.get('uom'))

        currency = None
        if Transaction().context.get('currency'):
            currency = currency_obj.browse(
                    Transaction().context.get('currency'))

        user = user_obj.browse(Transaction().user)

        if uom:
            cost_price = uom_obj.compute_price(
                    product.default_uom, cost_price, uom)
        if currency and user.company:
            if user.company.currency.id != currency.id:
                date = Transaction().context.get('sale_date') or today
                with Transaction().set_context(date=date):
                    cost_price = currency_obj.compute(
                            user.company.currency.id, cost_price,
                            currency.id)
        return cost_price

Product()
