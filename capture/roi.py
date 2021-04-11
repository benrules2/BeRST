import log

class ROI:
    def __init__(self, parameters : tuple, id):
        self.parameters = parameters
        self.top_left = (parameters[0], parameters[1])
        self.width = parameters[2]
        self.height = parameters[3]
        self.bottom_right = (parameters[0] + self.width, parameters[1] + self.height)
        self._report_corners_and_dimensions()
        self.roi = parameters
    
    def check_if_coords_in_region(self, coords):        
        x_inside = coords[0] >= self.top_left[0] and coords[0] <= self.bottom_right[0] 
        y_inside = coords[1] <= self.bottom_right[1] and coords[1] >= self.top_left[1]

        if x_inside and y_inside:
            return True

    def _report_corners_and_dimensions(self):
        log.info("ROI width {} height {} top left {} bottom right {}".format(self.width, self.height, self.top_left, self.bottom_right))
