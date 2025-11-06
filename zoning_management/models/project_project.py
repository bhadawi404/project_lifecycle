from odoo import models, fields, api, _
class ProjectProject(models.Model):
    _inherit = 'project.project'

    zoning_analysis_ids = fields.One2many('project.zoning.analysis', 'project_id', string='Zoning Analyses')
    current_phase = fields.Selection([
        ('sd', 'SD - Schematic Design'),
        ('dd', 'DD - Design Development'),
        ('cd', 'CD - Construction Documents'),
        ('qc', 'QC - Quality Control'),
    ], string="Phase", default='sd')
