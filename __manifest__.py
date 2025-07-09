{
    "name":"Smart Workflow Automation Engine",
    "version":"1.0",
    "category":"Tools",
    "summary":"Flexible rule-based automation engine for odoo",
    'description':"Trigger custom actions on model events with conditions",
    "author":"Filimon Tesfaye",
    "depends":['base',"mail"],
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/workflow_rule_views.xml',
        'views/workflow_action_views.xml',
        'views/workflow_log_views.xml',
        'views/workflow_queue_views.xml',
        'views/menu.xml',
        # 'data/workflow_cron.xml',
        
    ],
    'installable':True,
    'application':True,

}