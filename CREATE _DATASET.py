import os
import pickle
import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.5)

# Data directory
DATA_DIR = './data'

# Initialize lists for data and labels
data = []
labels = []

# Function to calculate the angle between three points
def calculate_angle(x1, y1, x2, y2, x3, y3):
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    return abs(angle)

# Function to calculate the Euclidean distance
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to apply data augmentation (flip the image)
def augment_image(image):
    return cv2.flip(image, 1)  # Horizontal flip

# Loop through each folder (sign labels)
for dir_ in os.listdir(DATA_DIR):
    for img_path in os.listdir(os.path.join(DATA_DIR, dir_)):
        data_aux = []
        x_ = []
        y_ = []

        # Read and convert the image
        img = cv2.imread(os.path.join(DATA_DIR, dir_, img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process the image with MediaPipe Hands
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Collect landmark coordinates
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                # Normalize coordinates
                min_x, min_y = min(x_), min(y_)
                max_x, max_y = max(x_), max(y_)
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append((x - min_x) / (max_x - min_x))
                    data_aux.append((y - min_y) / (max_y - min_y))

                # Calculate angles between fingers
                angle_1 = calculate_angle(x_[0], y_[0], x_[1], y_[1], x_[2], y_[2])
                angle_2 = calculate_angle(x_[2], y_[2], x_[3], y_[3], x_[4], y_[4])
                angle_3 = calculate_angle(x_[5], y_[5], x_[6], y_[6], x_[8], y_[8])
                data_aux.extend([angle_1, angle_2, angle_3])

                # Calculate distances between key landmarks
                distance_1 = calculate_distance(x_[0], y_[0], x_[5], y_[5])
                distance_2 = calculate_distance(x_[5], y_[5], x_[9], y_[9])
                distance_3 = calculate_distance(x_[9], y_[9], x_[13], y_[13])
                data_aux.extend([distance_1, distance_2, distance_3])

                data.append(data_aux)
                labels.append(dir_)

                # Apply augmentation (flip the image)
                flipped_img = augment_image(img)
                flipped_results = hands.process(cv2.cvtColor(flipped_img, cv2.COLOR_BGR2RGB))
                if flipped_results.multi_hand_landmarks:
                    for hand_landmarks in flipped_results.multi_hand_landmarks:
                        data_flip = []
                        x_flip, y_flip = [], []
                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            x_flip.append(x)
                            y_flip.append(y)

                        # Normalize flipped coordinates
                        min_x, min_y = min(x_flip), min(y_flip)
                        max_x, max_y = max(x_flip), max(y_flip)
                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            data_flip.append((x - min_x) / (max_x - min_x))
                            data_flip.append((y - min_y) / (max_y - min_y))

                        # Calculate angles and distances for flipped image
                        angle_1 = calculate_angle(x_flip[0], y_flip[0], x_flip[1], y_flip[1], x_flip[2], y_flip[2])
                        angle_2 = calculate_angle(x_flip[2], y_flip[2], x_flip[3], y_flip[3], x_flip[4], y_flip[4])
                        angle_3 = calculate_angle(x_flip[5], y_flip[5], x_flip[6], y_flip[6], x_flip[8], y_flip[8])
                        data_flip.extend([angle_1, angle_2, angle_3])

                        distance_1 = calculate_distance(x_flip[0], y_flip[0], x_flip[5], y_flip[5])
                        distance_2 = calculate_distance(x_flip[5], y_flip[5], x_flip[9], y_flip[9])
                        distance_3 = calculate_distance(x_flip[9], y_flip[9], x_flip[13], y_flip[13])
                        data_flip.extend([distance_1, distance_2, distance_3])

                        # Append flipped data
                        data.append(data_flip)
                        labels.append(dir_)

# Save the dataset
with open('data.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print("Data collection completed and saved to 'data.pickle'")
