# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, modules, _
from odoo.addons.auditlog.models.rule import FIELDS_BLACKLIST


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    field_ids = fields.Many2many(
        "ir.model.fields",
        required=True,
    )
    group_ids = fields.Many2many(
        "res.groups",
        string="Groups",
        help="""Groups that will be allowed to see the logged fields, if left empty 
                all groups will be allowed (global rule creation)""",
    )

    """ note this solution will work only with a hardcoded design of models,
    because on initialization , self.model_id.id still is not defined.
    for now, to keep generality we put the filtering in the view."""

    def get_field_ids_domain(self):
        return [
            ("model_id", "=", self.env.ref("base.model_res_partner").id),
            ("name", "not in", FIELDS_BLACKLIST),
        ]

    def unlink(self):
        # if we delete auditlog rule, corresponding ir.rules are removed
        # TODO PROPOSAL: a warning here with detailed information?
        res = super(AuditlogRule, self).unlink()
        return (
            res
            and self.env["ir.rule"]
            .with_context(auditlog_write=True)
            .search([("auditlog_id", "in", self.ids)])
            .unlink()
        )

    @api.multi
    def write(self, vals):
        res = super(AuditlogRule, self).write(vals)
        for this in self:
            if any([x in vals for x in ("group_ids", "field_ids", "model_id")]):
                this.generate_rules()
        return res

    def generate_rules(self):
        old_rule = self.env["ir.rule"].search([("auditlog_id", "=", self.id)], limit=1)
        domain_force = (
            "[ "
            + " ('log_id.model_id' , '=', %s)," % (self.model_id.id)
            + "('field_id', 'in',  %s)" % (self.field_ids.ids)
            + "]"
        )
        values = {
            "name": "auditlog_extended_%s" % self.id,
            "model_id": self.env.ref("auditlog.model_auditlog_log_line").id,
            "groups": [(6, 0, self.group_ids.ids)],
            "perm_read": True,
            "domain_force": domain_force,
            "auditlog_id": self.id,
        }
        if old_rule:
            old_rule.with_context(auditlog_write=True).write(values)
        else:
            self.with_context(auditlog_write=True).env["ir.rule"].create(values)
