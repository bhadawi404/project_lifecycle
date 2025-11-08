from odoo import models, fields, api

class ProjectSOPChecklist(models.Model):
    _name = 'project.sop.checklist'
    _description = 'SOP Checklist Item'
    _order = 'sop_id, sequence, id'

    sop_id = fields.Many2one('project.sop', ondelete='cascade', required=True)
    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Instructions / Details')
    section = fields.Char('SOP Section')
    sequence = fields.Integer('Sequence', default=1)
    number = fields.Integer('#', compute='_compute_sequence_number')

    @api.depends('sop_id.checklist_ids.sequence')
    def _compute_sequence_number(self):
        sop_ids = self.mapped('sop_id')
        for sop in sop_ids:
            sorted_lines = sop.checklist_ids.sorted(key=lambda x: x.sequence)
            for idx, line in enumerate(sorted_lines, start=1):
                line.number = idx
