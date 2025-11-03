# models/project_zoning_result.py
from odoo import models, fields

class ProjectZoningResult(models.Model):
    _name = 'zoning.result'
    _description = 'Zoning Analysis Result Table'
    _order = 'rule_code, id'

    zoning_id = fields.Many2one('project.zoning', string="Zoning Analysis", ondelete='cascade', required=True, index=True)
    rule_code = fields.Char(string="ZR Section")
    description = fields.Char(string="Description")
    max_allowed = fields.Char(string="Max Allowed / Min Required")
    proposed = fields.Char(string="Proposed")
    sheet_reference = fields.Char(string="Sheet Reference")
    rule_id = fields.Many2one('project.zoning.rule', string='Rule', ondelete='set null')
    snippet_ids = fields.Many2many('project.zoning.snippet', 'zoning_result_snippet_rel', 'result_id', 'snippet_id', string='Snippets')
