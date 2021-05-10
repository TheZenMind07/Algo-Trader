"use-strict";
$(document).ready(function () {
    setTimeout(function () {
        Morris.Donut({
            element: "morris-donut-chart-positions",
            data: [
                { label: "Download Sales", value: 12 },
                { label: "In-Store Sales", value: 30 },
                { label: "Mail-Order Sales", value: 20 }
            ],
            colors: ["#1de9b6", "#A389D4", "#04a9f5", "#1dc4e9"]
        });
        Morris.Donut({
            element: "morris-donut-chart-holdings",
            data: [
                { label: "Download Sales", value: 12 },
                { label: "In-Store Sales", value: 30 },
                { label: "Mail-Order Sales", value: 20 }
            ],
            colors: ["#1de9b6", "#A389D4", "#04a9f5", "#1dc4e9"]
        });

        Morris.Donut({
            element: "morris-donut-chart-mutualfund",
            data: [
                { label: "Download Sales", value: 12 },
                { label: "In-Store Sales", value: 30 },
                { label: "Mail-Order Sales", value: 20 }
            ],
            colors: ["#1de9b6", "#A389D4", "#04a9f5", "#1dc4e9"]
        });

        Morris.Donut({
            element: "morris-donut-chart-summary",
            data: [
                { label: "Download Sales", value: 12 },
                { label: "In-Store Sales", value: 30 },
                { label: "Mail-Order Sales", value: 20 }
            ],
            colors: ["#1de9b6", "#A389D4", "#04a9f5", "#1dc4e9"]
        });
    }, 700);
});
