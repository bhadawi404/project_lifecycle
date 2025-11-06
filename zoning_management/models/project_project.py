from odoo import models, fields, api, _
class ProjectProject(models.Model):
    _inherit = 'project.project'

    zoning_analysis_ids = fields.One2many('project.zoning.analysis', 'project_id', string='Zoning Analyses')
