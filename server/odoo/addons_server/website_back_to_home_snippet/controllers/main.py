# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ctypes import sizeof
from http import client
import base64
import babel.messages.pofile
import base64
import copy
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
import math
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
from datetime import timedelta,datetime, date

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR
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
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.tools.misc import get_lang
from odoo.addons.portal.controllers.portal import CustomerPortal




_logger = logging.getLogger(__name__)
import string
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)


class WebRegisteration(AuthSignupHome):
    

    @http.route('/', type='http',  auth='public', website=True)
    def HomeBack(self,  **kw):
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

        
        return http.request.render('website_back_to_home_snippet.homeback',{'is_users':is_users})