from odoo import models, fields, api

class Projecttemplate(models.Model):
    _name = 'project.template'
    _rec_name = 'name'

    name = fields.Char('Template Name',required=True)
    project_type_id = fields.Many2one('project.type', string='Project Type')
    line_ids = fields.One2many('project.template.line', 'project_template_id', string='Detail Phase')

class ProjectTemplateLine(models.Model):
    _name = 'project.template.line'

    number = fields.Integer('#', compute='_compute_sequence_number', store=True)
    sequence = fields.Integer(default=1)
    project_template_id = fields.Many2one('project.template', string='Template ID', ondelete='cascade')
    phase_id = fields.Many2one('project.phase', string='Phase')
    is_zoning_phase = fields.Boolean(string="Zoning Required ?")
    description = fields.Text('Description', related='phase_id.description')

    @api.onchange('phase_id')
    def _onchange_phase_id(self):
        for record in self:
            record.is_zoning_phase = False
            if record.phase_id:
                record.is_zoning_phase = record.phase_id.is_zoning_phase

    @api.depends('project_template_id.line_ids.sequence')
    def _compute_sequence_number(self):
        templates = self.mapped('project_template_id')
        for template in templates:
            sorted_lines = template.line_ids.sorted(key=lambda x: x.sequence)
            for idx, line in enumerate(sorted_lines, start=1):
                line.number = idx