# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, _


class IrRule(models.Model):
    _inherit = "ir.rule"

    auditlog_line_access_rule_id = fields.Many2one(
        "auditlog.line.access.rule",
        required=False,
        index=True,
        ondelete='cascade',
        help="Auditlog line access Rule that generated this ir.rule",
    )

    @api.model
    def create(self, values):
        if values.get("model_id") == self.env.ref(
            "auditlog.model_auditlog_log_line"
        ).id and not self.env.context.get("auditlog_write"):
            raise exceptions.ValidationError(
                _(
                    """
                 Auditlog line rules are automatically generated from the  
                 auditlog interface, please use that to create"""
                )
            )
        return super(IrRule, self).create(values)

    @api.multi
    def write(self, vals):
        if "auditlog_id" in vals and not self.env.context.get("auditlog_write"):
            raise exceptions.ValidationError(
                _("""Cannot change auditlog_line_access_rule""")
            )
        return super(IrRule, self).write(vals)

    @api.multi
    def unlink(self):
        auditlog_write = self.env.context.get("auditlog_write")
        for this in self:
            if this.auditlog_line_access_rule_id and not auditlog_write:
                raise exceptions.ValidationError(
                    _(
                        """
                 Auditlog line rules are automatically generated from the  
                 auditlog interface, please use that to delete"""
                    )
                )
        return super(IrRule, self).unlink()
