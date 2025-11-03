from odoo import models, fields, api
import operator
class ProjectZoningRule(models.Model):
    _name = 'project.zoning.rule'
    _description = 'Zoning Rule Definition'
    _rec_name = 'name'

    name = fields.Char(string="Rule Name", required=True)
    code = fields.Char('Code', help="Zoning Rule Code e.g., ZR-001")
    project_type_id = fields.Many2one('project.type', string='Project Type', required=True)
    legal_reference = fields.Char(string="Legal Reference", help="e.g., IZC §402, City Ordinance 14-3.2")
    jurisdiction = fields.Selection([
        ('city', 'City'),
        ('county', 'County'),
        ('state', 'State'),
        ('federal', 'Federal')
    ], string="Jurisdiction Level", default='city')
    severity = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor')
    ], string="Severity Level", default='major')
    model_id = fields.Many2one('ir.model', string="Target Model", required=True,
                               help="Target model to evaluate (usually project.zoning)",ondelete='cascade', default=lambda self: self.env['ir.model'].search([('model', '=', 'project.zoning')], limit=1))
    field_id = fields.Many2one('ir.model.fields', string="Condition Field",
                               help="Select numeric field from target model (filtered dynamically).")
    operator = fields.Selection([
        ('gt', 'Greater than (>)'),
        ('lt', 'Less than (<)'),
        ('ge', 'Greater or Equal (≥)'),
        ('le', 'Less or Equal (≤)'),
        ('eq', 'Equal (==)'),
        ('ne', 'Not Equal (!=)')
    ], string="Operator", required=True)
    value = fields.Float(string="Expected Value", required=True)
    snippet_ids = fields.Many2many('project.zoning.snippet', 'zoning_rule_snippet_rel', 'rule_id', 'snippet_id', string="Zoning Snippets / Clauses")
    sop_id = fields.Many2one('project.sop', string="Linked SOP", help="SOP to be used when this rule triggers.")
    note = fields.Text(string="Rule Notes")
    auto_action = fields.Selection([
        ('none', 'No Action'),
        ('warning', 'Raise Warning'),
        ('create_task', 'Create Compliance Task')
    ], string="Auto Action", default='none')
    active = fields.Boolean(default=True)

    def _evaluate_condition(self, record):
        """Evaluate this zoning rule against a given record dynamically."""
        self.ensure_one()
        if not self.field_id:
            return False
        field_name = self.field_id.name
        try:
            field_value = getattr(record, field_name)
        except Exception:
            return False

        ops = {
            'gt': operator.gt,
            'lt': operator.lt,
            'ge': operator.ge,
            'le': operator.le,
            'eq': operator.eq,
            'ne': operator.ne,
        }
        op = ops.get(self.operator)
        if not op:
            return False

        try:
            return bool(op(float(field_value), float(self.value)))
        except Exception:
            return False
            

class ProjectSOP(models.Model):
    _inherit = 'project.sop'

    rule_ids = fields.One2many('project.zoning.rule', 'sop_id', string="Linked Zoning Rules")
