from odoo import models, fields

class TestWorkflowModel(models.Model):
    _name = "test.workflow.model"
    _inherit = ["mail.thread", "mail.activity.mixin", "workflow.engine.mixin"]
    _description = "Test Model for Workflow"

    name = fields.Char(string="Name", tracking=True)
