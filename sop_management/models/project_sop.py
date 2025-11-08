from odoo import models, fields

class ProjectSOP(models.Model):
    _name = 'project.sop'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Standard Operating Procedure (SOP)'

    name = fields.Char('SOP Name', required=True)
    code = fields.Char('SOP Code')
    description = fields.Text('Description')
    active = fields.Boolean(default=True)
    checklist_ids = fields.One2many('project.sop.checklist', 'sop_id', string='Checklist Items')
