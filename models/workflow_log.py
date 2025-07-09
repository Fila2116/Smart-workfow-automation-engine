from odoo import models, fields
from datetime import datetime

class WorkflowLog(models.Model):
    _name = "workflow.log"
    _description = "Workflow Execution Log"

    timestamp = fields.Datetime(string="Timestamp", default=lambda self: fields.Datetime.now())
    rule_id = fields.Many2one("workflow.rule", required=True, ondelete="cascade")
    action_id = fields.Many2one("workflow.action", required=True, ondelete="cascade")
    model_name = fields.Char(required=True)
    res_id = fields.Integer(string="Record ID", required=True)
    state = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], required=True)
    message = fields.Text(string="Log Message")
