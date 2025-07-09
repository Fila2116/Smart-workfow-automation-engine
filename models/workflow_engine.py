from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class WorkFlowEngineMixin(models.AbstractModel):
    _name='workflow.engine.mixin'
    _description = 'workflow Trigger Engine'

    def _run_workflow_triggers(self,operation):
        model_name=self.name
        records = self if isinstance(self,models.Model) else self.browse([])

        for record in records:
            rules=self.env['workflow.rule'].search([
                ('model_id.model','=',model_name),
                ('trigger_type','=',operation),
                ('active','=',True)
            ])

            for rule in rules:
                try:
                    domain = safe_eval(rule.condition_domain or '[]')
                    if not record.filtered_domain(domain):
                        continue 
                except Exception:
                    continue 

                for action in sorted(rule.action_ids,key=lambda a : a.sequence):
                    if rule.execution_timing == 'immediate':
                        self.env['workflow.action'].run_action(action,record)
                    else:
                        self.env['workflow.queue'].create({
                            'rule_id':rule.id,
                            'action_id':action.id,
                            'model_name':model_name,
                            'res_id':record.id,
                            'state':'pending'
                        })