from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class BulkCreateTaskChecklistWizard(models.TransientModel):
    _name = 'bulk.create.task.checklist'
    _description = 'Create Checklist'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    is_related_task = fields.Boolean('Add a Task ?')
    task_id = fields.Many2one('project.task', string='Task')
    checklist_ids = fields.One2many('bulk.create.task.checklist.line', 'wizard_id', string='Checklist')
    
    @api.onchange('is_related_task')
    def _onchange_is_related_task(self):
        if not self.is_related_task:
            self.task_id = False

    def action_confirm(self):
        self.ensure_one()
        if not self.checklist_ids:
            raise ValidationError(_("Please input at least one checklist in the list."))
        
        if self.is_related_task and self.task_id.project_id != self.project_id:
            raise ValidationError(_(
                "Task '%s' does not belong to the selected project '%s'."
            ) % (self.task_id.name, self.project_id.name))

        for line in self.checklist_ids:
            task_checklist = self.env['project.task.checklist'].create({
                'name': line.name,
                'task_id': self.task_id.id if self.task_id else False,
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
    name = fields.Char('Title')
    user_ids = fields.Many2many('res.users', string='Assignees')
    description = fields.Text('Description')