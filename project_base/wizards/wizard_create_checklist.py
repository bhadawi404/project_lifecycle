from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BulkCreateTaskChecklistWizard(models.TransientModel):
    _name = 'bulk.create.task.checklist'
    _description = 'Create Task Checklist'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    checklist_ids = fields.One2many('bulk.create.task.checklist.line', 'wizard_id', string='Checklist')
    
    def action_confirm(self):
        self.ensure_one()
        if not self.checklist_ids:
            raise ValidationError(_("Please input at least one checklist in the list."))
        
        for line in self.checklist_ids:
            if line.task_id and line.task_id.project_id != self.project_id:
                raise ValidationError(_(
                    "Task '%s' does not belong to the selected project '%s'."
                ) % (line.task_id.name, self.project_id.name))

        for line in self.checklist_ids:
            task_checklist = self.env['project.task.checklist'].create({
                'name': line.name,
                'task_id': line.task_id.id,
                'project_id': self.project_id.id,
                'description': line.description,
                'status': 'todo',
                'user_ids': [(6, 0, line.user_ids.ids)],
                })
        return {'type': 'ir.actions.act_window_close'}


class BulkCreateTaskChecklistLineWizard(models.TransientModel):
    _name = 'bulk.create.task.checklist.line'
    _description = 'Create Tasks Checklist Line'

    wizard_id = fields.Many2one('bulk.create.task.checklist', string='Wizard')
    task_id = fields.Many2one('project.task', string='Task')
    name = fields.Char('Title')
    user_ids = fields.Many2many('res.users', string='Assignees')
    description = fields.Text('Description')