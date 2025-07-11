from odoo import models, fields,api,_
from datetime import datetime

class WorkflowLog(models.Model):
    _name = "workflow.log"
    _description = "Workflow Execution Log"
    _order = 'create_date desc'

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
    
    @api.model
    def get_dashboard_date(self):
        success_count = self.search_count([('state','=','success')])
        error_count = self.search_count([('state',"=","error")])
        total = success_count + error_count

        rule_data = self.read_group(
            domain = [],
            fields = ['rule_id'],
            groupby = ['rule_id']
        )

        rule_counts = {
            self.env["workflow.rule"].browse(data['rule.id'][0]).name : data['rule_id_count']
            for data in rule_data if data['rule_id']
        }

        return {
            'success_count':success_count,
            "error_count":error_count,
            'total':total,
            'by_rule':rule_counts,
        }

    