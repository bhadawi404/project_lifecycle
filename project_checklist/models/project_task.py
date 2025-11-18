from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    checklist_ids = fields.Many2many('project.checklist','task_checklist_rel','task_id','checklist_id',string='Checklists')
    checklist_line_ids = fields.Many2many('project.checklist.line','task_checklist_line_rel','task_id','line_id',string='Checklist Lines')
