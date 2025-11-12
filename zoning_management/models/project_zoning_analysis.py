from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ZoningAnalysis(models.Model):
    _name = 'project.zoning.analysis'
    _description =  'Zoning Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, default=lambda self: _('Zoning Analysis'), tracking=True)
    project_id = fields.Many2one('project.project', required=True, ondelete='cascade')
    line_ids = fields.One2many('project.zoning.analysis.line', 'analysis_id', string='Zoning Lines')

    @api.model
    def create(self, vals):
        # require project_id
        if not vals.get('project_id'):
            raise UserError(_('Please choose a Project before creating a Zoning Analysis.'))
        # If name is default "Zoning Analysis" ensure uniqueness per project
        name = vals.get('name') or _('Zoning Analysis')
        if name.strip() == _('Zoning Analysis'):
            existing = self.search([('project_id', '=', vals['project_id']), ('name', '=', _('Zoning Analysis'))], limit=1)
            if existing:
                raise UserError(_('A "Zoning Analysis" already exists for the selected project. If you need a second analysis, please provide a different name.'))
        return super().create(vals)
    
    