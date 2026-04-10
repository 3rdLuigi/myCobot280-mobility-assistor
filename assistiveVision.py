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
        marker_dict = {int(marker_id[0]): corner[0] for marker_id, corner in zip(ids, corners)}

        try: 
            #Extract the top left corner from each marker
            pixel_TL = marker_dict[0][3]
            pixel_TR = marker_dict[1][2]
            pixel_BR = marker_dict[2][0]
            pixel_BL = marker_dict[3][1]

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
    
    #Detection logic, using HSV (hue, saturation, value)
    def detect_objects(self, flat_frame, lower_hsv, upper_hsv, lower_hsv2=None, upper_hsv2=None, min_area=5):
        #Filter image

        hsv_frame = cv2.cvtColor(flat_frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)

        if lower_hsv2 is not None and upper_hsv2 is not None:
            mask2 = cv2.inRange(hsv_frame, lower_hsv2, upper_hsv2)
            mask = cv2.bitwise_or(mask, mask2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_objects = []
        result_frame = flat_frame.copy()

        for contour in contours:
            area = cv2.contourArea(contour)

            if area > min_area: 
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    #Store data
                    detected_objects.append({'x': cX, 'y': cY, 'area_mm2': area})

                    #Draw a visual feedback, green outline and red dot at center
                    cv2.drawContours(result_frame, [contour], -1, (0,255,0), 2)
                    cv2.circle(result_frame, (cX,cY), 4, (0,0,255), -1)

                    #Write object coordinates near the object
                    coord_text = f"X:{cX} Y:{cY}"
                    cv2.putText(result_frame, coord_text, (cX -20, cY -15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0),1)

        return result_frame, mask, detected_objects


#Testing script

if __name__ == "__main__":

    #Known workspace dimensions in mm
    vision_system = AssistiveVision(workspace_width_mm = 378.0, workspace_height_mm = 225.0)

    test_image = cv2.imread("lego_test_ws.jpg")
    if test_image is not None:
        is_calibrated = vision_system.calibrate_workspace(test_image)

        if is_calibrated:
            flat_workspace = vision_system.get_flat_workspace(test_image)

            #Separate HSV ranges into lower and upper ranges
            lower_red1 = np.array([0,120,70])
            upper_red1 = np.array([10,255,255])

            lower_red2 = np.array([165,120,70])
            upper_red2 = np.array([179,255,255])
            
            #Run object detection for red objects
            tracked_frame, color_mask, objects = vision_system.detect_objects(
                flat_workspace, 
                lower_red1, 
                upper_red1, 
                lower_red2, 
                upper_red2)
            print(f"\nFound {len(objects)} Red Objects")

            for i, obj in enumerate(objects):
                print(f"Object {i+1}: X={obj['x']}mm, Y={obj['y']}mm, | Area: {obj['area_mm2']}mm^2")
            
            #Display the results
            cv2.imshow("1. Flatten Workspace", flat_workspace)
            cv2.imshow("2. Color Mask", color_mask)
            cv2.imshow("3. Final Tracking", tracked_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("ERROR: Couldn't load test image.")