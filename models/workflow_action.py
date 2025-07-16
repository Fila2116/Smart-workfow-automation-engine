from odoo import models, fields
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
import logging
import requests
_logger = logging.getLogger(__name__)

class WorkFlowAction(models.Model):
    
    _name="workflow.action"
    _description="Smart Automation Action"
    
    

    name=fields.Char(string="Name" ,required=True)
    rule_id=fields.Many2one("workflow.rule",string="Rule",ondelete='cascade',required=True)
    action_type=fields.Selection(
        [('email',"Send an Email"),
        ('update',"Update an info"),
        ('assign',"Assign Record"),
        ('webhook','Call webhook'),
        ('create_record',"Create Related Record")],string="Action Type",tracking=True,required=True,
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
            elif action.action_type == 'webhook':
                url = params.get('url')
                payload = params.get('payload',{})

                if not url:
                    raise UserError("Webhook URL is missing in params.")

                #We are Replacing the fields from record into payload
                prepared_payload = {}
                for key,value in payload.items():
                    if isinstance (value,str) and hasattr(target_record,value):
                        prepared_payload[key] = getattr(target_record,value)
                    else:
                        prepared_payload[key] = value
                import requests
                response = requests.post(url, json=prepared_payload, timeout=5)
                log_vals['message'] = f"Webhook sent to {url} with status {response.status_code}: {response.text}"
            log_vals['state'] = 'success'
            log_vals['message'] = 'Action executed successfully.'

            elif action.action_type = 'create_record':
                target_model = params.get('model')
                values = params.get('values',{})

                if not target_model:
                    raise ValueError("Target model not specified for create_record action")
                
                filled_values = {}
                for field, val in values.items():
                    if isinstance(val,str) and hasattr(target_record, val):
                        filled_values[field] = getattr(target_value,val)
                    else:
                        filled_values[field] = val
                new_record = self.env[target_model].create(filled_values)
                _logger.info(f"--> Created related record {new_record._name} ID: {new_record.id}")
        except Exception as e:
            log_vals['state'] = 'error'
            log_vals['message'] = str(e)
            _logger.error(f"--> Action execution failed: {str(e)}")

        self.env['workflow.log'].create(log_vals)
 
            