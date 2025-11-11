from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
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
    assoc_employee_ids = fields.Many2many('hr.employee','project_checklist_line_employee_rel', 'line_id', 'employee_id', string='Associated Employees')
    assoc_task_ids = fields.Many2many('project.task', 'checklist_line_task_rel', 'cll_id', 'task_id', string='Associated Tasks')
    tag_ids = fields.Many2many('project.tags', string='Tags')
    # assoc_page_ids = fields.Many2many('project.page', string='Associated Pages')  # project.page could be custom
    # Reuse linking
    linked_checklist_id = fields.Many2one('project.checklist', string='Linked Checklist')
    linked_cll_ids = fields.Many2many('project.checklist.line', 'checklist_line_link_rel', 'cll_id', 'linked_id', string='Linked Lines')
    rule_ids = fields.One2many('project.checklist.rule', 'line_id', string='Rules')
    sequence = fields.Integer(string='Sequence', default=1)
    project_id = fields.Many2one(related='checklist_id.project_id', store=True, string='Project')
    number = fields.Integer(string='#', compute='_compute_sequence_number')


    @api.depends('checklist_id.line_ids.sequence')
    def _compute_sequence_number(self):
        checklists = self.mapped('checklist_id')
        for checklist in checklists:
            sorted_lines = checklist.line_ids.sorted(key=lambda x: x.sequence)
            for idx, line in enumerate(sorted_lines, start=1):
                line.number = idx

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
                
    def write(self, vals):
        # capture old statuses to detect change
        lines = self
        old_status = {l.id: l.status for l in lines}
        res = super(ProjectChecklistLine, self).write(vals)
        # after write, trigger rules for lines whose status changed
        changed = []
        if 'status' in vals:
            for l in lines:
                if old_status.get(l.id) != l.status:
                    changed.append(l)
        # Evaluate rules for changed lines
        for line in changed:
            # trigger rules with trigger 'on_status_change'
            for rule in line.rule_ids.filtered(lambda r: r.trigger == 'on_status_change' and r.active):
                try:
                    if rule._evaluate_condition():
                        rule._run_actions()
                except Exception as e:
                    _logger.exception("Error evaluating rule %s on line %s: %s", rule.id, line.id, e)
        return res