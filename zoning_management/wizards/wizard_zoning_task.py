# your_module_name/models/wizard_zoning_task.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ZoningTaskWizard(models.TransientModel):
    _name = 'zoning.task.wizard'
    _description = 'Wizard to Create or Link Task from Zoning Line'

    action_type = fields.Selection([('create', 'Create New Task'), ('link', 'Link Existing Task')], string='Action', default='create', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    analysis_id = fields.Many2one('project.zoning.analysis', string='Zoning Analysis', domain="[('project_id','=',project_id)]")
    zoning_line_id = fields.Many2one('project.zoning.analysis.line', string='Zoning Line', domain="[('analysis_id','=',analysis_id)]")

    # fields for creating new task
    new_task_name = fields.Char('Task Name')
    new_task_description = fields.Text('Description')
    new_task_deadline = fields.Date('Deadline')
    new_task_phase_id = fields.Many2one('project.phase', string='Phase')

    # field for linking existing
    existing_task_ids = fields.Many2many('project.task', string='Existing Task', domain="[('project_id','=',project_id)]")

    def action_confirm(self):
        self.ensure_one()
        if self.action_type == 'create':
            phase_default = self.zoning_line_id.phase_hint_id or self.analysis_id.project_id.current_phase_id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_project_id': self.project_id.id,
                    'default_analysis_id': self.analysis_id.id,
                    'default_phase_id': phase_default.id,
                    'default_show_zoning_tab': True,
                    'default_zoning_line_ids': [(6, 0, [self.zoning_line_id.id])],
                    'from_zoning_analysis': True,
                },
            }

        elif self.action_type == 'link':
            if not self.existing_task_ids:
                raise ValidationError(_("Please select at least one existing task to link."))
            self.zoning_line_id.task_ids = [(4, t.id) for t in self.existing_task_ids]
            return {'type': 'ir.actions.act_window_close'}
