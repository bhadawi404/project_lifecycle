from odoo import models, fields, api

class ProjectPhase(models.Model):
    _name = 'project.phase'
    _rec_name = 'name'

    code = fields.Char('Code', required=True)
    name = fields.Char('Phase',required=True)
    description = fields.Text('Description')
    is_zoning_phase = fields.Boolean(string="Zoning Required ?", default=False)
    active = fields.Boolean(default=True)

    @api.depends('code','name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code} - {record.name}" if record.code else record.name