# Copyright 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AuditlogLog(models.Model):
    _name = 'auditlog.log'
    _description = "Auditlog - Log"
    _order = "create_date desc"

    name = fields.Char("Resource Name", size=64)
    model_id = fields.Many2one(
        "ir.model", string="Model", index=True,
        required=True
    )
    model_name = fields.Char(readonly=True,  related='model_id.name' )
    model_model = fields.Char(string="Technical Model Name", readonly=True,
            related="model_id.model"
    )
    res_id = fields.Integer("Resource ID")
    user_id = fields.Many2one(
        'res.users', string="User")
    method = fields.Char("Method", size=64)
    line_ids = fields.One2many(
        'auditlog.log.line', 'log_id', string="Fields updated")
    http_session_id = fields.Many2one(
        'auditlog.http.session', string="Session")
    http_request_id = fields.Many2one(
        'auditlog.http.request', string="HTTP Request")
    log_type = fields.Selection(
        [('full', "Full log"),
         ('fast', "Fast log"),
         ],
        string="Type")


class AuditlogLogLine(models.Model):
    _name = 'auditlog.log.line'
    _description = "Auditlog - Log details (fields updated)"

    field_id = fields.Many2one(
        "ir.model.fields", ondelete="set null", string="Field", index=True,
        required=True
    )
    log_id = fields.Many2one(
        'auditlog.log', string="Log", ondelete='cascade', index=True)
    old_value = fields.Text("Old Value")
    new_value = fields.Text("New Value")
    old_value_text = fields.Text("Old value Text")
    new_value_text = fields.Text("New value Text")
    field_name = fields.Char("Technical name", related='field_id.name')
    field_description = fields.Char(
        "Description", related='field_id.field_description')
