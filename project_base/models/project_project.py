from odoo import models, fields, api, _
class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_default_phase(self):
        default_phase = self.env['project.phase'].search([('code', '=', 'SD')], limit=1)
        return default_phase.id if default_phase else False
    
    current_phase_id = fields.Many2one('project.phase',string='Current Phase',tracking=True, default=_get_default_phase)
