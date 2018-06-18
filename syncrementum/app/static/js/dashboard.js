window.onload = function () {

var chart = new CanvasJS.Chart("chartContainer", {
	animationEnabled: true,
	title:{
		text: ""
	},
	axisY :{
		valueFormatString: ""
	},
	axisX: {

	},
	toolTip: {
		enabled: false
	},
	data: [{
		type: "stackedArea",
		showInLegend: false,
		//toolTipContent: "<span style=\"color:#4F81BC\"><strong>{name}: </strong></span> {y}",
		//name: "iOS",
		dataPoints: [
		{ x: 1, y: 3000 },
		{ x: 2, y: 7000 },
		{ x: 3, y: 10000 },
		{ x: 4, y: 14000 },
		{ x: 5, y: 23000 },
		{ x: 6, y: 31000 },
		{ x: 7, y: 42000 },
		{ x: 8, y: 56000 },
		{ x: 9, y: 64000 },
		{ x: 10, y: 81000 },
		{ x: 12, y: 105000 },
		{ x: 13, y: 105000 },
		{ x: 14, y: 105000 },
		{ x: 15, y: 105000 },
		{ x: 16, y: 105000 },
		{ x: 17, y: 105000 },
		{ x: 19, y: 105000 },
		{ x: 20, y: 105000 },
		{ x: 21, y: 105000 },
		{ x: 22, y: 105000 },
		{ x: 23, y: 105000 },
		{ x: 24, y: 105000 },
		{ x: 25, y: 105000 },
		{ x: 26, y: 105000 },
		{ x: 27, y: 105000 },
		{ x: 28, y: 105000 },
		{ x: 29, y: 105000 },
		{ x: 30, y: 105000 }
		]
	}]
});

//chart.render();


}