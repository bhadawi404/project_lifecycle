from odoo import models, fields, api, _


class ProjectTaskChecklist(models.Model):
    _name = 'project.task.checklist'
    _description =  'Project Checklist'

    task_id = fields.Many2one('project.task', string='Task')
    project_id = fields.Many2one('project.project', string='Project')
    name = fields.Char('Title',required=True, tracking=True)
    user_ids = fields.Many2many('res.users', string='Assignees')
    description = fields.Text('Description')
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('n/a', 'N/A')
    ], string='Status', default='todo', tracking=True)
    

    
    