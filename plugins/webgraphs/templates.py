MAIN_PAGE = """
<html>
<head>
<title>Graphs!</title>
<script type="text/javascript"
	src="http://dygraphs.com/dygraph-combined.js"></script>

<style type="text/css">
.chart {
	width: 1000px;
	height: 600px;
	border-left: 4px solid #ccc;
	margin-top: 4ex;
}
p {
	max-width: 100ex;
}
</style>

</head>

<body>
	%(localHtml)s
	<p>Mouse over to see values; hover over annotations for details. Drag to zoom, double-click to zoom back out. Rendered by <a href="http://dygraphs.com/">Dygraphs</a>. (By default, graphs are zoomed to the last 48 hours.)</p>

%(chartDivsHtml)s
</body>

<script type="text/javascript">
var DEFAULT_WINDOW_MILLIS = 2 * 24 * 60 * 60 * 1000;
var NOW = new Date().valueOf();

var graphs = [];
var blockRedraw = false; // block while updating to avoid recursion
// see http://dygraphs.com/tests/synchronize.html
function synchronizeZooms(drawnGraph, firstDraw) {
	if (blockRedraw || firstDraw) {
		return;
	}
	blockRedraw = true;
	var xRange = drawnGraph.xAxisRange();
	for (var i = 0; i < graphs.length; i++) {
		if (graphs[i] == drawnGraph) {
			continue;
		}
		graphs[i].updateOptions({dateWindow: xRange});
	}
	blockRedraw = false;
}

function drawGraph(elementId, graphData, titleHtml, labels, annotations) {
	var g = new Dygraph(
		document.getElementById(elementId),
		graphData,
		{
			title: titleHtml,
			labels: labels,
			connectSeparatedPoints: true,
			drawGapEdgePoints: true,
			dateWindow:
				[NOW - DEFAULT_WINDOW_MILLIS, NOW],
			drawCallback: synchronizeZooms,
		});
	if (annotations) {
		g.setAnnotations(annotations);
	}
	graphs.push(g);
}

%(annotationsJs)s

%(drawCallsJs)s

</script>
</html>
"""

CHART_DIV = """\t<div id="%sGraph" class="chart"></div>"""

ANNOTATIONS = """
var %(name)sAnnotations = %(dataJs)s;
"""

DRAW_CALL = """
drawGraph('%(name)sGraph',
	%(dataJs)s,
	%(title)s,
	%(labelJs)s,
	%(name)sAnnotations);
"""
