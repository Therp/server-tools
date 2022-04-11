# Copyright 2021 Therp B.V. <https://www.therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Audit Log Permissions",
    "version": "11.0.1.0.1",
    "author": "Therp B.V.,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools/",
    "category": "Tools",
    "depends": [
        "auditlog",
        "contacts",
    ],
    "data": [
        "demo/auditlog_rule.xml",
        "views/auditlog_view.xml",
    ],
    "application": True,
    "installable": True,
}
