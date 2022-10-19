import numpy as np
import pupil_apriltags as pupil
import scipy as sci


detector: pupil.Detector = pupil.Detector(families='tag16h5',
                       nthreads=1,
                       quad_decimate=0.0,
                       quad_sigma=0.0,
                       refine_edges=1,
                       decode_sharpening=0.25,
                       debug=0)

detection : pupil.Detection = detector.detect()