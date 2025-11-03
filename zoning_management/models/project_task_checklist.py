from odoo import models, fields, api
import operator

class ProjectTaskChecklist(models.Model):
    _name = 'project.task.checklist'
    _description = 'Project Task Checklist'

    task_id = fields.Many2one('project.task', string='Task')
    checklist_name = fields.Char('Checklist Item')
    sop_id = fields.Many2one('project.sop', string='SOP ')
    notes = fields.Text(string="Notes")
    is_done = fields.Boolean('Is Done ?')