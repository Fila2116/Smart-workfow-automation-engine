from odoo import models, fields

class TestWorkflowModel(models.Model):
    _name = "test.workflow.model"
    _inherit = ["mail.thread", "mail.activity.mixin", "workflow.engine.mixin"]
    _description = "Test Model for Workflow"

    name = fields.Char(string="Name", tracking=True)
    user_id = fields.Many2one('res.users',string = "user Id",default=lambda self: self.env.user,)

    def create(self, vals):
        records = super().create(vals)
        records._run_workflow_triggers('create')
        return records

    def write(self, vals):
        result = super().write(vals)
        self._run_workflow_triggers('write')
        return result

    def unlink(self):
        self._run_workflow_triggers('unlink')
        return super().unlink()
