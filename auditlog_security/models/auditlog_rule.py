# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions, models, fields, api, modules, _, tools
from odoo.addons.auditlog.models.rule import FIELDS_BLACKLIST
from odoo.exceptions import ValidationError, UserError

class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    auditlog_line_access_rule_ids = fields.One2many(
        "auditlog.line.access.rule", "auditlog_rule_id", ondelete="cascade"
    )
    server_action_id = fields.Many2one('ir.actions.server', "Server Action",)
    log_selected_fields_only = fields.Boolean(
        default=True,
        help="Log only the selected fields, to save space avoid large DB data.")

    @api.constrains('model_id')
    def unique_model(self):
        if self.search_count([('model_id', '=', self.model_id.id)]) > 1:
            raise ValidationError("A rule for this model already exists")

    @api.model
    def get_auditlog_fields(self, model):
        res = super(AuditlogRule, self).get_auditlog_fields(model)
        unique_rule = self._get_rule_for_model(model)
        if unique_rule.log_selected_fields_only:
            traced_fields = unique_rule._get_fields_of_rule()
            # we re-use the checks on non-stored fields from super.
            return [x for x in traced_fields if x in res]
        return res

    @api.multi
    def write(self, values):
        cache_invalidating_fields = [
                "auditlog_line_access_rule_ids" ,
                "log_selected_fields_only",
        ]
        if any([field in values.keys() for field in cache_invalidating_fields]):
            # clear cache for all ormcache methods.
            self.clear_caches()
        return super(AuditlogRule, self).write(values)

    @api.onchange("model_id")
    def onchange_model_id(self):
        # if model changes we must wipe out all field ids
        self.auditlog_line_access_rule_ids.unlink()

    @tools.ormcache('model')
    def _get_rule_for_model(self, model):
        unique_rule =  self.env['auditlog.rule'].sudo().search(
            [('model_id.model', '=', model._name)])
        return unique_rule.sudo()

    @tools.ormcache('rule')
    def _get_fields_of_rule(rule):
        if rule.auditlog_line_access_rule_ids:
            return rule.mapped(
                    'auditlog_line_access_rule_ids.field_ids').ids
        return []

    @api.model
    def _get_view_log_lines_action(self, rule_id=None):
        rule = self.sudo().browse(rule_id)
        domain = [
            ('model_id', '=', rule.model_id.id),
            ('res_id', 'in', self.env.context.get('active_ids')),
        ]
        field_ids =  rule._get_fields_of_rule() 
        if field_ids:
            domain.append(('field_id', 'in', field_ids))
        lines = self.env['auditlog.log.line'].search(domain)
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
        code = \
            "action =env['auditlog.rule']._get_view_log_lines_action(rule_id=%s)" % (self.id)
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

