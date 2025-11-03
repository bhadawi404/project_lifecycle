# models/project_zoning_sheet_map.py
from odoo import models, fields

class ProjectZoningSheetMap(models.Model):
    _name = 'zoning.sheet.map'
    _description = 'Zoning Sheet Mapping'
    _order = 'sequence, id'

    name = fields.Char(string="Mapping Name", required=True)
    category = fields.Selection([
        ('height', 'Height Regulation'),
        ('area', 'FAR / Coverage'),
        ('setback', 'Setback'),
        ('environment', 'Environmental'),
        ('parking', 'Parking'),
        ('other', 'Other'),
    ], string='Snippet Category', required=True)
    sheet_code = fields.Char(string="Sheet Code", required=True, help="Code like Z01, Z02, etc.")
    description = fields.Char(string="Description")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
