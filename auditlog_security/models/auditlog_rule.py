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
                "[('log_id.model_id', '=', %s), ('log_id.res_id', '=', "
                "active_id),('field_id', 'in', %s)]"
                % (rule.model_id.id,
                   rule.auditlog_line_access_rule_ids.mapped('field_ids').ids)
            )
            vals = {
                "name": _("View log lines"),
                "res_model": "auditlog.log.line",
                "src_model": rule.model_id.model,
                "binding_model_id": rule.model_id.id,
                "domain": domain
            }
            audit_grp_sec = self.env.ref(
                'auditlog_security.group_can_view_audit_logs')
            act_window = act_window_model.sudo().create(vals)
            act_window.groups_id = audit_grp_sec
            domain = "[('model_id', '=', %s), ('res_id', '=', active_id)]" % (
                rule.model_id.id)
            pvals = {
                'name': _("View logs"),
                'res_model': 'auditlog.log',
                'src_model': rule.model_id.model,
                'binding_model_id': rule.model_id.id,
                'domain': domain,
            }
            params_view = [
                ('name', '=', pvals['name']),
                ('res_model', '=', pvals['res_model']),
                ('src_model', '=', pvals['src_model']),
                ('binding_model_id', '=', pvals['binding_model_id']),
                ('domain', '=', pvals['domain'])
            ]
            act_window_view = act_window_model.search(params_view)
            for action in act_window_view:
                action.groups_id = audit_grp_sec
            rule.write({"state": "subscribed", "action_id": act_window.id})
        return True

    @api.multi
    def unsubscribe(self):
        act_window_model = self.env["ir.actions.act_window"]
        for rule in self:
            domain = "[('model_id', '=', %s), ('res_id', '=', active_id)]" % (
                rule.model_id.id)
            vals = {
                'name': _("View logs"),
                'res_model': 'auditlog.log',
                'src_model': rule.model_id.model,
                'binding_model_id': rule.model_id.id,
                'domain': domain,
            }
            params_view = [
                ('name', '=', vals['name']),
                ('res_model', '=', vals['res_model']),
                ('src_model', '=', vals['src_model']),
                ('binding_model_id', '=', vals['binding_model_id']),
                ('domain', '=', vals['domain'])
            ]
            act_window_view = act_window_model.search(params_view)
            for action in act_window_view:
                action.unlink()
        return super(AuditlogRule, self).unsubscribe()

    def _prepare_log_line_vals_on_read(self, log, field, read_values):
        res = super(AuditlogRule, self)._prepare_log_line_vals_on_read(
            log, field, read_values)
        res.update({'user_id': self.env.user.id})
        return res

    def _prepare_log_line_vals_on_write(
            self, log, field, old_values, new_values):
        res = super(AuditlogRule, self)._prepare_log_line_vals_on_write(
            log, field, old_values, new_values)
        res.update({'user_id': self.env.user.id})
        return res

    def _prepare_log_line_vals_on_create(self, log, field, new_values):
        res = super(AuditlogRule, self)._prepare_log_line_vals_on_create(
            log, field, new_values)
        res.update({'user_id': self.env.user.id})
        return res

