// /** @odoo-module **/

// import { registry } from "@web/core/registry";
// import { useService } from "@web/core/utils/hooks";
// import { Layout } from "@web/search/layout";
// import { Component, onWillStart, useRef, onMounted, useState } from "@odoo/owl";
// console.log("1 - Module imports completed");

// export class WorkflowDashboard extends Component {
//     static template = "workflow_dashboard_template";
//     static components = { Layout };

//     setup() {
//         console.log("3 - Component setup started")
//         this.rpc = useService("rpc");
//         this.state = useState({
//             kpi_data: {},
//             loading: true,
//         });
//         this.chartRef = useRef("chart");

//         onWillStart(async () => {
//             try {
//                 const data = await this.rpc("/web/dataset/call_kw/workflow.log/get_dashboard_data", {
//                     model: "workflow.log",
//                     method: "get_dashboard_data",
//                     args: [],
//                     kwargs: {},
//                 });
//                 this.state.kpi_data = data;
//                 this.state.loading = false;
//             } catch (error) {
//                 console.error("Error loading dashboard data:", error);
//                 this.state.loading = false;
//             }
//         });

//         onMounted(() => this.renderChart());
//     }

//     renderChart() {
//         if (!this.chartRef.el || !window.Chart) return;
        
//         const ctx = this.chartRef.el.getContext("2d");
//         new Chart(ctx, {
//             type: "bar",
//             data: {
//                 labels: Object.keys(this.state.kpi_data.by_rule || {}),
//                 datasets: [{
//                     label: "Executions per Rule",
//                     data: Object.values(this.state.kpi_data.by_rule || {}),
//                     backgroundColor: "#3e95cd",
//                     barThickness: 40,
//                 }],
//             },
//             options: {
//                 responsive: true,
//                 plugins: {
//                     legend: { display: true, position: "top" },
//                     title: { display: true, text: "Workflow Rule Executions" },
//                 },
//             },
//         });
//     }
// }
// console.log("something")
// registry.category("actions").add("workflow_dashboard_client", WorkflowDashboard);