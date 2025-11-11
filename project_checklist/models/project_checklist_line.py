from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectChecklistLine(models.Model):
    _name = 'project.checklist.line'
    _description = 'Project Checklist Line'
    _inherit = ['mail.thread']
    _order = 'id'

    checklist_id = fields.Many2one('project.checklist', string='Checklist', ondelete='cascade', index=True, required=True)
    name = fields.Char(string='Line Title', required=True, tracking=True)
    description = fields.Text(string='Description')
    code = fields.Char(string='Code', help='Optional unique code per project')
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('n/a', 'N/A')
    ], string='Status', default='todo', tracking=True)
    is_confirmed = fields.Boolean(string='Confirmed', default=False)
    completed_by = fields.Many2one('res.users', string='Completed By')
    completed_on = fields.Datetime(string='Completed On')
    # Associations
    assoc_phase_ids = fields.Many2many('project.phase', string='Associated Phases')
    assoc_employee_ids = fields.Many2many('hr.employee', string='Associated Employees')
    assoc_task_ids = fields.Many2many('project.task', 'checklist_line_task_rel', 'cll_id', 'task_id', string='Associated Tasks')
    # assoc_page_ids = fields.Many2many('project.page', string='Associated Pages')  # project.page could be custom
    # Reuse linking
    linked_checklist_id = fields.Many2one('project.checklist', string='Linked Checklist')
    linked_cll_ids = fields.Many2many('project.checklist.line', 'checklist_line_link_rel', 'cll_id', 'linked_id', string='Linked Lines')
    rule_ids = fields.One2many('project.checklist.rule', 'line_id', string='Rules')
    sequence = fields.Integer(string='Sequence', default=1)
    number = fields.Integer(string='#', compute='_compute_sequence_number')


    @api.depends('checklist_id.line_ids.sequence')
    def _compute_sequence_number(self):
        checklists = self.mapped('checklist_id')
        for checklist in checklists:
            sorted_lines = checklist.line_ids.sorted(key=lambda x: x.sequence)
            for idx, line in enumerate(sorted_lines, start=1):
                line.number = idx

    @api.onchange('status')
    def _onchange_status_set_completed(self):
        for rec in self:
            if rec.status == 'done':
                rec.completed_by = rec.env.user.id
                rec.completed_on = fields.Datetime.now()
            else:
                # if revert from done, clear completed fields (optional)
                if rec.status != 'done':
                    rec.completed_by = rec.completed_by or False
                    # do not clear timestamps automatically in starter module

                    pass
    
    @api.constrains('code', 'checklist_id')
    def _check_code_unique_per_project(self):
        for rec in self:
            if rec.code:
                same = self.search([
                    ('code', '=', rec.code),
                    ('checklist_id.project_id', '=', rec.checklist_id.project_id.id),
                    ('id', '!=', rec.id)
                ], limit=1)
                if same:
                    raise ValidationError(_('Code %s already used in this project') % rec.code)