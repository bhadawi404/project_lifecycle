import json
from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    analysis_id = fields.Many2one(
        'project.zoning.analysis',
        string='Zoning Analysis',
        domain="[('project_id', '=', project_id)]"
    )
    zoning_line_ids = fields.Many2many(
        'project.zoning.analysis.line',
        'task_zoning_line_rel',  
        'task_id',
        'zoning_line_id',
        string='Zoning Lines'
    )

    
    available_zoning_line_ids = fields.Many2many(
        'project.zoning.analysis.line',
        compute='_compute_available_zoning_line_ids',
        store=False,
        string='Available Zoning Lines'
    )
    phase = fields.Selection([
        ('sd', 'SD - Schematic Design'),
        ('dd', 'DD - Design Development'),
        ('cd', 'CD - Construction Documents'),
        ('qc', 'QC - Quality Control'),
    ], string="Phase")

    @api.onchange('project_id')
    def _onchange_project_id_clear_analysis(self):
        if not self.project_id:
            self.analysis_id = False
            self.zoning_line_ids = [(5, 0, 0)]

        if not self.env.context.get('from_zoning_analysis'):
            if self.project_id:
                self.phase = self.project_id.current_phase or False

    @api.onchange('analysis_id')
    def _onchange_analysis_id_clear_lines(self):
        if not self.analysis_id:
            self.zoning_line_ids = [(5, 0, 0)]

    @api.depends('analysis_id')
    def _compute_available_zoning_line_ids(self):
        for task in self:
            if task.analysis_id:
                task.available_zoning_line_ids = task.analysis_id.line_ids
            else:
                task.available_zoning_line_ids = False

    def action_view_zoning_lines(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Zoning Lines'),
            'res_model': 'project.zoning.analysis.line',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.zoning_line_ids.ids)],
            'context': {'default_task_id': self.id},
        }

        if len(self.zoning_line_ids) == 1:
            form_view = self.env.ref('zoning_management.project_zoning_analysis_line_form_view', False)
            if form_view:
                action.update({
                    'view_mode': 'form',
                    'views': [(form_view.id, 'form')],
                    'res_id': self.zoning_line_ids.id,
                })
        return action
    

    