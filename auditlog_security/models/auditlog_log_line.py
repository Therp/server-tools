# Copyright 2022 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields


class AuditlogLogLine(models.Model):
    _inherit = 'auditlog.log.line'
    _order = "create_date desc"

    user_id = fields.Many2one(
        'res.users',
        related="log_id.user_id",
        string="User",
    )
    method = fields.Char("Method", related='log_id.method')

    
