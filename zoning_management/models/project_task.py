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
    phase_id = fields.Many2one('project.phase', string='Phase')
    show_zoning_tab = fields.Boolean(default=False)
    
    @api.onchange('project_id')
    def _onchange_project_id_clear_analysis(self):
        if not self.project_id:
            self.analysis_id = False
            self.zoning_line_ids = [(5, 0, 0)]

        if not self.env.context.get('from_zoning_analysis'):
            if self.project_id:
                self.phase_id = self.project_id.current_phase_id or False

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

    @api.onchange('show_zoning_tab')
    def _onchange_show_zoning_tab(self):
        """Clear zoning fields when toggle is turned off"""
        if not self.show_zoning_tab:
            self.analysis_id = False
            self.available_zoning_line_ids = [(5, 0, 0)]  # clear all many2many
            self.zoning_line_ids = [(5, 0, 0)]  # clear one2many

    

    