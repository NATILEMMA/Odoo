from . import controllers
from . import models

# from . import wizard

import logging
_logger = logging.getLogger(__name__)

def init(self):
    """
    This method defines the initial setup for the module.
    `cr`: Database Cursor
    `registry`: Odoo registry instance
    """

    _logger.info("##################kkkkkkkkkkkkkkkkkkkkkkkkk#####################")
    # gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
    # ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
    # users = self.env['res.users'].search([])
    
    # _logger.info("----------- Gregory %s",gro_groups)
    # _logger.info("----------- ethio_groups %s",ethio_groups)
    # _logger.info("----------- users %s",users)
    pass



# def init_hook(cr, registry):
#     """
#     This method defines the initial setup for the module.
#     `cr`: Database Cursor
#     `registry`: Odoo registry instance
#     """

#     _logger.info("##################init_hook#####################")

    # Perform any setup or configuration here.
    # For example, you might create a new database table, 
    # or import some data from a CSV file.

    # Make sure to commit any database changes.
    # cr.commit()