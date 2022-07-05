# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, modules, _
from odoo.addons.auditlog.models.rule import FIELDS_BLACKLIST


class AuditlogLineAccessRule(models.Model):
    _name = "auditlog.line.access.rule"

    name = fields.Char()

    field_ids = fields.Many2many("ir.model.fields")
    group_ids = fields.Many2many(
        "res.groups",
        help="""Groups that will be allowed to see the logged fields, if left empty
                default will be all users with a login""",
    )
    model_id = fields.Many2one(
        "ir.model", related="auditlog_rule_id.model_id", readonly=True
    )
    auditlog_rule_id = fields.Many2one(
        "auditlog.rule", "auditlog_access_rule_ids", readonly=True, ondelete="cascade"
    )
    state = fields.Selection(related="auditlog_rule_id.state", readonly=True)


    def needs_rule(self):
        self.ensure_one()
        return bool(self.group_ids)

    def get_linked_rules(self):
        # return with context key so that deletion will not be forbidden
        return self.env["ir.rule"].search(
            [("auditlog_line_access_rule_id", "in", self.ids)]
        )

    def get_field_ids_domain(self):
        """note this solution will work only with a hardcoded design of models,
        because on initialization , self.model_id.id still is not defined.
        for now, to keep generality we put the filtering in the view."""
        return [
            ("model_id", "=", self.env.ref("base.model_res_partner").id),
            ("name", "not in", FIELDS_BLACKLIST),
        ]

    # def unlink(self):
    #     to_delete = self.get_linked_rules()
    #     res = super(AuditlogLineAccessRule, self).unlink()
    #     if res:
    #         res = res and to_delete.with_context(auditlog_write=True).unlink()
    #     return res

    def add_default_group_if_needed(self):
        self.ensure_one()
        res = False
        if not self.group_ids and self.field_ids:
            res = self.with_context(no_iter=True).write(
                {"group_ids": [(6, 0, [self.env.ref("base.group_user").id])]}
            )
        return res

    @api.model
    def create(self, vals):
        res = super(AuditlogLineAccessRule, self).create(vals)
        res.add_default_group_if_needed()
        if res.needs_rule():
            res.generate_rules()
        return res

    @api.multi
    def write(self, vals):
        res = super(AuditlogLineAccessRule, self).write(vals)
        for this in self:
            added = this.add_default_group_if_needed()
            if (
                any(
                    [
                        x in vals
                        for x in ("group_ids", "field_ids", "model_id", "all_fields")
                    ]
                )
                or added
            ):
                if this.needs_rule():
                    this.generate_rules()
                else:
                    this.get_linked_rules().with_context(auditlog_write=True).unlink()
        return res

    def generate_rules(self):
        old_rule = self.env["ir.rule"].search(
            [("auditlog_line_access_rule_id", "=", self.id)], limit=1
        )
        values = self._prepare_rule_values()
        if old_rule:
            old_rule.with_context(auditlog_write=True).write(values)
        else:
            self.with_context(auditlog_write=True).env["ir.rule"].create(values)

    def _prepare_rule_values(self):
        domain_force = "[" + " ('log_id.model_id' , '=', %s)," % (
            self.model_id.id
        )
        if self.field_ids:
            domain_force += "('field_id', 'in',  %s)" % (self.field_ids.ids)
        domain_force += "]"
        return {
            "name": "auditlog_extended_%s" % self.id,
            "model_id": self.env.ref("auditlog.model_auditlog_log_line").id,
            "groups": [(6, 0, self.group_ids.ids)],
            "perm_read": True,
            "domain_force": domain_force,
            "auditlog_line_access_rule_id": self.id,
        }
