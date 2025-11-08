from odoo import models, fields, api, _

class ProjectTaskChecklist(models.Model):
    _name = 'project.task.checklist'
    _description = 'Task Checklist Item'
    _order = 'sequence, id'

    task_id = fields.Many2one('project.task', ondelete='cascade', required=True)
    sop_checklist_id = fields.Many2one('project.sop.checklist', string='SOP Template Item')
    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Details')
    section = fields.Char('Section')
    sequence = fields.Integer('Sequence', default=1)
    number = fields.Integer('#', compute='_compute_sequence_number')
    is_done = fields.Boolean('Completed')
    reviewer_id = fields.Many2one('res.users', string='Reviewed By')
    reviewed_date = fields.Datetime('Reviewed On')

    @api.depends('task_id.checklist_ids.sequence')
    def _compute_sequence_number(self):
        task_ids = self.mapped('task_id')
        for task in task_ids:
            sorted_lines = task.checklist_ids.sorted(key=lambda x: x.sequence)
            for idx, line in enumerate(sorted_lines, start=1):
                line.number = idx

    @api.onchange('is_done')
    def _onchange_is_done(self):
        """Optional visual feedback"""
        for line in self:
            if line.is_done:
                line.reviewed_date = fields.Datetime.now()
                if not line.reviewer_id:
                    line.reviewer_id = self.env.user
