import cv2
import numpy as np

class AssistiveVision:
    def __init__(self, workspace_width_mm, workspace_height_mm):
        #Initialize the vision pipeline

        self.width_mm = workspace_width_mm
        self.height_mm = workspace_height_mm

        #ArUco config
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        self.homography_matrix = None

    def calibrate_workspace(self, frame):
        #Detect ArUco markers and compute homography

        corners, ids, _ = self.detector.detectMarkers(frame)

        if ids is None or len(ids) != 4:
            #Handle cases where no markers or an incorrect number of markers are detected
            if ids is None:
                print("ERROR: None ArUco markers detected")
            else:
                print(f"ERROR: {len(ids)} ArUco markers not detected")
            return False


        #Map out the detected corners to their IDs
        marker_dict = {int(marker_id): corner[0] for marker_id, corner in zip(ids, corners)}

        try: 
            #Extract the top left corner from each marker
            pixel_TL = marker_dict[0][0]
            pixel_TR = marker_dict[1][0]
            pixel_BR = marker_dict[2][0]
            pixel_BL = marker_dict[3][0]

            pts_pixels = np.array([pixel_TL, pixel_TR, pixel_BR, pixel_BL], dtype="float32")

            #Define the real world coords of those corners
            pts_real_world = np.array ([[0,0],
                                    [self.width_mm, 0], 
                                    [self.width_mm, self.height_mm], 
                                    [0, self.height_mm]], 
                                    dtype="float32")
            
            #Calculate and store matrix
            self.homography_matrix, _ = cv2.findHomography(pts_pixels, pts_real_world)
            print("Workspace calibrated successfully")
            return True

        except KeyError as e:
            print(f"ERROR: Missing required marker ID: {e}")
            return False

    def get_flat_workspace(self, frame):
        #Apply homography to get a top down view of the workspace

        if self.homography_matrix is None:
            print("Warning: Can't flatten workspace. The calibration matrix is not set.")
            return frame

        warped_image = cv2.warpPerspective(frame, self.homography_matrix, (int(self.width_mm), int(self.height_mm)))
        return warped_image

#Testing script

if __name__ == "__main__":

    vision_system = AssistiveVision(workspace_width_mm=354.0, workspace_height_mm=262.0)

    test_image = cv2.imread("test_workspace.jpg")
    if test_image is not None:
        is_calibrated = vision_system.calibrate_workspace(test_image)

        if is_calibrated:
            flat_workspace = vision_system.get_flat_workspace(test_image)
            cv2.imshow("Original Camera View", test_image)
            cv2.imshow("Flattened Workspace", flat_workspace)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("ERROR: Couldn't load test image.")