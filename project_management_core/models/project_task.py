from odoo import models, fields, api

class ProjectTaskBase(models.Model):
    _inherit = 'project.task'

    phase_id = fields.Many2one('project.phase', string='Phase')