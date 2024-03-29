from typing import List
import cv2
import output_processor.robot_output_processor as robot_output_processor


class VisualOutputProcessor:
    def __init__(self, rop):
        self.tag_detections = [[], [], [], []]
        self.rop = rop

    def display_frame(self, frame, cam_id):
        display_frame = frame.copy()

        for tag_detection in self.tag_detections[cam_id]:
            tag_id, family, corners, center, timestamp, camera_id = tag_detection

            if not robot_output_processor.valid_detection(family, tag_id):
                continue

            x1 = int(corners[0][0])
            y1 = int(corners[0][1])
            x2 = int(corners[1][0])
            y2 = int(corners[1][1])
            cv2.line(display_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            x1 = int(corners[1][0])
            y1 = int(corners[1][1])
            x2 = int(corners[2][0])
            y2 = int(corners[2][1])
            cv2.line(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            x1 = int(corners[2][0])
            y1 = int(corners[2][1])
            x2 = int(corners[3][0])
            y2 = int(corners[3][1])
            cv2.line(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            x1 = int(corners[3][0])
            y1 = int(corners[3][1])
            x2 = int(corners[0][0])
            y2 = int(corners[0][1])
            cv2.line(display_frame, (x1, y1), (x2, y2), (255, 128, 64), 2)

            textSize, baseline = cv2.getTextSize(str(id), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
            textyheight = textSize[1] + baseline

            cv2.putText(display_frame, str(id), (int(center[0]), int(center[1]) + textyheight * 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)

            cv2.putText(display_frame, str(self.rop.april_tag_corners[family][tag_id][0]), (int(corners[0][0]), int(corners[0][1]) + textyheight),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
            cv2.putText(display_frame, str(self.rop.april_tag_corners[family][tag_id][1]), (int(corners[1][0]), int(corners[1][1]) + textyheight),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
            cv2.putText(display_frame, str(self.rop.april_tag_corners[family][tag_id][2]), (int(corners[2][0]), int(corners[2][1]) + textyheight),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)
            cv2.putText(display_frame, str(self.rop.april_tag_corners[family][tag_id][3]), (int(corners[3][0]), int(corners[3][1]) + textyheight),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 128, 128), 2)

        display_frame = resize(display_frame, 640.0)
        cv2.imshow(str(cam_id), display_frame)
        cv2.waitKey(1)

    def add_tag_detections(self, cam_id, tag_detections):
        for tag_detection in tag_detections:
            self.tag_detections[cam_id].append(tag_detection)

    def clear_tag_detections(self, cam_id):
        self.tag_detections[cam_id].clear()


def resize(frame, dst_width):
    width = frame.shape[1]
    height = frame.shape[0]
    scale = dst_width * 1.0 / width
    return cv2.resize(frame, (int(scale * width), int(scale * height)))
