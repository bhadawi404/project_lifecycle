from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
class ProjectChecklistLine(models.Model):
    _name = 'project.checklist.line'
    _description = 'Project Checklist Line'
    _inherit = ['mail.thread']
    _order = 'id'

    name = fields.Char(string='Question / Item', required=True, tracking=True)
    description = fields.Text(string='Description')
    code = fields.Char(string='Code', help='Optional code unique per project')
    checklist_ids = fields.Many2many(
        'project.checklist',
        'checklist_line_rel',
        'line_id',
        'checklist_id',
        string='Used in Checklists'
    )
    primary_checklist_id = fields.Many2one('project.checklist', string='Primary Checklist', help='Optional primary checklist reference')
    # user assignment: a line may be assigned to employees
    assoc_employee_ids = fields.Many2many('hr.employee', 'project_checklist_line_employee_rel','line_id', 'employee_id', string='Assigned Employees')
    assoc_task_ids = fields.Many2many('project.task', 'checklist_line_task_rel','cll_id', 'task_id', string='Associated Tasks')
    sequence = fields.Integer(string='Sequence', default=10)
    project_id = fields.Many2one('project.project', compute='_compute_project_id', store=True)
    note = fields.Text(string='Notes')

    def add_line_to_checklist_wizard_action(self):
        self.ensure_one()
        return {
            'name': _('Add line(s) to checklist(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'add.line.to.checklist.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_line_ids': [(6, 0, [self.id])],
            }
        }
    
    @api.depends('checklist_ids.project_id')
    def _compute_project_id(self):
        for rec in self:
            rec.project_id = rec.checklist_ids[:1].project_id.id if rec.checklist_ids else False

    @api.constrains('code')
    def _check_code_unique_per_project(self):
        for rec in self:
            if rec.code and rec.project_id:
                existing = self.search([
                    ('code', '=', rec.code),
                    ('project_id', '=', rec.project_id.id),
                    ('id', '!=', rec.id)
                ], limit=1)
                if existing:
                    raise ValidationError(_('Code %s already used in this project') % rec.code)
                

    