# Copyright 2025 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AuditlogLog(models.Model):
    _inherit = "auditlog.log"

    rule_id = fields.Many2one("auditlog.rule", compute="_compute_rule_id", store=True)
    allowed_group_ids = fields.Many2many(
        "res.groups", compute="_compute_allowed_group_ids", store=True
    )

    @api.depends("model_id")
    def _compute_rule_id(self):
        for log in self:
            log.rule_id = self.env["auditlog.rule"].search(
                [("model_id", "=", log.model_id.id)]
            )

    @api.depends("rule_id")
    def _compute_allowed_group_ids(self):
        for log in self:
            log.allowed_group_ids = (
                self.env["auditlog.line.access.rule"]
                .search([("auditlog_rule_id", "=", log.rule_id.id)])
                .group_ids
            )
