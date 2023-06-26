# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Web Translate Dialog",
    "summary": "Easy-to-use pop-up to translate fields in several languages",
    "version": "13.0.1.1.0",
    "category": "Web",
    "website": "http://triaplc.com",
    "author": "Camptocamp, Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["web"],
    "data": ["views/res_lang.xml", "views/web_translate.xml"],
    "qweb": ["static/src/xml/base.xml"],
}
