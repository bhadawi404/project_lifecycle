from odoo import models, fields, api, _


class ZoningAnalysis(models.Model):
    _name = 'project.zoning.analysis'
    _description =  'Zoning Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
    line_ids = fields.One2many('project.zoning.analysis.line', 'analysis_id', string='Zoning Lines')


    
    