import json
import logging
from odoo import models, fields,_
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

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

    def _parse_params(self):
        try:
            return json.loads(self.params_json or '{}')
        except Exception:
            return {}

    def _resolve_targets(self, trigger_line):
        """Return dict of target recordsets based on target_scope and trigger_line context."""
        self.ensure_one()
        env = self.env
        targets = {
            'lines': env['project.checklist.line'].browse(),
            'tasks': env['project.task'].browse(),
            'employees': env['hr.employee'].browse(),
        }
        if self.target_scope == 'this_line':
            targets['lines'] = trigger_line
        elif self.target_scope == 'associated_tasks':
            targets['tasks'] = trigger_line.assoc_task_ids or env['project.task'].browse()
        elif self.target_scope == 'associated_employees':
            targets['employees'] = trigger_line.assoc_employee_ids or env['hr.employee'].browse()
        elif self.target_scope == 'explicit_selection':
            targets['lines'] = self.rule_id.line_id or env['project.checklist.line'].browse()
            targets['tasks'] = self.rule_id.line_id.assoc_task_ids or env['project.task'].browse()
        return targets

    def execute_action(self, trigger_line):
        """Execute this action in the context of trigger_line."""
        self.ensure_one()
        params = self._parse_params()
        targets = self._resolve_targets(trigger_line)

        # set_line_status
        if self.action_type == 'set_line_status':
            status = params.get('status')
            if not status:
                raise UserError(_("Parameter 'status' is required for set_line_status"))
            lines = targets.get('lines')
            if lines:
                lines.sudo().write({'status': status})

        # activate_line / deactivate_line (toggle active)
        elif self.action_type == 'activate_line':
            lines = targets.get('lines')
            if lines:
                lines.sudo().write({'active': True})
        elif self.action_type == 'deactivate_line':
            lines = targets.get('lines')
            if lines:
                lines.sudo().write({'active': False})

        # set_task_stage
        elif self.action_type == 'set_task_stage':
            stage_id = params.get('stage_id')
            if not stage_id:
                raise UserError(_("Parameter 'stage_id' is required for set_task_stage"))
            tasks = targets.get('tasks')
            if tasks:
                tasks.write({'stage_id': int(stage_id)})

        # block_task / unblock_task -> set custom boolean if exists else no-op
        elif self.action_type in ('block_task', 'unblock_task'):
            tasks = targets.get('tasks')
            for t in tasks:
                if hasattr(t, 'is_blocked'):
                    t.write({'is_blocked': (self.action_type == 'block_task')})

        # set_field_value: params: { "field": "name", "value": "X", "model": "project.task" (optional) }
        elif self.action_type == 'set_field_value':
            field_name = params.get('field')
            value = params.get('value')
            model = params.get('model')
            if not field_name:
                raise UserError(_("Parameter 'field' is required for set_field_value"))
            recs = None
            if model:
                if model not in ('project.task', 'project.checklist.line'):
                    raise UserError(_("Model %s not permitted for set_field_value in starter module") % model)
                Model = self.env[model]
                if model == 'project.task':
                    recs = targets.get('tasks') or Model.browse()
                else:
                    recs = targets.get('lines') or Model.browse()
            else:
                # default to lines if present else tasks
                recs = targets.get('lines') or targets.get('tasks')
            if recs:
                recs.write({field_name: value})

        else:
            _logger.warning("Unknown action_type %s on action %s", self.action_type, self.id)