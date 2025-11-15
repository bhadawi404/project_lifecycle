from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BulkCreateTaskWizard(models.TransientModel):
    _name = 'bulk.create.task'
    _description = 'Bulk Create Tasks'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    phase_id = fields.Many2one('project.phase', string='Current Phase', related='project_id.current_phase_id')
    task_ids = fields.One2many('bulk.create.task.line', 'wizard_id', string='task')
    
    def action_confirm(self):
        self.ensure_one()
        if not self.task_ids:
            raise ValidationError(_("Please input at least one task in the list."))
        created_tasks = []
        for line in self.task_ids:
            phase_default = line.phase_id or self.phase_id
            # Create project.task
            task = self.env['project.task'].create({
                'project_id': self.project_id.id,
                'name': line.name,
                'phase_id': phase_default.id,
                'description': line.description,
                'date_deadline': line.date_deadline,
                'user_ids': [(6, 0, line.user_ids.ids)],
            })
            created_tasks.append(task.id)
        if len(created_tasks) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'res_id': created_tasks[0],
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'name': _('Created Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_tasks)],
            'target': 'current',
        }


class BulkCreateTaskLineWizard(models.TransientModel):
    _name = 'bulk.create.task.line'
    _description = 'Bulk Create Tasks Line'

    wizard_id = fields.Many2one('bulk.create.task', string='Wizard')
    name = fields.Char('Task Name')
    user_ids = fields.Many2many('res.users', string='Assignees')
    phase_id = fields.Many2one('project.phase', string='Phase')
    date_deadline = fields.Datetime(string=_('Deadline'), default=fields.Datetime.now)
    description = fields.Text('Description')