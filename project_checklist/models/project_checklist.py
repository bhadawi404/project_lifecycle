from odoo import models, fields, api, _


class ProjectChecklist(models.Model):
    _name = 'project.checklist'
    _description =  'Project Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Checklist Name', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade', index=True, tracking=True)
    # scope_type defines what this checklist is primarily for
    scope_type = fields.Selection([
        ('project_phase', 'Project Phase'),
        ('project_page', 'Project Page'),
        ('task', 'Task'),
        ('employee', 'Employee'),
    ], string='Scope Type', default='project_phase', required=True)
    # dynamic reference to the actual record (project/task/employee/...); optional
    scope_ref = fields.Reference([
        ('project.project', 'Project'),
        ('project.task', 'Task'),
        ('hr.employee', 'Employee'),
    ], string='Scope Reference', help='Reference to the target record for this checklist')
    phase_id = fields.Many2one('project.phase', string='Phase (optional)')  # project.phase may be custom; optional
    line_ids = fields.One2many('project.checklist.line', 'checklist_id', string='Lines', cascade=True)
    active = fields.Boolean(default=True)
    progress = fields.Float(string='Progress (%)', compute='_compute_progress', store=False)
    note = fields.Text('Notes')

    @api.depends('line_ids.status')
    def _compute_progress(self):
        for rec in self:
            lines = rec.line_ids.filtered(lambda l: l.status != 'n/a')
            total = len(lines)
            done = len(lines.filtered(lambda l: l.status == 'done'))
            rec.progress = (done / total * 100.0) if total else 0.0


    
    