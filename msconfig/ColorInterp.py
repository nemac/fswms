class ColorInterp:
    def __init__(self, xMin, xMax, rMin, gMin, bMin, rMax, gMax, bMax):
        self.xMin = float(xMin)
        self.rMin = float(rMin)
        self.gMin = float(gMin)
        self.bMin = float(bMin)
        xLen = float(xMax) - float(xMin)
        self.rFactor = ( float(rMax) - float(rMin) ) / float(xLen)
        self.gFactor = ( float(gMax) - float(gMin) ) / float(xLen)
        self.bFactor = ( float(bMax) - float(bMin) ) / float(xLen)
    def interp(self,x):
        return [float(round(self.rMin + (x - self.xMin) * self.rFactor)),
                float(round(self.gMin + (x - self.xMin) * self.gFactor)),
                float(round(self.bMin + (x - self.xMin) * self.bFactor))]
