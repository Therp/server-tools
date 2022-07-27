# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api


class AuditlogAutovacuum(models.TransientModel):
    _inherit = "auditlog.autovacuum"

    @api.model
    def autovacuum(self, days):
        return super(
            AuditlogAutovacuum, self.with_context(auditlog_write=True)
        ).autovacuum(days=days)