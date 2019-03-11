# -*- coding: utf-8 -*-
# Copyright 2018 Wolfgang Pichler, Callino <wpichler@callino.at>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.addons.website.models.website import slug
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = ["product.template"]

    def write(self, vals):
        result = super(ProductTemplate, self).write(vals)
        if 'name' not in vals:
            return result
        for product in self:
            redirection = self.env['website.seo.redirection'].search(
                [('origin', '=', "/shop/product/%s" % slug(product))])
            if redirection:
                redirection.origin = "/shop/product/%s" %\
                                     slug((product.id, vals['name']))
        return result

    @api.multi
    def _compute_website_url(self):
        super(ProductTemplate, self)._compute_website_url()
        for product in self:
            redirection = self.env['website.seo.redirection'].search([
                ('origin', '=', "/shop/product/%s" % slug(product))
            ])
            if redirection:
                product.website_url = redirection.destination
            else:
                product.website_url = "/shop/product/%s" % slug(product)

    @api.multi
    def _compute_website_seo_redirections(self):
        for product in self:
            product.website_redirection_ids = self.env['website.seo.redirection'].search([
                ('origin', '=ilike', "/shop/product/%"),
                ('origin', '=ilike', "%-" + str(product.id)),
            ])

    def fix_redirections(self):
        # Get all published products
        products = self.search([('website_published', '=', True)])
        for product in products:
            website_redirection_ids = self.env['website.seo.redirection'].search([
                ('origin', '=ilike', "/shop/product/%"),
                ('origin', '=ilike', "%-" + str(product.id)),
            ])
            website_url = "/shop/product/%s" % slug(product)
            for redirection in website_redirection_ids:
                if website_url != redirection.origin:
                    existing_redirection_ids = self.env['website.seo.redirection'].search([
                        ('origin', '=', website_url)
                    ])
                    if not existing_redirection_ids:
                        redirection.origin = website_url
                    else:
                        _logger.info("Existing redirection id on %s", product.name)


    website_redirection_ids = fields.Many2many('website.seo.redirection', compute='_compute_website_seo_redirections', string='SEO Links')
