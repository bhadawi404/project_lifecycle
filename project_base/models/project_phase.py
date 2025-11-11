from odoo import models, fields, api, _


class ProjectPhase(models.Model):
    _name = 'project.phase'
    _description =  'Project Phase'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name',required=True)
    code = fields.Char('Phase', required=True)
    description = fields.Text('Description')
    display_name = fields.Char('display_name', compute='_compute_display_name')
    
    @api.depends('code', 'name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code} - {record.name}"

    
    