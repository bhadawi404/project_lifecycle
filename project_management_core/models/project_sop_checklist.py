from odoo import models, fields, api

class ProjectSOP(models.Model):
    _name = 'project.sop.checklist'
    _rec_name = 'name'

    name = fields.Char(string="Checklist Item", required=True)
    sop_id = fields.Many2one('project.sop', string="SOP", ondelete='cascade')
    notes = fields.Text(string="Notes")
    number = fields.Integer('#', compute='_compute_sequence_number', store=True)
    sequence = fields.Integer(default=1)
    
    @api.depends('sop_id.checklist_template_ids.sequence')
    def _compute_sequence_number(self):
        sop_groups = self.mapped('sop_id')
        for jpd in sop_groups:
            sorted_lines = jpd.checklist_template_ids.sorted(key=lambda x: x.sequence)
            for idx, line in enumerate(sorted_lines, start=1):
                line.number = idx
