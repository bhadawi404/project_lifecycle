from odoo import models, fields, api

class ProjectType(models.Model):
    _name = 'project.type'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name',required=True)
    description = fields.Text('Description')
    active = fields.Boolean(default=True)

    @api.depends('code','name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code} - {record.name}" if record.code else record.name