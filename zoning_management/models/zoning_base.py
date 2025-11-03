from odoo import api, models, fields, _

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
        return super(ProjectZoning, self).create(vals)

    @api.depends('evaluation_log_ids')
    def _compute_violation_count(self):
        for rec in self:
            rec.violation_count = len(rec.evaluation_log_ids.filtered(lambda l: l.result in ['no_match', 'task_created']))

    def action_evaluate_rules(self):
        Rule = self.env['project.zoning.rule']
        Log = self.env['project.zoning.evaluation.log']

        for zoning in self:
            zoning.evaluation_log_ids.unlink() 
            triggered_rules = []
            triggered_snippets = []
            violation_found = False

            project_type = getattr(zoning.project_id, 'project_type_id', False)
            rules_domain = [('active', '=', True)]
            if project_type:
                rules_domain.append(('project_type_id', '=', project_type.id))
            rules = Rule.search(rules_domain)

            operator_symbols = {
                'gt': '>',
                'lt': '<',
                'ge': '≥',
                'le': '≤',
                'eq': '=',
                'ne': '≠',
            }

            for rule in rules:
                field_name = rule.field_id.name if rule.field_id else None
                field_value = getattr(zoning, field_name, None) if field_name else None
                result_flag = False
                log_message = ""
                task_ref = False

                try:
                    result_flag = rule._evaluate_condition(zoning)
                except Exception as e:
                    log_message = f"Error evaluating rule: {e}"

                if not log_message:
                    log_message = f"{field_name}: {field_value} (Expected {operator_symbols.get(rule.operator, rule.operator)} {rule.value})"

                log_vals = {
                    'evaluated_by': self.env.user.id,
                    'zoning_id': zoning.id,
                    'project_id': zoning.project_id.id,
                    'rule_id': rule.id,
                    'field_name': field_name or 'N/A',
                    'field_value': field_value or 'N/A',
                    'operator': operator_symbols.get(rule.operator, rule.operator),
                    'expected_value': rule.value or '',
                    'message': log_message,
                }

                # === 1️⃣ Buat Subtask/Sheet untuk semua hasil zoning (PASS dan FAIL) ===
                zoning._create_sheet_subtasks(rule, result_flag)

                if not result_flag:
                    violation_found = True
                    triggered_rules.append(rule.id)
                    triggered_snippets += rule.snippet_ids.ids

                    # Jika rule gagal dan auto_action create_task → buat task violation
                    if rule.auto_action == 'create_task':
                        task_ref = zoning._create_violation_task(rule)
                        log_vals.update({
                            'result': 'task_created',
                            'task_id': task_ref[0].id if task_ref else False,
                            'message': f"Violation detected — task created for rule {rule.name}. {log_message}",
                        })
                    else:
                        log_vals['result'] = 'no_match'
                else:
                    log_vals['result'] = 'match'

                Log.create(log_vals)

            zoning.write({
                'zoning_rule_ids': [(6, 0, triggered_rules)],
                'zoning_snippet_ids': [(6, 0, list(set(triggered_snippets)))],
                'state': 'violation' if violation_found else 'approved',
            })

            zoning.message_post(body=_("Zoning evaluation completed. Result: %s" % zoning.state))


    def _create_sheet_subtasks(self, rule, result_flag):
        """Create zoning sheet subtasks for documentation (for both PASS and FAIL results)."""
        Task = self.env['project.task']
        SheetMap = self.env['zoning.sheet.map']
        created_subtasks = []

        for zoning in self:
            for snippet in rule.snippet_ids:
                sheet_mappings = SheetMap.search([
                    ('id', '=', snippet.sheet_map_id.id),
                    ('active', '=', True)
                ])
                if not sheet_mappings:
                    sheet_mappings = SheetMap.create({
                        'name': f"Auto Map for {snippet.category}",
                        'category': snippet.sheet_map_id.category,
                        'sheet_code': 'Z99',
                        'description': 'Auto-created fallback sheet',
                    })

                # buat subtask
                for sheet in sheet_mappings:
                    subtask = Task.create({
                        'name': f"[{sheet.sheet_code}] {snippet.name}",
                        'project_id': zoning.project_id.id,
                        'parent_id': False,  # subtask berdiri sendiri jika bukan violation
                        'zoning_id': zoning.id,
                        # 'zoning_snippet_id': snippet.id,
                        'sheet_code': sheet.sheet_code,
                        'description': (
                            f"Result: {'PASS ✅' if result_flag else 'FAIL ❌'}\n"
                            f"Snippet: {snippet.name}\n"
                            f"Reference: {snippet.reference_code or ''}\n"
                            f"Category: {snippet.sheet_map_id.category}\n"
                            f"City/State: {snippet.city or ''}, {snippet.state or ''}\n"
                            f"Action: {snippet.action_recommendation or 'Review requirement.'}"
                        ),
                    })
                    created_subtasks.append(subtask)

            if created_subtasks:
                zoning.message_post(
                    body=_("📄 Created %s zoning sheet subtasks for rule <b>%s</b>." %
                        (len(created_subtasks), rule.name))
                )
        return created_subtasks

    # ===========================
    # CREATE TASK
    # ===========================
    def _create_violation_task(self, rule):
        Task = self.env['project.task']
        SheetMap = self.env['zoning.sheet.map']
        created_tasks = []

        for zoning in self:
            try:
                field_val = getattr(zoning, rule.field_id.name, 'N/A') if rule.field_id else 'N/A'
                project_name = zoning.project_id.display_name or 'Unnamed Project'
                phase_name = zoning.phase_id.display_name if zoning.phase_id else ''
                snippet_titles = ', '.join(rule.snippet_ids.mapped('name')) or 'No Snippet Linked'

                task_name = f"[Zoning Violation] - {project_name} - {rule.name}"
                if phase_name:
                    task_name += f" ({phase_name})"

                parent_task = Task.create({
                    'name': task_name,
                    'project_id': zoning.project_id.id,
                    'zoning_id': zoning.id,
                    'description': (
                        f"<b>Zoning Violation Detected</b><br/>"
                        f"<b>Rule:</b> {rule.name}<br/>"
                        f"<b>Expected:</b> {rule.operator} {rule.value}<br/>"
                        f"<b>Found:</b> {field_val}<br/>"
                        f"<b>Legal Reference:</b> {rule.legal_reference or 'N/A'}<br/>"
                        f"<b>Snippets:</b> {snippet_titles}<br/><br/>"
                        f"<b>Action Required:</b> {rule.note or 'Please review compliance and update drawings.'}"
                    ),
                })
                created_tasks.append(parent_task)

                for snippet in rule.snippet_ids:
                    sheet_mappings = SheetMap.search([
                        ('id', '=', snippet.sheet_map_id.id),
                        ('active', '=', True)
                    ])
                    if not sheet_mappings:
                        sheet_mappings = SheetMap.create({
                            'name': f"Auto Map ({snippet.category})",
                            'category': snippet.category,
                            'sheet_code': 'Z99',
                            'description': 'Auto-created fallback sheet',
                        })

                    for sheet in sheet_mappings:
                        subtask_vals = {
                            'name': f"[{sheet.sheet_code}] {snippet.name}",
                            'project_id': zoning.project_id.id,
                            'parent_id': parent_task.id,  
                            'zoning_id': zoning.id,
                            # 'zoning_snippet_id': snippet.id,
                            'sheet_code': sheet.sheet_code,
                            'description': (
                                f"📄 <b>Snippet:</b> {snippet.name}<br/>"
                                f"<b>Reference:</b> {snippet.reference_code or ''}<br/>"
                                f"<b>Category:</b> {snippet.category}<br/>"
                                f"<b>City/State:</b> {snippet.city or ''}, {snippet.state or ''}<br/>"
                                f"<b>Required Action:</b> {snippet.action_recommendation or 'Review and verify compliance.'}"
                            ),
                        }
                        subtask = Task.create(subtask_vals)
                        created_tasks.append(subtask)

                if created_tasks:
                    child_tasks = [t.id for t in created_tasks if t.id != parent_task.id]
                    if child_tasks:
                        parent_task.write({'child_ids': [(6, 0, child_tasks)]})

                zoning.message_post(
                    body=_(
                        f"Created violation task <b>{parent_task.name}</b> "
                        f"with {len(created_tasks)-1} subtasks (linked to zoning rule <b>{rule.name}</b>)."
                    )
                )

            except Exception as e:
                zoning.message_post(
                    body=_("❌ Error creating violation task for rule %s: %s" % (rule.name, str(e)))
                )

        return created_tasks

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