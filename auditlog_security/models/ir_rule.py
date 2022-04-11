# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, _


class IrRule(models.Model):
    _inherit = "ir.rule"

    auditlog_id = fields.Many2one(
        "auditlog.rule",
        required=False,
        help="Auditlog Rule that generated this ir.rule",
    )

    def prevent_rule_mod(self, vals=None):
        auditlog_write = self.env.context.get("auditlog_write")
        if "auditlog_id" in vals and not auditlog_write:
            raise exceptions.validationerror(_("""Cannot change auditlog_id"""))
        for this in self:
            if this.auditlog_id and not auditlog_write:
                raise exceptions.validationerror(
                    _(
                        """
                     auditlog line rules are automatically generated from the auditlog 
                     interface, please use that to edit/delete/"""
                    )
                )

    @api.model
    def create(self, values):
        if values.get("model_id") == self.env.ref(
            "auditlog.model_auditlog_log_line"
        ).id and not self.env.context.get("auditlog_write"):
            raise exceptions.ValidationError(
                _(
                    """
                 Auditlog line rules are automatically generated from the auditlog 
                 interface, please use that to create"""
                )
            )
        return super(IrRule, self).create(values)

    @api.multi
    def write(self, vals):
        self.prevent_rule_mod(vals)
        return super(IrRule, self).write(vals)

    @api.multi
    def unlink(self):
        self.prevent_rule_mod()
        return super(IrRule, self).unlink()
