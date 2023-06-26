
from ctypes import sizeof
from http import client
import base64
import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import pprint
import operator
import os
import re
import sys
import tempfile
# from numpy import True_

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from lxml import etree
import unicodedata
from datetime import timedelta,datetime

from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.event.controllers.main import EventController
from odoo.http import request
from odoo.osv import expression
from odoo.tools.misc import get_lang, format_date


import werkzeug
from werkzeug.datastructures import OrderedMultiDict
from werkzeug.exceptions import NotFound

from ast import literal_eval
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import odoo
from odoo.addons.base.models.res_partner import Partner
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.osv.expression import OR



_logger = logging.getLogger(__name__)
import string
# import africastalking



class WebRegisteration(AuthSignupHome):
    
    
    @http.route('/success', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.redirect('/shop')


    @http.route('/', type='http',  auth='public', website=True)
    def home(self,  **kw):
        _logger.info("@@@@@@@@@@@@")
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        is_users = []
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")
        company = request.env['res.company'].sudo().search([])
        return http.request.render('AADBO_website.Home',{'is_users': is_users})
        
    @http.route('/home', type='http',  auth='public', website=True)
    def home1(self,  **kw):
        _logger.info("@@@@@@@@@@@@")
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        is_users = []
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")
        company = request.env['res.company'].sudo().search([])
        return http.request.render('AADBO_website.Home',{'is_users':is_users})
    

    @http.route('/registrations', type='http', auth='public', website=True)
    def register(self, **post):
        """This function will create supporters from portal"""
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        is_users = []
        if not users:
            is_users.append("False")
        else:
            is_users.append("True")
        if post and request.httprequest.method == 'POST':
            values = {}
            values.update(post)
            for field in set(['subcity_id', 'wereda_id', 'ethnic_group', 'education_level', 'field_of_study_id']) & set(values.keys()):
                try:
                    values[field] = int(values[field])
                except:
                    values[field] = False
            name = values['first_name'] + ' ' + values['fathers_name'] + ' ' + values['grandfathers_name']
            values['name'] = name
            values.pop('first_name') 
            values.pop('fathers_name')
            values.pop('grandfathers_name')
            values.pop('livelihood')

            year = request.env['fiscal.year'].search([('state', '=', 'active')])
            if not year:
                return request.render('AADBO_website.year_error', {'is_users': is_users})
            plan_city = request.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
            if not plan_city:
                return request.render('AADBO_website.plan_city_error', {'is_users': is_users})
            plan_subcity = request.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('subcity_id', '=', values['subcity_id'])])
            if not plan_subcity:
                return request.render('AADBO_website.plan_sub_city_error', {'is_users': is_users}) 
            plan_woreda = request.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('wereda_id', '=', values['wereda_id'])])
            if not plan_woreda:
                return request.render('AADBO_website.plan_wereda_error', {'is_users': is_users})

            if values['user_input']:
                request.env['user.input'].sudo().create({
                    'model': "Field of Study",
                    'user_input': values['user_input']
                })
                values['is_user_input'] = 'True'
            if int(values['age']) == 0:
                return request.render('AADBO_website.wrong_age_error', {'is_users': is_users})
            if int(values['age']) < 15:
                return request.render('AADBO_website.age_error', {'is_users': is_users})
            if values['image_1920']:
                values['image_1920'] = values['image_1920'].read()
                values['image_1920'] = base64.b64encode(values['image_1920'])
                values['work_place'] = values['company_name']
                values.pop('company_name')
                request.env['supporter.members'].sudo().create(values)
                return request.render('AADBO_website.registration_end')                                       
            else:
                values['work_place'] = values['company_name']
                values.pop('company_name')
                request.env['supporter.members'].sudo().create(values)
                return request.render('AADBO_website.registration_end')  
        cities = request.env['res.country.state'].sudo().search([('country_id', '=', 69)])
        ed_levels = request.env['res.edlevel'].sudo().search([])
        studies = request.env['field.study'].sudo().search([])
        ethnicity = request.env['ethnic.groups'].sudo().search([])
        subcities = request.env['membership.handlers.parent'].sudo().search([])
        weredas = request.env['membership.handlers.branch'].sudo().search([])
        return request.render("AADBO_website.registration_form", {
                                                                    'ed_levels': ed_levels,
                                                                    'cities': cities,
                                                                    'subcities': subcities,
                                                                    'weredas': weredas,
                                                                    'ethnicity': ethnicity,
                                                                    'is_users': is_users,
                                                                    'studies': studies
                                                                })
