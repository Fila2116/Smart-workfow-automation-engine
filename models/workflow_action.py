from odoo import models, fields, api,_
from odoo.tools.safe_eval import safe_eval
import logging
import requests
from odoo.exceptions import UserError
import re

_logger = logging.getLogger(__name__)

def _interpolate_value(value, record):
        if isinstance(value, str):
            matches = re.findall(r'\$\{([^\}]+)\}', value)
            for match in matches:
                parts = match.split('.')
                attr = record
                for part in parts:
                    attr = getattr(attr, part, '')
                value = value.replace('${%s}' % match, str(attr))
        return value

class WorkFlowAction(models.Model):
    _name = "workflow.action"
    _description = "Smart Automation Action"
    
    name = fields.Char(string="Name", required=True)
    rule_id = fields.Many2one("workflow.rule", string="Rule", ondelete='cascade', required=True)
    action_type = fields.Selection(
        [('email', "Send an Email"),
         ('update', "Update an info"),
         ('assign', "Assign Record"),
         ('webhook', 'Call webhook'),
         ('create_record', "Create Related Record")],
        string="Action Type", tracking=True, required=True,
    )
    params = fields.Text(string="Parameters", widget="json_widget")
    sequence = fields.Integer(string="Sequence", default=10)
    delay_number = fields.Integer(string = "Delay",help="Number of time units to delay this action",default=0)
    delay_unit = fields.Selection(
        [
            ('minutes',"Minutes"),
            ('hours',"Hours"),
            ('days',"Days"),
        ],
        string="Delay unit",
        help = "Unit of time for delay",
        default = 'minutes',
    )
    

    
    @api.model
    def run_action(self, action, target_record):
        _logger.warning(f"--> Running action: {action.name} on record: {target_record.display_name} [ID: {target_record.id}]")
        log_vals = {
            'rule_id': action.rule_id.id,
            'action_id': action.id,
            'model_name': target_record._name,
            'res_id': target_record.id,
            'state': 'error',  # Default to error, will be updated to success if execution succeeds
            'message': 'Action execution started'
        }

        try:
            params = safe_eval(action.params or '{}')
            _logger.warning(f"--> Params parsed: {params}")

            if action.action_type == 'email':
                body = params.get('body', 'NO content')
                target_record.message_post(body=body)
                _logger.warning(f"--> Posted message: {body}")
                log_vals.update({
                    'state': 'success',
                    'message': 'Email posted successfully'
                })
                
            elif action.action_type == 'update':
                values = params.get('values', {})
                target_record.write(values)
                log_vals.update({
                    'state': 'success',
                    'message': f"Record updated with values: {values}"
                })
                
            elif action.action_type == 'assign':
                user_id = params.get('user_id')
                if user_id:
                    target_record.write({'user_id': user_id})
                    log_vals.update({
                        'state': 'success',
                        'message': f"Record assigned to user ID: {user_id}"
                    })
                else:
                    log_vals.update({
                        'message': 'No user_id specified in parameters'
                    })
                    
            elif action.action_type == 'webhook':
                url = params.get('url')
                payload = params.get('payload', {})

                if not url:
                    raise UserError("Webhook URL is missing in params.")

                # Replacing the fields from record into payload
                prepared_payload = {}
                for key, value in payload.items():
                    if isinstance(value, str) and hasattr(target_record, value):
                        prepared_payload[key] = getattr(target_record, value)
                    else:
                        prepared_payload[key] = value
                        
                response = requests.post(url, json=prepared_payload, timeout=5)
                log_vals.update({
                    'state': 'success',
                    'message': f"Webhook sent to {url} with status {response.status_code}: {response.text}"
                })

            elif action.action_type == 'create_record':
                target_model = params.get('model')
                values = params.get('values', {})

                if not target_model:
                    raise ValueError("Target model not specified for create_record action")
                
                _logger.warning(f"Initial values before processing: {values}")
                
                filled_values = {}
                for field, val in values.items():
                    try:
                        if isinstance(val, list):  # Handle x2many fields
                            new_val = []
                            for item in val:
                                if isinstance(item, list):  # This is a command list
                                    # Process command tuple (like [6, 0, [ids]])
                                    if len(item) >= 3 and isinstance(item[2], list):
                                        command = item[0]
                                        link = item[1]
                                        ids = item[2]
                                        
                                        processed_ids = []
                                        for id_val in ids:
                                            if isinstance(id_val, str) and id_val.startswith('${') and id_val.endswith('}'):
                                                # Evaluate the field reference
                                                field_expr = id_val[2:-1]
                                                try:
                                                    field_value = _interpolate_value(field_expr, target_record)
                                                    if hasattr(field_value, 'id'):
                                                        processed_ids.append(field_value.id)
                                                    else:
                                                        processed_ids.append(int(field_value))
                                                except Exception as e:
                                                    _logger.error(f"Failed to interpolate {id_val}: {str(e)}")
                                                    processed_ids.append(False)  # Use False as fallback
                                            else:
                                                processed_ids.append(id_val)
                                        
                                        new_val.append([command, link, processed_ids])
                                    else:
                                        new_val.append(item)
                                else:
                                    new_val.append(item)
                            filled_values[field] = new_val
                        else:
                            filled_values[field] = _interpolate_value(val, target_record)
                    except Exception as e:
                        _logger.error(f"Error processing field {field}: {str(e)}")
                        raise

                _logger.warning(f"Creating record with values: {filled_values}")
                
                try:
                    new_record = self.env[target_model].create(filled_values)
                    _logger.warning(f"Successfully created record: {new_record} (ID: {new_record.id})")
                    log_vals.update({
                        'state': 'success',
                        'message': f"Related record {new_record._name} (ID: {new_record.id}) created successfully."
                    })
                except Exception as e:
                    _logger.error(f"Failed to create record: {str(e)}")
                    log_vals.update({
                        'state': 'error',
                        'message': f"Failed to create record: {str(e)}"
                    })
                    raise

        except Exception as e:
            _logger.error(f"Action execution failed: {str(e)}", exc_info=True)
            log_vals.update({
                'state': 'error',
                'message': str(e)
            })

        self.env['workflow.log'].create(log_vals)