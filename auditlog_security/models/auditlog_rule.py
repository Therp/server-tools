# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, modules, _
from odoo.addons.auditlog.models.rule import FIELDS_BLACKLIST
from odoo import SUPERUSER_ID


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    auditlog_line_access_rule_ids = fields.One2many(
        "auditlog.line.access.rule", "auditlog_rule_id", ondelete="cascade"
    )
    server_action_id = fields.Many2one('ir.actions.server', "Server Action")


    def sudo(self, user=SUPERUSER_ID):
       return super(
            AuditlogRule, self.with_context(real_user=self.env.context.get('uid'))
            ).sudo(user=user)

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

    def _get_view_log_lines_action(rule):
        rule.ensure_one()
        domain = (
            "[('log_id.model_id', '=', %s), ('log_id.res_id', '=', "
            "active_id),('field_id', 'in', %s)]"
            % (rule.model_id.id,
               rule.auditlog_line_access_rule_ids.mapped('field_ids').ids)
        )
        return  {
            "name": _("View Log Lines"),
            "res_model": "auditlog.log.line",
            "src_model": rule.model_id.model,
            "binding_model_id": rule.model_id.id,
            "domain": domain
        }

    def _create_server_action(self, rule):

        code = """
        if env.user.has_group("auditlog_security.group_can_view_audit_logs"):
            rule = env['auditlog.rule'].browse(%s)
            fields_ids = rule.auditlog_line_access_rule_ids.mapped('field_ids').ids
            logs = env['auditlog.log'].sudo().search([('model_id', '=', rule.model_id.id), ('res_id', 'in', env.context.get('active_ids'))])
            domain = [('log_id', 'in', logs.ids), ('field_id', 'in', fields_ids)]
            action_values = env.ref('auditlog_security.audit_log_line_action').read()[0]
            action = action_values
        """ % rule.id
        server_action = self.env['ir.actions.server'].sudo().create({
            'name': "View Log Lines",
            'model_id': rule.model_id.id,
            'state': "code",
            'code': code.strip()
        })
        rule.write({
            'server_action_id': server_action.id
        })
        return server_action

    def _get_view_log_action(rule):
        #small helper , not used but may be useful.
        rule.ensure_one()
        domain = "[('model_id', '=', %s), ('res_id', '=', active_id)]" % (
            rule.model_id.id)
        return {
            'name': _("View logs"),
            'res_model': 'auditlog.log',
            'src_model': rule.model_id.model,
            'binding_model_id': rule.model_id.id,
            'domain': domain,
         }

    @api.multi
    def subscribe(self):
        for rule in self:
            server_action = self._create_server_action(rule)
            server_action.create_action()
        return super(AuditlogRule, self).subscribe()

    @api.multi
    def unsubscribe(self):
        for rule in self:
            rule.server_action_id.unlink()
        return super(AuditlogRule, self).unsubscribe()

    def _prepare_log_line_vals_on_read(self, log, field, read_values):
        res = super(AuditlogRule, self)._prepare_log_line_vals_on_read(
            log, field, read_values)
        res.update({'user_id': self.env.context.get('real_user')})
        return res

    def _prepare_log_line_vals_on_write(
            self, log, field, old_values, new_values):
        res = super(AuditlogRule, self)._prepare_log_line_vals_on_write(
            log, field, old_values, new_values)
        res.update({'user_id': self.env.context.get('real_user')})
        return res

    def _prepare_log_line_vals_on_create(self, log, field, new_values):
        res = super(AuditlogRule, self)._prepare_log_line_vals_on_create(
            log, field, new_values)
        res.update({'user_id': self.env.context.get('real_user')})
        return res

