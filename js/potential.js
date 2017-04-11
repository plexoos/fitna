
var nPoints = 50;
var x_min = -100, x_max = 100;
var derivativeDelta = 0.0001;
var gamma = 1;

var coords = [-70, -66, -68, -65, -63, -25, 10, 15, 12, 9, 60];



function createDataPoints( coords )
{
  var dataPoints = [];
  var nPoints = coords.length;

  for (var i = 0; i < nPoints; i++)
  {
    dataPoints.push( new DataPoint1D(coords[i], DataPoint1D.gWidth, -1) );
  }

  return dataPoints;
}



function createProbes(nProbes = 1)
{
  var probes = [];

  for (var i = 0; i < nProbes; i++)
  {
    var x = Math.floor(Math.random() * (x_max - x_min)) + x_min;

    probes.push( new DataPoint1D(x, 100, +1) );
  }

  return probes;
}



function getCoords( dataPoints )
{
  var coords = { x: [], y: [] };

  for (var i = 0; i < dataPoints.length; i++)
  {
    coords.x.push(dataPoints[i].x);
    coords.y.push(0);
  }

  return coords;
}



function updatePotentials(dataPoints, probes)
{
  // Update global width common to all dataPoints
  if ( Math.abs(DataPoint1D.gWidth - DataPoint1D.gWidthMax) < Math.abs(DataPoint1D.gWidthMax * DataPoint1D.gWidthDelta) ||
       Math.abs(DataPoint1D.gWidth - DataPoint1D.gWidthMin) < Math.abs(DataPoint1D.gWidthMin * DataPoint1D.gWidthDelta) )
  {
    DataPoint1D.gWidthDelta *= -1;
  }

  DataPoint1D.gWidth += DataPoint1D.gWidth * DataPoint1D.gWidthDelta;

  for (var iPoint = 0; iPoint < dataPoints.length; iPoint++)
  {
    var dataPoint = dataPoints[iPoint];
 
    dataPoint.width = DataPoint1D.gWidth;

    // Now calculate the potential created by the probes at this data point
    // location. With it we can updated the strength (i.e. amplitude) of the
    // data point
    var probePotential = 0;

    for (var iProbe = 0; iProbe < probes.length; iProbe++)
    {
      var probe = probes[iProbe];

      probePotential += probe.calculatePotential(dataPoint.x);
    }

    //dataPoint.amplitude = (1 - probePotential*0.30);


    // The following modifier would be used to update individual widths
    //dataPoints[iPoint].updatePotential();
  }
}



function calculateProbesXY(probes, dataPoints)
{
  var probesXY = [];
  var probePositions = {x: [], y: []};

  for (var iProbe = 0; iProbe < probes.length; iProbe++)
  {
    var probe = probes[iProbe];

    var totalPotential = 0;
    var totalPotential_mdelta = 0;
    var totalPotential_pdelta = 0;
    var variance = 0;

    // Calculate position of each probe using the overall potential
    for (var iPoint = 0; iPoint < dataPoints.length; iPoint++)
    {
      var dataPoint = dataPoints[iPoint];
      var potential = dataPoint.calculatePotential(probe.x);

      totalPotential += potential;

      totalPotential_mdelta += dataPoint.calculatePotential(probe.x - derivativeDelta);
      totalPotential_pdelta += dataPoint.calculatePotential(probe.x + derivativeDelta);

      // Calculate the variance
      var delta_x = probe.x - dataPoint.x;
      variance += delta_x * delta_x * potential;
    }

    var totalPotentialDerivative = (totalPotential_pdelta - totalPotential_mdelta) * 0.5 / derivativeDelta;

    // Update the probe position and its width
    probe.x -= totalPotentialDerivative * gamma * DataPoint1D.gWidth * 0.5;
    probe.width = Math.sqrt(variance / totalPotential);
    if (probe.width < 1) probe.width = 1;

    probePositions.x.push(probe.x);
    probePositions.y.push(0);

    // Build curves for probes
    var probePotential = {x: [], y: []};

    var nPointsSum = 10*nPoints;

    for (var i = 0; i < nPointsSum; i++)
    {
      var min_x = probe.x - 5*probe.width;
      var max_x = probe.x + 5*probe.width;
      var x = min_x + (max_x - min_x)*i/nPointsSum;
      var y = probe.calculatePotential(x);

      probePotential.x.push(x);
      probePotential.y.push(y);
    }

    probesXY.push( {x: probePotential.x, y: probePotential.y, mode: 'lines', line: {color: 'rgb(0, 100, 0)'} } );
  }

  probesXY.push( { x: probePositions.x, y: probePositions.y, mode: 'markers', marker: {size: 15, color: 'rgb(0, 200, 0)'} } );

  return probesXY;
}



function calculatePotentials(dataPoints, probes)
{
  // add the overall potential
  var totalPotentialXY = {x: [], y: []};
  var modifPotentialXY = {x: [], y: []};
  var derivativeXY     = {x: [], y: []};
  var varianceXY       = {x: [], y: []};

  var nPointsSum = 10*nPoints;
  var maxAbsPotential = 0;
  var maxAbsPotentialModif = 0;
  var maxAbsDerivative = 0;
  var maxAbsVariance = 0;

  for (var i = 0; i < nPointsSum; i++)
  {
    var x = x_min + (x_max - x_min)*i/nPointsSum;

    var totalPotential = 0;
    var modifPotential = 0;
    var totalPotential_mdelta = 0;
    var totalPotential_pdelta = 0;
    var variance = 0;

    for (var iPoint = 0; iPoint < dataPoints.length; iPoint++)
    {
      var dataPoint = dataPoints[iPoint];
      var potential = dataPoint.calculatePotential(x);

      totalPotential += potential;

      // Calculate modified potential by scaling the potential of the data point
      for (var iProbe = 0; iProbe < probes.length; iProbe++)
      {
        var probe = probes[iProbe];
        //dataPoint.amplitude = (1 - probePotential*0.30);
        // temporarily scale the amplitude of the dataPoint potential
        var savedAmplitude = dataPoint.amplitude;
        dataPoint.amplitude *= (1 - probe.calculatePotential(dataPoint.x) );
        var potentialModif = dataPoint.calculatePotential(x);
        // restore dataPoint
        dataPoint.amplitude = savedAmplitude;
      }

      modifPotential += potentialModif;

      totalPotential_mdelta += dataPoint.calculatePotential(x - derivativeDelta);
      totalPotential_pdelta += dataPoint.calculatePotential(x + derivativeDelta);

      // Calculate the variance
      var delta_x = x - dataPoint.x;
      variance += delta_x * delta_x * potential;
    }

    var totalPotentialDerivative = (totalPotential_pdelta - totalPotential_mdelta) * 0.5 / derivativeDelta;

    totalPotentialXY.x.push(x);
    totalPotentialXY.y.push(totalPotential);

    modifPotentialXY.x.push(x);
    modifPotentialXY.y.push(modifPotential);

    derivativeXY.x.push(x);
    derivativeXY.y.push(totalPotentialDerivative);

    varianceXY.x.push(x);
    varianceXY.y.push( Math.sqrt(variance / totalPotential) );

    if (Math.abs(totalPotential) > maxAbsPotential)
      maxAbsPotential = Math.abs(totalPotential);

    if (Math.abs(modifPotential) > maxAbsPotentialModif)
      maxAbsPotentialModif = Math.abs(modifPotential);

    if (Math.abs(totalPotentialDerivative) > maxAbsDerivative)
      maxAbsDerivative = Math.abs(totalPotentialDerivative);

    if (Math.abs(variance) > maxAbsVariance)
      maxAbsVariance = Math.abs(variance);
  }

  // Rescale total potential values
  for (var i = 0; i < totalPotentialXY.y.length; i++)
  {
    totalPotentialXY.y[i] = totalPotentialXY.y[i] / maxAbsPotential;
    modifPotentialXY.y[i] = modifPotentialXY.y[i] / maxAbsPotentialModif;

    derivativeXY.y[i] = derivativeXY.y[i] / maxAbsDerivative;

    varianceXY.y[i] = varianceXY.y[i] / maxAbsVariance;
  }


  var xyData = [];

  xyData.push( {x: totalPotentialXY.x, y: totalPotentialXY.y, mode: 'lines', line: {color: 'rgb(220, 0, 0)'} } );
  xyData.push( {x: modifPotentialXY.x, y: modifPotentialXY.y, mode: 'lines', line: {color: 'rgb(0, 0, 255)'} } );
  //xyData.push( {x: derivativeXY.x, y: derivativeXY.y, mode: 'lines', line: {color: 'rgb(0, 255, 0)'} } );
  //xyData.push( {x: varianceXY.x, y: varianceXY.y, mode: 'lines', line: {color: 'rgb(100, 100, 100)'} } );

  return xyData;
}



var dataPoints = createDataPoints( coords );
var probes     = createProbes();

// dataToPlot = [ {x: [], y: [], mode: ...}, {x: [], y: [], mode: ...}, ... , {x: [], y: [], mode: ...} ]
var dataToPlot = calculatePotentials(dataPoints, probes);
var probesXY   = calculateProbesXY(probes, dataPoints);

dataToPlot.push(...probesXY);

var dataXY = getCoords( dataPoints );

dataToPlot.push(
   { x: dataXY.x, y: dataXY.y, mode: 'markers', marker: {size: 15, color: 'rgb(255, 0, 0)'} }
);


Plotly.plot('graph', dataToPlot,
{
  xaxis: {range: [x_min, x_max]},
  yaxis: {range: [-1.1, 1.1]},
  hovermode: false,
  showlegend: false
});


var pause = true;


function updatePlot()
{
  updatePotentials(dataPoints, probes);

  var dataToPlot = calculatePotentials(dataPoints, probes);
  var probesXY   = calculateProbesXY(probes, dataPoints);

  dataToPlot.push(...probesXY);

  Plotly.animate('graph', {
    data: dataToPlot
  }, {
    transition: {
      duration: 0,
    },
    frame: {
      duration: 0,
      redraw: false,
    }
  });

  if (pause) return;
  requestAnimationFrame(updatePlot);
}


// Stop the animation by animating to an empty set of frames:
function stopAnimation ()
{
  pause = true;
}


function startAnimation ()
{
  if (pause) {
    requestAnimationFrame(updatePlot);
    pause = false;
  }
}


function next(times = 10)
{
  pause = true;

  for (var i=0; i < times; i++)
  {
     updatePlot();
  }
}
