from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class WorkFlowEngineMixin(models.AbstractModel):
    _name = 'workflow.engine.mixin'
    _description = 'Workflow Trigger Engine'

    def _run_workflow_triggers(self, operation):
        try:
            model_name = self._name
            records = self if isinstance(self, models.Model) else self.browse([])

            _logger.info(f"Running workflow triggers for model: {model_name}, operation: {operation}, records: {records.ids}")

            for record in records:
                rules = self.env['workflow.rule'].search([
                    ('model_id.model', '=', model_name),
                    ('trigger_type', '=', operation),
                    ('active', '=', True)
                ])

                _logger.info(f"Found {len(rules)} workflow rule(s) for model {model_name} and operation {operation}.")

                for rule in rules:
                    try:
                        domain = safe_eval(rule.condition_domain or '[]')
                        if not record.filtered_domain(domain):
                            _logger.info(f"Record {record.id} skipped due to domain: {domain}")
                            continue

                        for action in sorted(rule.action_ids, key=lambda a: a.sequence):
                            try:
                                _logger.info(f"Processing action {action.name} (type: {action.action_type}) on record {record.id}")

                                # Calculate delay if defined
                                delay = timedelta()
                                if action.delay_unit == 'minutes':
                                    delay = timedelta(minutes=action.delay_number)
                                elif action.delay_unit == 'hours':
                                    delay = timedelta(hours=action.delay_number)
                                elif action.delay_unit == 'days':
                                    delay = timedelta(days=action.delay_number)

                                execute_at = fields.Datetime.now() + delay

                                if rule.execution_timing == 'immediate' and not delay:
                                    # Run now if no delay
                                    action.run_action(action, record)
                                else:
                                    # Queue for delayed or scheduled execution
                                    self.env['workflow.queue'].create({
                                        'rule_id': rule.id,
                                        'action_id': action.id,
                                        'model_name': model_name,
                                        'res_id': record.id,
                                        'state': 'pending',
                                        'execute_at': execute_at,
                                    })

                            except Exception as action_error:
                                _logger.error(f"Failed to handle action {action.name} for record {record.id}: {str(action_error)}")

                    except Exception as rule_error:
                        _logger.error(f"Failed to process rule {rule.name}: {str(rule_error)}")

        except Exception as e:
            _logger.error(f"Workflow trigger processing failed: {str(e)}")
            raise
