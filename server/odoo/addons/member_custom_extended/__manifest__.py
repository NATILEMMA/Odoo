
{
    "name": "Members custom extended",
    "summary": "Extention on members custom module it contains cell split for league and members ...",
    "version": "1.0",
    "category": "membership",
    "author": "Tria trading -  Natnael Lemma ,Software developer",
    "sequence": 0,
    "application": True,
    "depends": ["members_custom"],
    "data": [
        'security/ir.model.access.csv',
        "wizard/cell_split_wizard_view.xml",
        "wizard/league_cell_split_wizard_view.xml",
        "views/office_in_membership.xml",
    ],
    "installable": True,
}
