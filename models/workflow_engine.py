from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

import logging
_logger = logging.getLogger(__name__)

class WorkFlowEngineMixin(models.AbstractModel):
    _name='workflow.engine.mixin'
    _description = 'workflow Trigger Engine'

    def _run_workflow_triggers(self, operation):
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
                except Exception as e:
                    _logger.warning(f"Invalid domain in rule {rule.name}: {e}")
                    continue

                for action in sorted(rule.action_ids, key=lambda a: a.sequence):
                    _logger.info(f"Processing action {action.name} (type: {action.action_type}) on record {record.id}")
                    if rule.execution_timing == 'immediate':
                        self.env['workflow.action'].run_action(action, record)
                    else:
                        self.env['workflow.queue'].create({
                            'rule_id': rule.id,
                            'action_id': action.id,
                            'model_name': model_name,
                            'res_id': record.id,
                            'state': 'pending'
                        })
                        _logger.info(f"Queued action {action.name} for record {record.id}")
