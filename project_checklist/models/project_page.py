from odoo import models, fields, api, _


class ProjectPage(models.Model):
    _name = 'project.page'
    _description =  'Project Page'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Name')
    code = fields.Char('Code')
    project_id = fields.Many2one('project.project', string='Project')
    description = fields.Text('Description')