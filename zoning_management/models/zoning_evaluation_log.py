from odoo import models, fields, api

class ProjectZoningEvaluationLog(models.Model):
    _name = 'project.zoning.evaluation.log'
    _description = 'Zoning Evaluation Log'
    _order = 'evaluated_on desc'

    evaluated_on = fields.Datetime(string='Evaluated On', default=fields.Datetime.now)
    evaluated_by = fields.Many2one('res.users', string='Evaluated By')
    zoning_id = fields.Many2one('project.zoning', string='Zoning Analysis', ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Project', ondelete='cascade')
    rule_id = fields.Many2one('project.zoning.rule', string='Rule')
    task_id = fields.Many2one('project.task', string='Generated Task')
    field_name = fields.Char(string='Field Name')
    field_value = fields.Char(string='Field Value')
    operator = fields.Char(string='Operator')
    expected_value = fields.Char(string='Expected Value')
    message = fields.Text(string='Message')
    result = fields.Selection([
        ('match', 'Match'),
        ('no_match', 'No Match'),
        ('task_created', 'Task Created'),
        ('error', 'Error')
    ], string='Result', default='no_match')