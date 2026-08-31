import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
def find_contours_of_ball(image):
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    T, thresh_img = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY_INV)
    (cnts, bob) = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cnts
def find_coordinates_of_ball(cnts, image):
    ball_coordinates = {}
    for i in range(0, len(cnts)):
        x, y, w, h = cv2.boundingRect(cnts[i])
        if w > 15 and h > 15:
            img_crop = image[y - 15:y +h + 15,
                             x - 15:x + w + 15]
            ball_name = find_features(img_crop)
            ball_coordinates[ball_name] = (x - 15, y - 15, x + w + 15, y + h + 15)
    return ball_coordinates
def find_features(img1):
    correct_matches_dct = {}
    directory = 'images/ball/sample/'
    for image in os.listdir(directory):
        img2 = cv2.imread(directory+image, 0)
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        correct_matches = []
        for m, n in matches:
            if m.distance < 0.75*n.distance:
                correct_matches.append([m])
        correct_matches_dct[image.split('.')[0]]= len(correct_matches)
        correct_matches_dct = dict(sorted(correct_matches_dct.items(), key=lambda item: item[1], reverse=True))
    return list(correct_matches_dct.keys())[0]
def video_to_frames(path, folder):
    cap = cv2.VideoCapture(path)
    frame_count = 0
    points = []
    ret, frame = cap.read()
    main_image = frame
    gray_main_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    contours = find_contours_of_ball(gray_main_image)
    ball_location = find_coordinates_of_ball(contours, gray_main_image)
    for key, value in ball_location.items():
        radius = (value[2]-value[0])/2
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        main_image = frame
        gray_main_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
        contours = find_contours_of_ball(gray_main_image)
        ball_location = find_coordinates_of_ball(contours, gray_main_image)
        ball_center = 0
        for key, value in ball_location.items():
            ball_center = (value[0]+value[2])/2
        points.append(ball_center)
        print(ball_center)
    cap.release()
    mean = sum(points)/frame_count
    result = []
    for i in range(len(points)):
        result.append(2.5*(points[i]-mean)/radius)
    print(f"Substracted {frame_count} frames from {path}")
    frame_list = []
    for i in range(frame_count):
        frame_list.append(i*0.033)
    plt.plot(frame_list, result, linestyle='-')
    plt.xlabel("Time, s")
    plt.ylabel("X coordinate, sm")
    plt.title('Dependence of X coordinate on time')
    plt.grid(True, alpha=0.3)
    plt.show()
video_to_frames("videos/pendulum/main_test_2.mp4", "frames_output")