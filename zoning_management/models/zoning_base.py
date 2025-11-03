from odoo import api, models, fields, _
import operator as py_operator
class ProjectZoning(models.Model):
    _name = 'project.zoning'
    _description = 'Project Zoning Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Zoning Reference', required=True, copy=False, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    phase_id = fields.Many2one('project.phase', string='Related Phase')
    land_area = fields.Float(string='Land Area (m²)')
    building_area = fields.Float(string='Building Area (m²)')
    far = fields.Float(string='FAR (Floor Area Ratio)', digits=(12, 6))
    height_limit = fields.Float(string='Building Height (m)', digits=(12, 4))
    setback_front = fields.Float(string='Front Setback (m)', digits=(12, 4))
    setback_rear = fields.Float(string='Rear Setback (m)', digits=(12, 4))
    setback_side = fields.Float(string='Side Setback (m)', digits=(12, 4))
    area_coverage = fields.Float(string='Coverage Ratio (%)', digits=(12, 6))
    green_ratio = fields.Float(string='Green Open Space (%)')
    parking_area = fields.Float(string='Parking Area (m²)')

    zoning_rule_ids = fields.Many2many('project.zoning.rule', 'zoning_rule_rel', 'zoning_id', 'rule_id', string='Triggered Rules', readonly=True)
    zoning_snippet_ids = fields.Many2many('project.zoning.snippet', 'zoning_snippet_rel', 'zoning_id', 'snippet_id', string='Legal References', readonly=True)
    evaluation_log_ids = fields.One2many('project.zoning.evaluation.log', 'zoning_id', string='Evaluation Logs')
    task_ids = fields.One2many('project.task', 'zoning_id', string='Generated Tasks')
    zoning_result_ids = fields.One2many('zoning.result', 'zoning_id', string='Zoning Analysis Sheet')
    violation_count = fields.Integer(string='Violation Count', compute='_compute_violation_count', store=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('evaluated', 'Evaluated'),
        ('approved', 'Approved'),
        ('violation', 'Violation'),
    ], string='Status', default='draft', tracking=True)

    _sql_constraints = [
        ('unique_project_zoning', 'unique(project_id)', 'Each project should have at most one zoning analysis record.')
    ]
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) in (None, '', _('New')):
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('project.zoning') or _('New')
        return super().create(vals)

    @api.depends('evaluation_log_ids')
    def _compute_violation_count(self):
        for rec in self:
            rec.violation_count = len(rec.evaluation_log_ids.filtered(lambda l: l.result in ['no_match', 'task_created']))

    # =====================================
    # RULE EVALUATION MAIN LOGIC
    # =====================================
    # -------------------------
    # Evaluate rules, create results rows and logs, create tasks when needed
    # -------------------------
    def action_evaluate_rules(self):
        Rule = self.env['project.zoning.rule']
        Log = self.env['project.zoning.evaluation.log']
        Result = self.env['zoning.result']
        SheetMap = self.env['zoning.sheet.map']

        operator_symbols = {
            'gt': '>',
            'lt': '<',
            'ge': '≥',
            'le': '≤',
            'eq': '=',
            'ne': '≠',
        }

        # operator mapping for comparison
        ops = {
            'gt': py_operator.gt,
            'lt': py_operator.lt,
            'ge': py_operator.ge,
            'le': py_operator.le,
            'eq': py_operator.eq,
            'ne': py_operator.ne,
        }

        for zoning in self:
            # clear old logs and result rows
            zoning.evaluation_log_ids.unlink()
            Result.search([('zoning_id', '=', zoning.id)]).unlink()

            triggered_rules = []
            triggered_snippets = []
            violation_found = False

            project_type = getattr(zoning.project_id, 'project_type_id', False)
            rules_domain = [('active', '=', True)]
            if project_type:
                rules_domain.append(('project_type_id', '=', project_type.id))
            rules = Rule.search(rules_domain)

            for rule in rules:
                field_name = rule.field_id.name if rule.field_id else None
                field_value = getattr(zoning, field_name, None) if field_name else None

                # evaluate
                try:
                    op_func = ops.get(rule.operator)
                    if op_func and field_value is not None:
                        result_flag = bool(op_func(float(field_value), float(rule.value)))
                    else:
                        # if no operator or value, consider match True by default
                        result_flag = True if not rule.operator else False
                except Exception as e:
                    result_flag = False

                # collect sheet codes from snippets
                sheet_codes = []
                related_snippets = rule.snippet_ids
                for snippet in related_snippets:
                    if getattr(snippet, 'sheet_map_id', False):
                        maps = SheetMap.search([('id', '=', snippet.sheet_map_id.id), ('active', '=', True)])
                    else:
                        maps = SheetMap.search([('category', '=', snippet.category), ('active', '=', True)])
                    sheet_codes += maps.mapped('sheet_code')

                sheet_reference = ', '.join(sorted(set(sheet_codes))) if sheet_codes else ''

                # create result row (report table)
                Result.create({
                    'zoning_id': zoning.id,
                    'rule_id': rule.id,
                    'rule_code': rule.code or rule.name,
                    'description': related_snippets and related_snippets[0].name or rule.name,
                    'max_allowed': f"{operator_symbols.get(rule.operator, rule.operator)} {rule.value}" if rule.value is not None else '',
                    'proposed': str(field_value) if field_value is not None else '',
                    'sheet_reference': sheet_reference,
                    'snippet_ids': [(6,0, related_snippets.ids)] if related_snippets else False,
                })

                # create evaluation log
                Log.create({
                    'evaluated_by': self.env.user.id,
                    'zoning_id': zoning.id,
                    'project_id': zoning.project_id.id,
                    'rule_id': rule.id,
                    'field_name': field_name or '',
                    'field_value': str(field_value) if field_value is not None else '',
                    'operator': rule.operator or '',
                    'expected_value': str(rule.value) if rule.value is not None else '',
                    'message': f"{field_name}: {field_value} (Expected {operator_symbols.get(rule.operator, rule.operator)} {rule.value})",
                    'result': 'match' if result_flag else 'no_match'
                })

                # bookkeeping
                if not result_flag:
                    violation_found = True
                    triggered_rules.append(rule.id)
                    triggered_snippets += related_snippets.ids

                    # create SOP task and attach failing subtasks
                    if rule.auto_action == 'create_task' and rule.sop_id:
                        # create sheet subtasks (all), then link failing ones to parent SOP task
                        created_subtasks = self._create_sheet_subtasks(rule, result_flag=False)
                        parent_task = self._create_violation_task_from_sop(rule, created_subtasks)
                        # update log to reference task
                        Log.create({
                            'evaluated_by': self.env.user.id,
                            'zoning_id': zoning.id,
                            'project_id': zoning.project_id.id,
                            'rule_id': rule.id,
                            'task_id': parent_task.id if parent_task else False,
                            'field_name': field_name or '',
                            'field_value': str(field_value) if field_value is not None else '',
                            'operator': rule.operator or '',
                            'expected_value': str(rule.value) if rule.value is not None else '',
                            'message': 'Violation - SOP task created' ,
                            'result': 'task_created'
                        })

            zoning.write({
                'zoning_rule_ids': [(6, 0, triggered_rules)],
                'zoning_snippet_ids': [(6, 0, list(set(triggered_snippets)))],
                'state': 'violation' if violation_found else 'approved',
            })

            zoning.message_post(body=_("Zoning evaluation completed. Result: %s" % zoning.state))


    # -------------------------
    # create sheet subtasks (PASS or FAIL)
    # returns list of created subtask records
    # -------------------------
    def _create_sheet_subtasks(self, rule, result_flag=True):
        Task = self.env['project.task']
        SheetMap = self.env['zoning.sheet.map']
        created_subtasks = []

        for zoning in self:
            for snippet in rule.snippet_ids:
                # get maps
                if getattr(snippet, 'sheet_map_id', False):
                    sheet_mappings = SheetMap.search([('id','=',snippet.sheet_map_id.id), ('active','=',True)])
                else:
                    sheet_mappings = SheetMap.search([('category','=',snippet.category), ('active','=',True)])
                if not sheet_mappings:
                    sheet_mappings = SheetMap.create({
                        'name': f"Auto Map for {snippet.category or 'other'}",
                        'category': snippet.category or 'other',
                        'sheet_code': 'Z-999',
                        'description': 'Auto-created fallback sheet',
                    })
                for sheet in sheet_mappings:
                    subtask = Task.create({
                        'name': f"[{sheet.sheet_code}] {snippet.name}",
                        'project_id': zoning.project_id.id,
                        'zoning_id': zoning.id,
                        'zoning_snippet_ids': [(4, snippet.id)],
                        'sheet_code': sheet.sheet_code,
                        'description': (
                            f"Result: {'PASS' if result_flag else 'FAIL'}\n"
                            f"Snippet: {snippet.name}\n"
                            f"Reference: {snippet.reference_code or ''}\n"
                            f"Action: {snippet.action_recommendation or ''}"
                        ),
                    })
                    created_subtasks.append(subtask)
        return created_subtasks


    # -------------------------
    # create parent SOP task and link subtasks (subtasks param list expected)
    # returns parent task
    # -------------------------
    def _create_violation_task_from_sop(self, rule, subtasks):
        Task = self.env['project.task']
        TaskChecklist = self.env['project.task.checklist']
        created_parent = False

        for zoning in self:
            try:
                sop = rule.sop_id
                # try to reuse existing parent for same zoning+rule+sop
                parent_task = Task.search([
                    ('sop_id','=', sop.id if sop else False),
                    ('zoning_id','=', zoning.id),
                    ('zoning_rule_id','=', rule.id),
                    ('project_id','=', zoning.project_id.id)
                ], limit=1)
                if not parent_task:
                    parent_name = f"[SOP] {sop.name if sop else 'Zoning SOP'} - {rule.name}"
                    parent_task = Task.create({
                        'name': parent_name,
                        'project_id': zoning.project_id.id,
                        'zoning_id': zoning.id,
                        'sop_id': sop.id if sop else False,
                        'zoning_rule_id': rule.id,
                        'description': (
                            f"SOP: {sop.name if sop else 'N/A'}\nRule: {rule.name}\n{rule.note or ''}"
                        ),
                    })
                # create checklist items from SOP template
                if sop and sop.checklist_template_ids:
                    lines = []
                    for tpl in sop.checklist_template_ids:
                        exists = TaskChecklist.search([('task_id','=',parent_task.id),('checklist_name','=',tpl.name)], limit=1)
                        if not exists:
                            TaskChecklist.create({
                                'task_id': parent_task.id,
                                'checklist_name': tpl.name,
                                'sop_id': sop.id,
                                'notes': tpl.notes or '',
                                'is_done': False
                            })
                # attach subtasks as children
                if subtasks:
                    # filter only ids
                    ids = [t.id for t in subtasks if t]
                    if ids:
                        parent_task.write({'child_ids': [(6,0, ids)]})
                created_parent = parent_task
                zoning.message_post(body=_("Created/Updated SOP task %s for rule %s" % (parent_task.name, rule.name)))
            except Exception as e:
                zoning.message_post(body=_("Error creating SOP task: %s" % e))
        return created_parent

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        self.message_post(body=_("Zoning record reset to draft."))

    def action_mark_approved(self):
        self.write({'state': 'approved'})
        self.message_post(body=_("Zoning record manually approved."))

    @api.onchange('land_area', 'building_area')
    def _onchange_calculate_far(self):
        for rec in self:
            if rec.land_area > 0 and rec.building_area > 0:
                rec.far = rec.building_area / rec.land_area