import json
from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    checklist_ids = fields.One2many('project.task.checklist', 'task_id', string='Checklist')
