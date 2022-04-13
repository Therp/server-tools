# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, modules, _
from odoo.addons.auditlog.models.rule import FIELDS_BLACKLIST


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    auditlog_line_access_rule_ids = fields.One2many(
        "auditlog.line.access.rule", "auditlog_rule_id", ondelete="cascade"
    )

    @api.onchange("model_id")
    def onchange_model_id(self):
        # if model changes we must wipe out all field ids
        self.auditlog_line_access_rule_ids.unlink()

    @api.multi
    def unlink(self):
        lines = self.mapped("auditlog_line_access_rule_ids")
        res = super(AuditlogRule, self).unlink()
        if res:
            lines.unlink()
        return res

    @api.multi
    def subscribe(self):
        super(AuditlogRule, self).subscribe()
        act_window_model = self.env["ir.actions.act_window"]
        for rule in self:
            domain = (
                "[('log_id.model_id', '=', %s), ('log_id.res_id', '=', active_id)]"
                % (rule.model_id.id)
            )
            vals = {
                "name": _("View log lines"),
                "res_model": "auditlog.log.line",
                "src_model": rule.model_id.model,
                "binding_model_id": rule.model_id.id,
                "domain": domain,
            }
            act_window = act_window_model.sudo().create(vals)
            rule.write({"state": "subscribed", "action_id": act_window.id})
        return True
