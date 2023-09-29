from odoo import models, api, fields,exceptions

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    request_vendor = fields.Many2one(comodel_name="res.partner", string="Request Vendor")
    contract_number = fields.Char(string= 'No. Kontrak')

    def po_btn(self):
        purchase_order_values = {
            'partner_id': self.request_vendor.id,
            'origin': self.name,
        }
        purchase_order = self.env['purchase.order'].create(purchase_order_values)
        
        for sale_line in self.order_line:
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
        # Memeriksa apakah nomor kontrak sudah ada pada Sale Order lain dengan nomor yang sama
        for order in self:
            if order.contract_number:
                existing_order = self.env['sale.order'].search([
                    ('contract_number', '=', order.contract_number),
                    ('id', '!=', order.id)
                ])
                if existing_order:
                    raise exceptions.ValidationError("No Kontrak sudah pernah diinputkan sebelumnya!")

        # Membuat proses pengiriman (delivery) dengan status 'Done' (barang sudah terkirim)
        pickings = self.env['stock.picking']
        for order in self:
            picking_vals = {
                'picking_type_id': order.picking_policy,
                'partner_id': order.partner_shipping_id.id,
                'origin': order.name,
                'location_id': order.warehouse_id.lot_stock_id.id,
                'location_dest_id': order.partner_shipping_id.property_stock_customer.id,
                'move_lines': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                }) for line in order.order_line]
            }
            picking = pickings.create(picking_vals)
            picking.action_done()

        # Mengubah status SO menjadi 'done' (opsional)
        self.write({'state': 'done'})

        return True
    
    