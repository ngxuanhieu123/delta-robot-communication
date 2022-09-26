import cv2 as cv 
from src.models import CenterDetector, TrajectoryPredictor
from threading import Thread
from time import sleep, time


vid = cv.VideoCapture("conveyor_belt.mp4")
predictor = TrajectoryPredictor(sample_time=10, num_data_points=20)
first_time = time()
fixed_points = []

def on_click(event, x, y, p1, p2):
    if event == cv.EVENT_LBUTTONDOWN:
        print(f"({x}, {y})")

def collect_predictor(predictor, center_detector, fixed_points):
    f_time = time()
    for i in range(predictor.get_num_data_points()):
        time_val = time() - f_time
        point = center_detector.get_current_points()[0]
        predictor.add_point(point, time_val * 1000)
        sleep(predictor.get_sample_time()/1000)

    point = predictor.predict(time=500)
    print(point)
    fixed_points.append([point, (0, 255, 0)])


center_detector = CenterDetector(shifting_frame=(78, 218))
thread = Thread(target=collect_predictor, args=(predictor, center_detector, fixed_points, ))

def draw_fixed_points(frame, points):
    for point, color in points:
        frame = cv.circle(frame, (int(point[0]), int(point[1])), 5, color, -1)

    return frame

test_time = None
run = False
while True:
    ret, frame = vid.read()
    new_time = time()

    if ret:
        cutting_frame = frame[218:322, 78:365]
        
        center_detector.get_center_points(cutting_frame)
        detected_frame = center_detector.draw_points(frame)
        drawed_frame = draw_fixed_points(detected_frame, fixed_points)
        cv.imshow("vid", cutting_frame)
        cv.imshow("detected", detected_frame)
        cv.imshow("full", frame)
        cv.imshow("draw", drawed_frame)

        if not run and new_time - first_time >= 3:
            thread.start()
            test_time = new_time
            run = True

        if test_time != None and new_time - test_time >= .5:
            if len(fixed_points) < 2:
                point = center_detector.get_current_points()[0] 
                fixed_points.append([point, (255, 0, 0)])
                print(point)
            
        if cv.waitKey(25) & 0xff == ord('q'):
            break
    else:
        break

thread.join()
