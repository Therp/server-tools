# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, modules, _
from odoo.addons.auditlog.models.rule import FIELDS_BLACKLIST


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    auditlog_line_access_rule_ids = fields.One2many(
        "auditlog.line.access.rule", "auditlog_rule_id", ondelete="cascade"
    )
    server_action_id = fields.Many2one('ir.actions.server', "Server Action",)

    @api.onchange("model_id")
    def onchange_model_id(self):
        # if model changes we must wipe out all field ids
        self.auditlog_line_access_rule_ids.unlink()

    @api.model
    def _get_view_log_lines_action(self, model_id):
        lines = self.env['auditlog.log.line'].search([
            ('model_id', '=', model_id),
            ('res_id', 'in', self.env.context.get('active_ids'))
            ])
        return {
                "name": _("View Log Lines"),
                "res_model": "auditlog.log.line",
                "view_mode": "tree,form",
                #"src_model": self.model_id.model,
                #"binding_model_id": self.model_id.id,
                "view_id": False,
                "domain": [('id', 'in', lines.ids)],
                "type": "ir.actions.act_window",
                }

    @api.multi
    def _create_server_action(self):
        self.ensure_one()
        code = "action = env['auditlog.rule']._get_view_log_lines_action(%s)" % (
            self.model_id.id,)
        server_action = self.env['ir.actions.server'].sudo().create({
            'name': "View Log Lines",
            'model_id': self.model_id.id,
            'state': "code",
            'code': code
        })
        self.write({
            'server_action_id': server_action.id
        })
        return server_action

    @api.multi
    def subscribe(self):
        for rule in self:
            server_action = rule._create_server_action()
            server_action.create_action()
        res = super(AuditlogRule, self).subscribe()
        # rule now will have "View Log" Action, make that visible only for admin
        if res:
            self.action_id.write({
                'groups_id': [(6, 0, [self.env.ref('base.group_system').id])]
            }) 
        return res

    @api.multi
    def unsubscribe(self):
        for rule in self:
            rule.server_action_id.unlink()
        return super(AuditlogRule, self).unsubscribe()

