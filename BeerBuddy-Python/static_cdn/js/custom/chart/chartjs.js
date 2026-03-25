$(function () {
    "use strict";
    // Bar chart
    new Chart(document.getElementById("bar-chart"), {
        type: 'bar',
        data: {
            labels: ["2010", "2011", "2012", "2013", "2015"],
            datasets: [
                {
                    label: "Users in (Hunderd)",
                    backgroundColor: ["#03a9f4", "#e861ff", "#08ccce", "#e2b35b", "#e40503"],
                    data: [78, 67, 54, 84, 73]
			}
		  ]
        },
        options: {
            legend: {
                display: false
            },
            title: {
                // display: true,
                // text: 'Predicted world population (millions) in 2050'
            }
        }
    });

    // New chart
    new Chart(document.getElementById("pie-chart"), {
        type: 'pie',
        data: {
            labels: ["Africa", "Asia", "Europe", "Latin America"],
            datasets: [{
                label: "Total Check Ins",
                backgroundColor: ["#36a2eb", "#ff6384", "#4bc0c0", "#ffcd56", "#07b107"],
                data: [2478, 5267, 3734, 2784]
		  }]
        },
        options: {
            title: {
                display: true,
                text: 'Total Check Ins Today'
            }
        }
    });


});
