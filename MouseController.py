import cv2
import mediapipe as mp
from pynput.mouse import Controller, Button

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


screen_width, screen_height = 1920, 1080
mouse = Controller()

DELAY = 5
delays = 0
ratio = 2

def is_fist(hand_landmarks, threshold=0.05):

    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # calculate the distance between the thumb and the index finger tip, to determine whether user is pinching
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    return distance < threshold

# def is_fist(hand_landmarks, threshold=0.05):

#     thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
#     index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

#     # calculate the distance between the thumb and the index finger tip, to determine whether user is pinching
#     distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
#     middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
#     distance = ((thumb_tip.x - middle_tip.x) ** 2 + (thumb_tip.y - middle_tip.y) ** 2) ** 0.5
#     return distance < threshold

previous = (-1, -1)
while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    image = cv2.flip(image, 1) # flip the image
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    landmarks = results.multi_hand_landmarks
    # if landmarks:
    #     for hand_landmarks in landmarks:
    #         mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    #         wrist_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    #         x = int(wrist_landmark.x * screen_width)
    #         y = int(wrist_landmark.y * screen_height)
    #         # print(x, y, previous)
    #         if x != None and y != None and previous != (-1, -1):
    #             dx = (x - previous[0]) * ratio
    #             dy = (y - previous[1]) * ratio
    #             print(dx, dy)
    #             mouse.move(dx, dy)
    #         previous = (x, y)
    #         if is_fist(hand_landmarks) and delays < 0:
    #             mouse.click(Button.left) 
    #             delays = DELAY
    #         else: delays -= 1
    if landmarks:
        for hand_landmarks in landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            wrist_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            x = int(wrist_landmark.x * screen_width)
            y = int(wrist_landmark.y * screen_height)
            if x != None and y != None:
                mouse.position = (x * ratio - (screen_width // 2), y * ratio - (screen_height // 2))
            if is_fist(hand_landmarks) and delays < 0:
                mouse.click(Button.left) 
                delays = DELAY
            else: delays -= 1

    cv2.imshow('Hand Tracking', image)
    if cv2.waitKey(1) == ord('q'): break

cap.release()
cv2.destroyAllWindows()