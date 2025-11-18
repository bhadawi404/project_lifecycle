# project_checklists/wizards/add_line_to_checklist_wizard.py
from odoo import models, fields, api

class AddLineToChecklistWizard(models.TransientModel):
    _name = 'add.line.to.checklist.wizard'
    _description = 'Add Line(s) to Checklists'

    line_ids = fields.Many2many('project.checklist.line', string='Lines', required=True)
    checklist_ids = fields.Many2many('project.checklist', string='Target Checklists', required=True)

    def action_apply(self):
        for wiz in self:
            # Add references: use ORM union (|=) to avoid duplicates
            for checklist in wiz.checklist_ids:
                checklist.line_ids = checklist.line_ids | wiz.line_ids
        return {'type': 'ir.actions.act_window_close'}
