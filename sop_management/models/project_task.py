from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    sop_id = fields.Many2one('project.sop', string='Standard Operating Procedure')
    checklist_ids = fields.One2many('project.task.checklist', 'task_id', string='Task Checklist')
    checklist_progress = fields.Float('Checklist Progress', compute='_compute_checklist_progress', store=True)

    @api.depends('checklist_ids.is_done')
    def _compute_checklist_progress(self):
        for task in self:
            total = len(task.checklist_ids)
            done = len(task.checklist_ids.filtered('is_done'))
            task.checklist_progress = (done / total * 100) if total > 0 else 0

    @api.onchange('sop_id')
    def _onchange_sop_id_generate_checklist(self):
        """Generate checklist lines from selected SOP"""
        for task in self:
            if task.sop_id:
                checklist_lines = []
                for item in task.sop_id.checklist_ids:
                    checklist_lines.append((0, 0, {
                        'sop_checklist_id': item.id,
                        'name': item.name,
                        'description': item.description,
                        'section': item.section,
                        'sequence': item.sequence,
                    }))
                task.checklist_ids = [(5, 0, 0)] + checklist_lines
