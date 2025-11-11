from odoo import models, fields, api, _


class ProjectChecklistRule(models.Model):
    _name = 'project.checklist.rule'
    _description = 'Checklist Line Rule'

    line_id = fields.Many2one('project.checklist.line', string='Checklist Line', ondelete='cascade', required=True)
    trigger = fields.Selection([
        ('on_create', 'On Create'),
        ('on_status_change', 'On Status Change'),
        ('on_confirm', 'On Confirm'),
        ('on_deadline_reached', 'On Deadline Reached'),
    ], string='Trigger', default='on_status_change', required=True)
    condition_expression = fields.Text(string='Condition (expression/domain)', help="Safe expression or domain-based condition. Evaluator not implemented in starter module.")
    active = fields.Boolean(string='Active', default=True)
    action_ids = fields.One2many('project.checklist.rule.action', 'rule_id', string='Actions')
