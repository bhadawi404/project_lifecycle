from odoo import models, fields, api, _

class ProjectChecklistRuleAction(models.Model):
    _name = 'project.checklist.rule.action'
    _description = 'Checklist Rule Action'

    rule_id = fields.Many2one('project.checklist.rule', string='Rule', ondelete='cascade', required=True)
    action_type = fields.Selection([
        ('set_task_stage', 'Set Task Stage'),
        ('set_line_status', 'Set Line Status'),
        ('activate_line', 'Activate Line'),
        ('deactivate_line', 'Deactivate Line'),
        ('block_task', 'Block Task'),
        ('set_field_value', 'Set Field Value'),
    ], string='Action Type', required=True)
    params_json = fields.Text(string='Parameters (JSON)', help='JSON parameters to configure action, e.g. {"stage_id": 5, "task_id": 12}')