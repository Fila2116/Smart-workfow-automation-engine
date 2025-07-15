from odoo import models,fields,api,_
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval


class WorkFlowRule(models.Model):
    _name = "workflow.rule"
    _description = "Smart Automation Rule"

    name= fields.Char(string="Name",required=True,)
    model_id = fields.Many2one("ir.model",string="Model to watch",required=True,ondelete='cascade')
    action_ids = fields.One2many(
        "workflow.action",inverse_name="rule_id",string="Actions",
    )
    trigger_type=fields.Selection([
        ("create","On Create"),
        ("write","On Update"),
        ("unlink","On Delete")
    ],string="Trigger Type",tracking=True,required=True)
    condition_domain = fields.Text(string="Condition domain")
    execution_timing = fields.Selection([
        ("immediate","Immediate"),
        ("scheduled","Scheduled"),
    ],string="Execution Timing",tracking=True,required=True,default="immediate")
    active =fields.Boolean(string="Active",default=True)
    interval_number = fields.Integer(
        string = "Every",
        default = 1,
        help = "Repeat every (interval)"
    )
    interval_type = fields.Selection(
        [
            ('minutes', 'Minutes'),
            ('hours', 'Hours'),
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months')
        ],
        string='Interval Unit',
        default='days',
        help="Interval unit"
    )
    next_execution = fields.Datetime(
        string='Next Execution',
        compute='_compute_next_execution',
        store=True,
        help="When this rule should run next"
    )

    def _cron_process_scheduled_rules(self):
        """Process rules that are set to execute on schedule"""
        now = fields.Datetime.now()
        rules = self.search([
            ('execution_timing', '=', 'scheduled'),
            ('next_execution', '<=', now),
            ('active', '=', True)
        ])
        
        for rule in rules:
            # Find all records that match the rule's conditions
            target_model = self.env[rule.model_id.model]
            domain = safe_eval(rule.condition_domain or '[]')
            records = target_model.search(domain)
            
            # Queue the actions
            for record in records:
                for action in rule.action_ids:
                    self.env['workflow.queue'].create({
                        'rule_id': rule.id,
                        'action_id': action.id,
                        'model_name': record._name,
                        'res_id': record.id,
                        'state': 'pending'
                    })
            
            # Schedule next execution
            rule._compute_next_execution()

    @api.depends('interval_number', 'interval_type', 'execution_timing')
    def _compute_next_execution(self):
        now = fields.Datetime.now()
        for rule in self:
            if rule.execution_timing == 'scheduled':
                rule.next_execution = now + relativedelta(
                    **{rule.interval_type: rule.interval_number}
                )
            else:
                rule.next_execution = False

    