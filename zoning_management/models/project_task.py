from odoo import models, fields, api
class ProjectTask(models.Model):
    _inherit = 'project.task'

    zoning_id = fields.Many2one('project.zoning', string="Related Zoning Analysis", ondelete='cascade')
    zoning_rule_id = fields.Many2one('project.zoning.rule', string="Zoning Rule Reference")
    zoning_snippet_ids = fields.Many2many('project.zoning.snippet', 'task_zoning_snippet_rel', 'task_id', 'snippet_id', string="Linked Regulation Snippets")
    sop_id = fields.Many2one('project.sop', string="Linked SOP")
    sheet_code = fields.Char(string="Sheet Code", help="E.g. Z01, A101")
    checklist_ids = fields.One2many('project.task.checklist', 'task_id', string="Task Checklists")
    checklist_progress = fields.Float(string="Checklist Progress", compute='_compute_checklist_progress')

    @api.depends('checklist_ids.is_done')
    def _compute_checklist_progress(self):
        for task in self:
            total = len(task.checklist_ids)
            done = len(task.checklist_ids.filtered(lambda c: c.is_done))
            task.checklist_progress = (done / total * 100.0) if total else 0.0