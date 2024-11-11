from odoo import models, fields, api, _


class PreOrder(models.Model):
    _name = "pre.order"
    _inherit = ['portal.mixin']
    _description = "Pre Order"
    _rec_name = "partner_id"
    _order = "order_date desc"


    order_date = fields.Date(string='Pre Order Date', default=fields.Date.context_today, required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    pre_product_id = fields.Many2one('product.template', string='Pre ID', ondelete='cascade')
    product_id = fields.Many2one('product.product','Product',required=True)
    product_qty = fields.Integer(string='Quantity', digits='Product Unit of Measure',default=1.0)
    note        = fields.Char(string="Note")



    
class CancelPreOrder(models.Model):
    _name = "cancel.pre.order"
    _inherit = ['portal.mixin']
    _description = "Cancel Pre Order"
    _rec_name = "partner_id"
    _order = "date desc"


    date        = fields.Date(string='Date', default=fields.Date.context_today, required=True, readonly=True)
    partner_id  = fields.Many2one('res.partner', string='Partner')
    product_id  = fields.Many2one('product.product','Product',required=True)
    product_qty = fields.Integer(string='Quantity', digits='Product Unit of Measure')
    note        = fields.Char(string="Note")
    state       = fields.Selection([('draft', 'Draft'),('validate', 'Validate')],'Status', default='draft')


    def action_validate(self):
        self.write({'state': 'validate'})

    def action_view_preorder(self):
        for rec in self :
            action = self.env.ref('asa_website_preorder.action_preorder').read()[0]
            action['context'] = {}
            action['domain'] = [('product_id', '=', rec.product_id.id),('partner_id', '=', rec.partner_id.id)]
        return action