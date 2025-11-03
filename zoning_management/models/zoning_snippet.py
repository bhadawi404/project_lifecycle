from odoo import models, fields, api

class ProjectZoningSnippet(models.Model):
    _name = 'project.zoning.snippet'
    _description = 'Zoning Regulation Snippet'
    _rec_name = 'name'

    name = fields.Char(string="Regulation Title", required=True)
    reference_code = fields.Char(string="Reference Code")
    description = fields.Text(string="Regulation Description")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment / Legal File")
    sheet_map_id = fields.Many2one('zoning.sheet.map', string='Zoning Sheet Map Category')
    city = fields.Char(string="City / Municipality")
    state = fields.Char(string="State / Region")
    project_type_id = fields.Many2one('project.type', string='Applicable Building Type')
    is_mandatory = fields.Boolean(string="Mandatory Requirement", default=True)
    action_recommendation = fields.Text(string="Recommended Compliance Action")
    note = fields.Text(string="Internal Notes")
    active = fields.Boolean(default=True)