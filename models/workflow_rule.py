from odoo import models,fields

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
    ],string="Execution Timing",tracking=True,required=True)
    active =fields.Boolean(string="Active",default=True)