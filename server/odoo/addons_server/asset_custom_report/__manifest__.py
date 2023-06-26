# Copyright 2015 Antiun Ingeniería, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Asset custom report",
    "summary": "Reports for asset value during a period of time with associated user",
    "version": "1.0",
    "category": "report",
    "author": "Tria trading  - Natnael lemma",
    "sequence": 0,
    "application": True,
    "depends": ["purchase","account_asset_management"],
   # "external_dependencies": {"python": ["wkhtmltopdf"]},
    "data": [
        'security/ir.model.access.csv',
        "views/report_template.xml",
        "report/asset_report.xml",
        "views/account_asset_deprication_value.xml",
    ],
    "installable": True,
}
