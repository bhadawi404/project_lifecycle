# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class ProjectChecklistViewEmployee(models.Model):
    _name = 'project.checklist.view.employee'
    _description = 'Checklist Lines per Employee'
    _auto = False  # SQL view
    _rec_name = 'line_name'

    line_id = fields.Many2one('project.checklist.line', string='Checklist Line', readonly=True)
    checklist_id = fields.Many2one('project.checklist', string='Checklist', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    line_name = fields.Char(string='Checklist Item', readonly=True)
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('na', 'N/A'),
    ], string='Status', readonly=False, group_expand='_group_expand_states')

    completed_by = fields.Many2one('res.users', string='Completed By', readonly=False)
    completed_on = fields.Datetime(string='Completed On', readonly=False)

    @api.model
    def _group_expand_states(self, states, domain):
        return [key for key, val in type(self).status.selection]
        
    def init(self):
        """Build SQL View"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    row_number() OVER() AS id,
                    cl.id AS line_id,
                    cl.checklist_id,
                    cl.project_id,
                    emp.id AS employee_id,
                    cl.name AS line_name,
                    cl.status,
                    cl.completed_by,
                    cl.completed_on
                FROM project_checklist_line cl
                JOIN project_checklist_line_employee_rel rel
                    ON rel.line_id = cl.id
                JOIN hr_employee emp
                    ON emp.id = rel.employee_id
            )
        """)

    def write(self, vals):
        for rec in self:
            if 'status' in vals:
                rec.line_id.status = vals['status']
        return super().write(vals)

class ProjectChecklistViewTask(models.Model):
    _name = 'project.checklist.view.task'
    _description = 'Checklist Lines per Task'
    _auto = False
    _rec_name = 'line_name'

    line_id = fields.Many2one('project.checklist.line', string='Checklist Line', readonly=True)
    checklist_id = fields.Many2one('project.checklist', string='Checklist', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)

    task_id = fields.Many2one('project.task', string='Task', readonly=True)
    line_name = fields.Char(string='Checklist Item', readonly=True)
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('na', 'N/A'),
    ], string='Status', readonly=False, group_expand='_group_expand_states')

    completed_by = fields.Many2one('res.users', string='Completed By', readonly=False)
    completed_on = fields.Datetime(string='Completed On', readonly=False)

    @api.model
    def _group_expand_states(self, states, domain):
        return [key for key, val in type(self).status.selection]
    
    def write(self, vals):
        for rec in self:
            if 'status' in vals:
                rec.line_id.status = vals['status']
        return super().write(vals)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    row_number() OVER() AS id,
                    cl.id AS line_id,
                    cl.checklist_id,
                    cl.project_id,
                    t.id AS task_id,
                    cl.name AS line_name,
                    cl.status,
                    cl.completed_by,
                    cl.completed_on
                FROM project_checklist_line cl
                JOIN checklist_line_task_rel rel
                    ON rel.cll_id = cl.id
                JOIN project_task t
                    ON t.id = rel.task_id
            )
        """)

