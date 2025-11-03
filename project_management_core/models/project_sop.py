from odoo import models, fields

class ProjectSOP(models.Model):
    _name = 'project.sop'
    _rec_name = 'name'

    name = fields.Char('Name',required=True)
    project_type_id = fields.Many2one('project.type', string='Project Type', required=True)
    description = fields.Text('Description')
    phase_id = fields.Many2one('project.phase', string='Phase')
    active = fields.Boolean(default=True)
    checklist_template_ids = fields.One2many('project.sop.checklist', 'sop_id', string="Checklist Template")

