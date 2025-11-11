import re
import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)

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

    def _lines_by_prefix(self, prefix):
        """Return lines in same project whose code startswith prefix (case-insensitive)."""
        self.ensure_one()
        if not self.line_id or not self.line_id.project_id:
            return self.env['project.checklist.line'].browse()
        domain = [
            ('checklist_id.project_id', '=', self.line_id.project_id.id),
            ('code', 'ilike', f"{prefix}%")
        ]
        return self.env['project.checklist.line'].search(domain)

    def _line_by_code(self, code):
        return self.env['project.checklist.line'].search([('code', '=', code)], limit=1)

    def _evaluate_condition(self):
        """Evaluate supported condition expressions for this rule. Returns True/False."""
        self.ensure_one()
        expr = (self.condition_expression or '').strip()
        if not expr:
            return False

        # Pattern 1: all('PREFIX:*') == done
        m_all = re.match(r"^\s*all\('([^']+)'\)\s*==\s*['\"]?done['\"]?\s*$", expr, flags=re.IGNORECASE)
        if m_all:
            token = m_all.group(1)  # e.g. "DD:*" or "DD:STRUCTURE:*" - we simplify to prefix before colon
            prefix = token.split(':')[0]
            lines = self._lines_by_prefix(prefix)
            if not lines:
                return False
            return all(l.status == 'done' for l in lines)

        # Pattern 2: any('PREFIX:*') == done
        m_any = re.match(r"^\s*any\('([^']+)'\)\s*==\s*['\"]?done['\"]?\s*$", expr, flags=re.IGNORECASE)
        if m_any:
            token = m_any.group(1)
            prefix = token.split(':')[0]
            lines = self._lines_by_prefix(prefix)
            if not lines:
                return False
            return any(l.status == 'done' for l in lines)

        # Pattern 3: line('CODE').status == 'done'
        m_line = re.match(r"^\s*line\('([^']+)'\)\.status\s*==\s*['\"]?done['\"]?\s*$", expr, flags=re.IGNORECASE)
        if m_line:
            code = m_line.group(1)
            line = self._line_by_code(code)
            return bool(line and line.status == 'done')

        # Extend here for more patterns later
        _logger.warning("Unsupported condition expression for rule %s: %s", self.id, expr)
        return False

    def _run_actions(self):
        """Run actions attached to this rule (simple runner)."""
        for action in self.action_ids.filtered('active'):
            try:
                action.execute_action(self.line_id)
            except Exception as e:
                _logger.exception("Error running action %s for rule %s: %s", action.id, self.id, e)

    @api.model
    def cron_check_rule_consistency(self):
        rules = self.search([('active', '=', True), ('trigger', '=', 'on_deadline_reached')])
        for rule in rules:
            try:
                if rule._evaluate_condition():
                    rule._run_actions()
            except Exception as e:
                _logger.error("CRON rule check failed for rule %s: %s", rule.id, e)
