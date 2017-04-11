
function gaus(x, mean=0, sigma=1, norm=false)
{
  var arg = (x-mean)/sigma;
  // for |arg| > 39  result is zero in double precision
  if (arg < -5.0 || arg > 5.0) return 0.0;
  var result = Math.exp(-0.5*arg*arg);
  if (!norm) return result;
  return result/(2.50662827463100024*sigma); //sqrt(2*Pi)=2.50662827463100024
};


function DataPoint1D(x, width = 1, sign=-1)
{
  this.x = x;
  this.width = width;
  this.sign = sign;
  this.amplitude = 1;
};


// "Static" members common to all instances of DataPoint1D
DataPoint1D.gWidth = 200;
DataPoint1D.gWidthMin = 1;
DataPoint1D.gWidthMax = 200;
DataPoint1D.gWidthDelta = 0.02; // Relative change rate of current width


DataPoint1D.prototype.calculatePotential = function(x)
{
  return this.sign * this.amplitude * gaus(x, this.x, this.width);
}


// Flip the sign of the increment when the value is within the delta from the edge
DataPoint1D.prototype.updatePotential = function()
{
  if ( Math.abs(this.width - DataPoint1D.gWidthMax) < Math.abs(DataPoint1D.gWidthMax * DataPoint1D.gWidthDelta) ||
       Math.abs(this.width - DataPoint1D.gWidthMin) < Math.abs(DataPoint1D.gWidthMin * DataPoint1D.gWidthDelta) )
  {
    DataPoint1D.gWidthDelta *= -1;
  }

  this.width += this.width * DataPoint1D.gWidthDelta;
}
