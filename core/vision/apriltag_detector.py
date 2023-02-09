import pupil_apriltags
import cv2
import numpy as np


class ApriltagDetector:
    # Default detector settings
    # You must call update_settings after modifiying these perameters for them to have any effect.

    families = 'tag16h5'
    nthreads = 1
    quad_decimate = .5
    quad_sigma = 0.0
    refine_edges = 1
    decode_sharpening = 0.25
    debug = 0

    detector = pupil_apriltags.Detector(families='tag16h5',
                                        nthreads=nthreads,
                                        quad_decimate=quad_decimate,
                                        quad_sigma=quad_sigma,
                                        refine_edges=refine_edges,
                                        decode_sharpening=decode_sharpening,
                                        debug=debug)

    def __init__(self):
        pass

    def detect(self, colorFrame: cv2.Mat):
        frame: cv2.Mat = cv2.cvtColor(colorFrame, cv2.COLOR_BGR2GRAY)
        result: list[pupil_apriltags.Detection] = self.detector.detect(frame)
        return result

    # Create a new detector because we can't modify the original detector.
    def update_settings(self):
        self.detector = pupil_apriltags.Detector(families='tag16h5',
                                                 nthreads=self.nthreads,
                                                 quad_decimate=self.quad_decimate,
                                                 quad_sigma=self.quad_sigma,
                                                 refine_edges=self.refine_edges,
                                                 decode_sharpening=self.decode_sharpening,
                                                 debug=self.debug)
