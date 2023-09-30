from odoo import models, api, fields,exceptions
from datetime import datetime



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    request_vendor = fields.Many2one(comodel_name="res.partner", string="Request Vendor", required=True)
    contract_number = fields.Char(string= 'No. Kontrak', required=True)

    def po_btn(self):
        purchase_order_values = {
            'partner_id': self.request_vendor.id,
            'origin': self.name,
        }
        purchase_order = self.env['purchase.order'].create(purchase_order_values)
        
        for sale_line in self.order_line:
            if not self.request_vendor:
                raise exceptions.ValidationError("Silakan lengkapi Reques Vendor!!")
            elif not self.contract_number:
                raise exceptions.ValidationError("Silakan lengkapi No Kontrak!!")
            else:
                pass

            purchase_order_line_values = {
                'order_id': purchase_order.id,
                'product_id': sale_line.product_id.id,
                'product_qty': sale_line.product_uom_qty,
                'price_unit': sale_line.price_unit,
            }
            self.env['purchase.order.line'].create(purchase_order_line_values)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def action_confirm(self):
        for order in self:
            if order.contract_number:
                existing_order = self.env['sale.order'].search([
                    ('contract_number', '=', order.contract_number),
                    ('id', '!=', order.id)
                ])
                if existing_order:
                    raise exceptions.ValidationError("No Kontrak sudah pernah diinputkan sebelumnya!")
                else:
                    order.state = 'sale'
                    for delivery_order in order.picking_ids:
                        delivery_order.move_ids_without_package.write({'qty_done': delivery_order.move_ids_without_package.product_uom_qty})
                        delivery_order.button_validate()
                    invoices = order._create_invoices()
                    invoices.action_post()

        super(SaleOrder, self).action_confirm()

        return True