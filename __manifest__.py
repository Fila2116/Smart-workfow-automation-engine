{
    "name":"Smart Workflow Automation Engine",
    "version":"1.0",
    "category":"Tools",
    "summary":"Flexible rule-based automation engine for odoo",
    'description':"Trigger custom actions on model events with conditions",
    "author":"Filimon Tesfaye",
    "depends":['base',"mail","web"],
    "assets":{
        'web.assets_backend':[
            # 'static/lib/Chart/Chart.js',
            # 'static/src/js/workflow_dashboard.js',
            # 'static/src/xml/workflow.xml',

        ]
    },
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/workflow_rule_views.xml',
        'views/workflow_action_views.xml',
        'views/workflow_log_views.xml',
        'views/workflow_queue_views.xml',
        'views/test_workflow_model_views.xml',
        # 'views/workflow_dashboard_action.xml',
        'views/menu.xml',
        'data/workflow_cron.xml',
        
    ],
    'installable':True,
    'application':True,

}