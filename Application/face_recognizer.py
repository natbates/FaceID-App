import numpy as np
import cv2, pygame, os, sys, time

MINNEIGHBOURS = 2
SCALEFACTOR = 1.2
DEBUG = False
class Scanner:

    def __init__(self, SCREEN):
        self.clock = pygame.time.Clock()
        self.scan_bar = None
        self.flytoposition = SCREEN.get_height() - 20
        self.SCREEN = SCREEN
        # Animation properties
        self.frames_per_second = 30
        self.delta_y = 15  # Speed of movement in pixels/frame
        self.flyingDown = False
        self.flyingUp = False
        self.font = pygame.font.Font(None, 24)
        self.scantext = self.font.render("SCANNING, PLEASE STARE INTO CAMERA", True, "red")

    def updatePosition(self):

        if self.flyingDown:
            if self.scan_bar.y < self.SCREEN.get_height():
                self.scan_bar.y += self.delta_y
                pygame.draw.rect(self.SCREEN, "black", self.scan_bar)
                pygame.display.update()
                self.clock.tick(self.frames_per_second)
            else:
                self.flyingUp = True
                self.flyingDown = False

        if self.flyingUp:

            if self.scan_bar.y > 0:
                self.scan_bar.y -= self.delta_y
                pygame.draw.rect(self.SCREEN, "black", self.scan_bar)
                pygame.display.update()
                self.clock.tick(self.frames_per_second)
            else:
                self.flyingUp = False
                self.flyingDown = True

    def drawScanner(self):

        self.SCREEN.blit(self.scantext, (self.SCREEN.get_width()/2 - self.scantext.get_width()/2, 50))

        if self.scan_bar is not None:
            # Update text position
            self.updatePosition()

            self.timer -= 1 / self.frames_per_second  # Decrease timer by one frame's worth of time
            if self.timer <= 0:
                self.timer = 0
                self.scan_bar = None

    def Scan(self, duration):

        self.scan_bar = pygame.Rect(0, 0, self.SCREEN.get_width(), 3)
        self.timer = duration
        self.flyingDown = True

def normalize_dict(dictionary):
    # Find the sum of all values in the dictionary
    sum_values = sum(dictionary.values())

    # Normalize the values in the dictionary
    normalized_dict = {}
    for key, value in dictionary.items():
        normalized_value = value / sum_values
        normalized_dict[key] = round(normalized_value, 2)

    return normalized_dict

def image_check(image_data):

    return True # Future option to check that user doesnt have another account via Face ID

def face_check(runtime, SCREEN, display):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')

    face_cascade_Path = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(face_cascade_Path)
    font = cv2.FONT_HERSHEY_SIMPLEX

    unordered_list = []
    for path in os.listdir("images"):
        unordered_list.append(path)

    def remove_duplicates_with_same_prefix(lst):
        prefixes = set()
        result = []

        for item in lst:
            parts = item.split('.')
            prefix = '.'.join(parts[:2])
            if prefix not in prefixes:
                result.append(prefix)
                prefixes.add(prefix)

        return result

    filtered_list = remove_duplicates_with_same_prefix(unordered_list)
    sorted_list = sorted(filtered_list, key=lambda x: int(x.split('.')[0]))
    ordered_list = [item.split('.')[1] for item in sorted_list]
    names = ['None'] + ordered_list

    print(names)

    for i in range(2):
        cam = cv2.VideoCapture(i)
        if cam.isOpened():
            break
        else:
            print(f"Failed to open camera {i}.")

    try:
        if not cam.isOpened():
            print("No camera is available.")
    except:
        print("No camera is available.")

    scanner = Scanner(SCREEN)
    scanner.Scan(10)

    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    start_time = time.time()
    user_confidences = {}

    while time.time() - start_time < runtime:

        SCREEN.fill((200, 200, 200))
        display.draw()
        scanner.drawScanner()
        pygame.display.update()


        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor= SCALEFACTOR,
            minNeighbors= MINNEIGHBOURS,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            cv2.putText(img, str(names[id]), (x + 5, y - 5), font, 1, (255, 255, 255), 2)

            # Check if confidence is above the threshold (e.g., 51)
            confidence_percentage = round((1 - (confidence / 400)) * 100, 2)

            try:
                name = names[id]
                if name not in user_confidences:
                    user_confidences[str(id) + "." + name] = 0
                user_confidences[str(id) + "." + name] += (confidence_percentage)

                # Display confidence percentage above the threshold
                confidence_percentage = round((1 - (confidence / 400)) * 100, 2)
                cv2.putText(img, f"{name}: {confidence_percentage}%", (x + 5, y + h + 20), font, 0.8,
                            (255, 255, 255), 1)
            except IndexError as e:
                pass

        time_left = int(runtime - (time.time() - start_time))
        cv2.putText(img, f"Time Left: {time_left} seconds", (10, 30), font, 0.8, (255, 255, 255), 2)

        if DEBUG:
            cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
    normalized_data = normalize_dict(user_confidences)
    return user_confidences, normalized_data

