from odoo import models, fields
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

class WorkFlowAction(models.Model):
    
    _name="workflow.action"
    _description="Smart Automation Action"
    
    

    name=fields.Char(string="Name" ,required=True)
    rule_id=fields.Many2one("workflow.rule",string="Rule",ondelete='cascade',required=True)
    action_type=fields.Selection(
        [('email',"Send an Email"),
        ('update',"Update an info"),
        ('assign',"Assign Record")],string="Action Type",tracking=True,required=True,
    )
    params = fields.Text(string="Parameters",widget="json_widget")
    sequence= fields.Integer(string ="Sequence",default=10)

    def run_action(self, action, target_record):
        _logger.warning(f"--> Running action: {action.name} on record: {target_record.display_name} [ID: {target_record.id}]")
        log_vals = {
            'rule_id': action.rule_id.id,
            'action_id': action.id,
            'model_name': target_record._name,
            'res_id': target_record.id,
        }

        try:
            params = safe_eval(action.params or '{}')
            _logger.warning(f"--> Params parsed: {params}")

            if action.action_type == 'email':
                body = params.get('body', 'NO content')
                target_record.message_post(body=body)
                _logger.warning(f"--> Posted message: {body}")
            elif action.action_type == 'update':
                target_record.write(params.get('values', {}))
            elif action.action_type == 'assign':
                user_id = params.get('user_id')
                if user_id:
                    target_record.write({'user_id': user_id})
            log_vals['state'] = 'success'
            log_vals['message'] = 'Action executed successfully.'
        except Exception as e:
            log_vals['state'] = 'error'
            log_vals['message'] = str(e)
            _logger.error(f"--> Action execution failed: {str(e)}")

        self.env['workflow.log'].create(log_vals)
 
            