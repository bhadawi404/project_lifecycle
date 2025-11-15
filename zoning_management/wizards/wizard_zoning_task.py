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
    task_ids = fields.One2many('zoning.create.task.wizard', 'wizard_id', string='Task(s)')

    # field for linking existing
    existing_task_ids = fields.Many2many('project.task', string='Existing Task', domain="[('project_id','=',project_id)]")

    def action_confirm(self):
        self.ensure_one()
        if self.action_type == 'create':
            if not self.task_ids:
                raise ValidationError(_("Please input at least one task in the list."))
            for line in self.task_ids:
                phase_default = self.zoning_line_id.phase_hint_id or self.analysis_id.project_id.current_phase_id

                # Create project.task
                task = self.env['project.task'].create({
                    'name': line.name,
                    'phase_id': phase_default.id,
                    'date_deadline': line.date_deadline,
                    'description': line.description,
                    'show_zoning_tab': True,
                    'project_id': self.project_id.id,
                    'analysis_id': self.analysis_id.id,
                    'zoning_line_ids': [(6, 0, [self.zoning_line_id.id])],
                })
            return {'type': 'ir.actions.act_window_close'}
                

        elif self.action_type == 'link':
            if not self.existing_task_ids:
                raise ValidationError(_("Please select at least one existing task to link."))
            self.zoning_line_id.task_ids = [(4, t.id) for t in self.existing_task_ids]
            return {'type': 'ir.actions.act_window_close'}


class ZoningTaskCreationWizard(models.TransientModel):
    _name = 'zoning.create.task.wizard'
    _description = 'Wizard to Create Task from Zoning Line'

    wizard_id = fields.Many2one('zoning.task.wizard', string='Wizard')
    name = fields.Char('Task Name')
    date_deadline = fields.Datetime(string=_('Deadline'), default=fields.Datetime.now)
    description = fields.Text('Description')
