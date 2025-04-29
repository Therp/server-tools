# Copyright 2021-2024 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    allowed_group_ids = fields.Many2many("res.groups", string="Allowed Groups")
    server_action_id = fields.Many2one(
        "ir.actions.server",
        "Server Action",
    )
    log_selected_fields_only = fields.Boolean(
        default=True,
        help="Log only the selected fields, to save space avoid large DB data.",
    )

    @api.constrains("model_id")
    def unique_model(self):
        if self.search_count([("model_id", "=", self.model_id.id)]) > 1:
            raise ValidationError(_("A rule for this model already exists"))

    def write(self, values):
        if "state" in values.keys():
            self.clear_caches()
        return super().write(values)

    @api.onchange("model_id")
    def onchange_model_id(self):
        # if model changes we must wipe out all field ids
        self.auditlog_line_access_rule_ids.unlink()

    @api.model
    def _get_view_log_lines_action(self):
        assert self.env.context.get("active_model")
        assert self.env.context.get("active_ids")
        model = (
            self.env["ir.model"]
            .sudo()
            .search([("model", "=", self.env.context.get("active_model"))])
        )
        domain = [
            ("model_id", "=", model.id),
            ("res_id", "in", self.env.context.get("active_ids")),
        ]
        return {
            "name": _("View Log Lines"),
            "res_model": "auditlog.log.line",
            "view_mode": "tree,form",
            "view_id": False,
            "domain": domain,
            "type": "ir.actions.act_window",
        }

    def _create_server_action(self):
        self.ensure_one()
        code = "action = env['auditlog.rule']._get_view_log_lines_action()"
        server_action = (
            self.env["ir.actions.server"]
            .sudo()
            .create(
                {
                    "name": "View Log Lines",
                    "model_id": self.model_id.id,
                    "state": "code",
                    "code": code,
                }
            )
        )
        self.write({"server_action_id": server_action.id})
        return server_action

    def subscribe(self):
        for rule in self:
            server_action = rule._create_server_action()
            server_action.create_action()
        res = super(AuditlogRule, self).subscribe()
        # rule now will have "View Log" Action, make that visible only for admin
        if res:
            self.action_id.write(
                {"groups_id": [(6, 0, [self.env.ref("base.group_system").id])]}
            )
        return res

    def unsubscribe(self):
        for rule in self:
            rule.server_action_id.unlink()
        return super(AuditlogRule, self).unsubscribe()
