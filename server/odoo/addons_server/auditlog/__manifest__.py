# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Tria-Odoo Audit Log",
    "version": "13.0.1.0.4",
    "author": "Amen Mesfin (Tria)",
    "license": "AGPL-3",
    "website": "triaplc.com",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/auditlog_view.xml",
        "views/http_session_view.xml",
        "views/http_request_view.xml",
    ],
    "application": True,
    "installable": True,
}
