from odoo import models, fields, api, _

class ProjectChecklist(models.Model):
    _name = 'project.checklist'
    _description =  'Project Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Checklist Name', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade', index=True, tracking=True, required=True)
    employee_id = fields.Many2one('hr.employee', string='Owner', help='Owner of this checklist (visibility)')
    # shared lines
    line_ids = fields.Many2many(
        'project.checklist.line',
        'checklist_line_rel',
        'checklist_id',
        'line_id',
        string='Lines'
    )
    note = fields.Text('Notes')
    active = fields.Boolean(default=True)

    # Compute employees & tasks based on lines
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Assigned Employees',
        compute='_compute_employee_ids'
    )
    task_ids = fields.Many2many(
        'project.task',
        string='Associated Tasks',
        compute='_compute_task_ids'
    )

    @api.depends('line_ids.assoc_employee_ids')
    def _compute_employee_ids(self):
        for rec in self:
            rec.employee_ids = rec.line_ids.mapped('assoc_employee_ids')

    @api.depends('line_ids.assoc_task_ids')
    def _compute_task_ids(self):
        for rec in self:
            rec.task_ids = rec.line_ids.mapped('assoc_task_ids')
    
    