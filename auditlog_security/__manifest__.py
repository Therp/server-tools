# Copyright 2021 Therp B.V. <https://www.therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Audit Log User Permissions",
    "version": "11.0.1.0.0",
    "author": "Therp B.V.,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools/",
    "category": "Tools",
    "description": """Allow regular users to view Audit log lines 
                   via the form view of the relevant model""",
    "depends": [
        "auditlog",
        "contacts",
    ],
    "data": [
        "views/auditlog_view.xml",
        "security/ir.model.access.csv",
    ],
    "application": True,
    "installable": True,
}
