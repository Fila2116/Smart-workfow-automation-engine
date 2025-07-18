from odoo import models,fields
from datetime import datetime

class WorkflowQueue(models.Model):
    _name="workflow.queue"
    _description="Workflow Queue"

    rule_id = fields.Many2one("workflow.rule",string="Rule" ,ondelete="cascade",required=True)
    action_id=fields.Many2one("workflow.action" ,string="Action" ,ondelete="cascade",required=True)
    model_name = fields.Char(string="Model" ,required=True)
    res_id = fields.Integer(string="Id" ,required=True)
    state = fields.Selection([('pending',"Pending"),
    ("done","Done"),("error","Error")],string="Status",tracking=True,required=True)
    error_message = fields.Text(string="Error message")
    execute_at = fields.Datetime(string="execute_at",help = "When to execute the action",defualt=fields.Datetime.now)

    def run_pending_actions(self):
        now = fields.Datetime.now()
        pending_jobs = self.search([('state','=','pending'),('scheduled_at','<=',now)],limit = 100)
        for job in pending_jobs:
            try:
                target = self.env[job.model_name].browse(job.res_id)
                if not target.exists():
                    raise UserError("Target record does not exist.")
                self.env['workflow.action'].run_action(job.action_id,target)
                job.write({'state':'done'})

            except Exception as e:
                    job.write({'state':'error','error_message':str(e)})