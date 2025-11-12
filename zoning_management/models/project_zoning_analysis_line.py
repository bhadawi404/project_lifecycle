from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ZoningAnalysisLine(models.Model):
    _name = 'project.zoning.analysis.line'
    _description = 'Zoning Analysis Line'

    analysis_id = fields.Many2one('project.zoning.analysis', ondelete='cascade')
    zoning_code = fields.Char('Zoning Code / Section')
    description = fields.Text('Description')
    max_allowed = fields.Char('Max Allowed / Min Required')
    proposed = fields.Char('Proposed')
    task_ids = fields.Many2many(
        'project.task',
        'task_zoning_line_rel',   
        'zoning_line_id',
        'task_id',
        string='Tasks'
    )
    display_name = fields.Char('display_name', compute='_compute_display_name')
    phase_hint_id = fields.Many2one('project.phase', string='Phase Hint (Optional)')


    @api.depends('zoning_code', 'description')
    def _compute_display_name(self):
        for line in self:
            code = (line.zoning_code or "").strip()
            desc = (line.description or "").strip()
            if code and desc:
                line.display_name = f"{code} - {desc}"
            elif code:
                line.display_name = code
            elif desc:
                line.display_name = desc

    # def action_create_task(self):
    #     self.ensure_one()  
    #     phase_default = self.phase_hint_id or self.analysis_id.project_id.current_phase_id
    #     action = self.env.ref("project.action_view_task").read()[0]
    #     action.update({
    #         "view_mode": "form",
    #         "views": [(self.env.ref("project.view_task_form2").id, "form")],
    #         "target": "current",
    #         "context": {
    #             "default_name": f"{self.zoning_code or ''} - {self.description or ''}",
    #             "default_phase_id": phase_default.id,
    #             "default_analysis_id": self.analysis_id.id,
    #             "default_project_id": self.analysis_id.project_id.id,
    #             "default_zoning_line_ids": [(6, 0, [self.id])],
    #             "from_zoning_analysis": True,
    #         },
    #     })
    #     return action

    def open_create_link_wizard(self):
        """Open wizard prefilled with current analysis and project."""
        self.ensure_one()
        view = self.env.ref('zoning_management.wizard_zoning_task_view_form', False)
        return {
            'name': _('Create / Link Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'zoning.task.wizard',
            'view_mode': 'form',
            'views': [(view.id, 'form')] if view else None,
            'target': 'new',
            'context': {
                'default_project_id': self.analysis_id.project_id.id if self.analysis_id else False,
                'default_analysis_id': self.analysis_id.id,
                'default_zoning_line_id': self.id,
            }
        }