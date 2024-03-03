import sys
import numpy as np
import cv2, os, pygame, time, dlib

pygame.font.init()
font = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 28)
font2 = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 19)
font3 = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 13)


MAXTRAINTIME = 5
PHOTOSPERDIRECTION = 10
PHOTOSPERDIRECTIONFORWARD = 30
NUMIMAGESCAP = 250 # Max amount of images a profile can have for learning
DEBUG = False

def faceScanSetUp(display, id, username, SCREEN): # Takes more detailed face images by making user turn face left right up and down
    # Create a directory to store the captured images

    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    # Initialize dlib's face detector and facial landmarks predictor
    detector = dlib.get_frontal_face_detector()
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    def getDirectionX(lefteye, righteye, nose, threshold=30):
        distance_x = abs(righteye - nose)
        distance_y = abs(lefteye - nose)

        if abs(distance_x - distance_y) < threshold:
            return "Looking Forward"
        else:
            if distance_x < distance_y:
                return "Looking Left"
            elif distance_y < distance_x:
                return "Looking Right"

            else:
                return "Undetermined"

    def getDirectionY(lefteye, righteye, nose):
        distance_x = abs(righteye - nose)
        distance_y = abs(lefteye - nose)

        distance = (distance_x + distance_y) / 2
        if distance > 40:
                return "Looking Down"
        elif distance > 20 and distance <= 40:
            return "Looking Forward"
        elif distance > 0:
            return "Looking Up"
        else:
            return "Undetermined"


    def drawprogress(forward, left, right, up, down):

        barlength = 200
        barthickness = 20
        colour = (119, 221, 119)
        forwardrect = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 300, barlength, barthickness)
        forwardprogress = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 300, barlength/PHOTOSPERDIRECTIONFORWARD * forward, barthickness)
        forwardtext = font3.render("Look Forward", True, "black")
        pygame.draw.rect(SCREEN, (50, 50, 50), forwardrect)
        pygame.draw.rect(SCREEN, colour, forwardprogress)
        if forward != PHOTOSPERDIRECTIONFORWARD:
            SCREEN.blit(forwardtext, (forwardrect.x + forwardtext.get_width()/2, 300 + 2))

        leftrect = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 340, barlength, barthickness)
        leftprogress = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 340, barlength/PHOTOSPERDIRECTION * left, barthickness)
        lefttext = font3.render("Look Left", True, "black")
        pygame.draw.rect(SCREEN, (50, 50, 50), leftrect)
        pygame.draw.rect(SCREEN, colour, leftprogress)
        if left != PHOTOSPERDIRECTION:
            SCREEN.blit(lefttext, (leftrect.x + lefttext.get_width()/2, 340 + 2))


        rightrect = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 380, barlength, barthickness)
        rightprogress = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 380, barlength/PHOTOSPERDIRECTION * right, barthickness)
        righttext = font3.render("Look Right", True, "black")
        pygame.draw.rect(SCREEN, (50, 50, 50), rightrect)
        pygame.draw.rect(SCREEN, colour, rightprogress)
        if right != PHOTOSPERDIRECTION:
            SCREEN.blit(righttext, (rightrect.x + righttext.get_width()/2, 380 + 2))

        uprect = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 420, barlength, barthickness)
        upprogress = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 420, barlength/PHOTOSPERDIRECTION * up, barthickness)
        uptext = font3.render("Look Up", True, "black")
        pygame.draw.rect(SCREEN, (50, 50, 50), uprect)
        pygame.draw.rect(SCREEN, colour, upprogress)
        if up != PHOTOSPERDIRECTION:
            SCREEN.blit(uptext, (uprect.x + uptext.get_width()/2, 420 + 2))

        downrect = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 460, barlength, barthickness)
        downprogress = pygame.Rect(SCREEN.get_width()/2 - barlength/2, 460, barlength/PHOTOSPERDIRECTION * down, barthickness)
        downtext = font3.render("Look Down", True, "black")
        pygame.draw.rect(SCREEN, (50, 50, 50), downrect)
        pygame.draw.rect(SCREEN, colour, downprogress)
        if down != PHOTOSPERDIRECTION:
            SCREEN.blit(downtext, (downrect.x + downtext.get_width()/2, 460 + 2))

    # Function to capture face images
    def capture_face():

        rightphotos = 0
        leftphotos = 0
        downphotos = 0
        upphotos = 0
        forwardphotos = 0
        totalphotos = 0

        ret, frame = cap.read()

        original_width = frame.shape[0]
        original_height = frame.shape[1]
        max_width = 400
        max_height = 300

        # Calculate the aspect ratio
        aspect_ratio = original_width / original_height
        # Calculate the new dimensions while preserving the aspect ratio
        if original_width > original_height:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * aspect_ratio)

        if not ret:
            print("Failed to capture image")
            return

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            ret, frame = cap.read()
            SCREEN.fill((200, 200, 200))
            text = font.render("Face ID set up, please move face accordingly!", True, "black")
            SCREEN.blit(text, (SCREEN.get_width()/2 - text.get_width()/2, 8))
            drawprogress(forwardphotos, leftphotos, rightphotos, upphotos, downphotos)

            if totalphotos == 4 * PHOTOSPERDIRECTION + PHOTOSPERDIRECTIONFORWARD:
                running = False
                SCREEN.fill((200, 200, 200))
                text = font.render("Loading...", True, (0, 0, 0))
                SCREEN.blit(text, (SCREEN.get_width()/2 - text.get_width()/2, SCREEN.get_height()/2 - text.get_height()/2))
                pygame.display.update()
                return totalphotos

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            # Get the facial landmarks of the first face
            if len(faces) == 1:
                shape = predictor(gray, faces[0])

                # Extracting the coordinates of left and right eyes
                left_eye = shape.part(36)
                right_eye = shape.part(45)

                # Draw rectangles around the eyes
                left_eye_top_left = (left_eye.x - 10, left_eye.y - 10)
                left_eye_bottom_right = (left_eye.x + 10, left_eye.y + 10)
                right_eye_top_left = (right_eye.x - 10, right_eye.y - 10)
                right_eye_bottom_right = (right_eye.x + 10, right_eye.y + 10)

                nose_points = [shape.part(i) for i in range(27, 36)]

                # Get the x-coordinates of the points representing the nose
                nose_points_x = [shape.part(i).x for i in range(27, 36)]
                nose_center_x = sum(nose_points_x) // len(nose_points_x)

                nose_points_y = [shape.part(i).y for i in range(27, 36)]
                nose_center_y = sum(nose_points_y) // len(nose_points_y)

                directionX = getDirectionX(left_eye.x, right_eye.x, nose_center_x)
                directionY = getDirectionY(left_eye.y, right_eye.y, nose_center_y)

                face_top = faces[0].top()
                if DEBUG:
                    cv2.putText(frame, "Y = " + directionY, (int(left_eye.x + 20), int(face_top - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(frame, "X = " + directionX, (int(left_eye.x + 20), int(face_top - 40)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    cv2.rectangle(frame, left_eye_top_left, left_eye_bottom_right, (0, 255, 0), 2)
                    cv2.rectangle(frame, right_eye_top_left, right_eye_bottom_right, (0, 255, 0), 2)

                    # Draw a line across the nose
                    for i in range(len(nose_points) - 1):
                        cv2.line(frame, (nose_points[i].x, nose_points[i].y),
                                 (nose_points[i + 1].x, nose_points[i + 1].y),
                                 (255, 0, 0), 2)

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = np.rot90(frame_rgb)  # Rotate frame (optional)
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
                pygame_frame = pygame.surfarray.make_surface(frame_rgb)
                SCREEN.blit(pygame_frame, (SCREEN.get_width() / 2 - new_width / 2 - 30, 60))
                pygame.draw.rect(SCREEN, (10, 10, 10),
                                 pygame.Rect(SCREEN.get_width() / 2 - new_width / 2 - 30, 60, new_height, new_width), 5)

                pygame.display.update()
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces2 = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                if len(faces2) != 0:
                    x, y, w, h = faces2[0]
                    frame = gray[y:y + h, x:x + w]

                    if directionX == "Looking Right" and directionY == "Looking Forward" and rightphotos < PHOTOSPERDIRECTION:
                        rightphotos += 1
                        totalphotos += 1
                        cv2.imwrite(f"./images/" + str(id) + "." + username + "." + str(totalphotos) + ".jpg", frame)
                    if directionX == "Looking Left" and directionY == "Looking Forward" and leftphotos < PHOTOSPERDIRECTION:
                        leftphotos += 1
                        totalphotos += 1
                        cv2.imwrite(f"./images/" + str(id) + "." + username + "." + str(totalphotos) + ".jpg", frame)
                    if directionX == "Looking Forward" and directionY == "Looking Up" and upphotos < PHOTOSPERDIRECTION:
                        upphotos += 1
                        totalphotos += 1
                        cv2.imwrite(f"./images/" + str(id) + "." + username + "." + str(totalphotos) + ".jpg", frame)
                    if directionX == "Looking Forward" and directionY == "Looking Down" and downphotos < PHOTOSPERDIRECTION:
                        downphotos += 1
                        totalphotos += 1
                        cv2.imwrite(f"./images/" + str(id) + "." + username + "." + str(totalphotos) + ".jpg", frame)
                    if directionX == "Looking Forward" and directionY == "Looking Forward" and forwardphotos < PHOTOSPERDIRECTIONFORWARD:
                        forwardphotos += 1
                        totalphotos += 1
                        cv2.imwrite(f"./images/" + str(id) + "." + username + "." + str(totalphotos) + ".jpg", frame)


            else:
                if len(faces) == 0:
                    message = "No Faces Found"
                    text = font.render(message, True, "white")
                elif len(faces) > 1:
                    message = "More than one face found"
                    text = font2.render(message, True, "white")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = np.rot90(frame_rgb)  # Rotate frame (optional)
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
                darkened_frame_rgb = np.clip(frame_rgb * 0.3, 0, 255).astype(np.uint8)
                pygame_frame = pygame.surfarray.make_surface(darkened_frame_rgb)
                SCREEN.blit(pygame_frame, (SCREEN.get_width() / 2 - new_width / 2 - 30, 60))
                pygame.draw.rect(SCREEN, (10, 10, 10),
                                 pygame.Rect(SCREEN.get_width() / 2 - new_width / 2 - 30, 60, new_height, new_width), 5)
                SCREEN.blit(text, (SCREEN.get_width()/2 - text.get_width()/2, 60 + pygame_frame.get_height()/2 - text.get_height()))
                pygame.display.update()


    # Main loop to capture face images in different directions

        # Capture faces in all directions
    totalphotos = capture_face()
    cap.release()
    cv2.destroyAllWindows()
    return totalphotos

def runFaceScan(display, SCREEN, id, numofphotos, username):

    def create_directory(directory):

        if not os.path.exists(directory):
            os.makedirs(directory)

    # Load the pre-trained face cascade classifier
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Open a connection to the default camera (camera index 0)
    cam = cv2.VideoCapture(0)
    # Set camera dimensions
    cam.set(3, 640)
    cam.set(4, 480)

    # Initialize face capture variables
    count = 0
    timer = MAXTRAINTIME
    start_time = time.time()
    create_directory('images/')

    try:
        numofimages = sum(1 for item in os.listdir("images/") if item.startswith(str(id) + "."))
    except:
        numofimages = 0

    if numofimages < NUMIMAGESCAP:
        while True:
            # Read a frame from the camera
            ret, img = cam.read()

            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                timer -= 1
                start_time = time.time()

            SCREEN.fill((200, 200, 200))
            display.draw()
            pygame.display.update()

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            # Process each detected face
            for (x, y, w, h) in faces:
                # Draw a rectangle around the detected face
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Increment the count for naming the saved images
                count += 1

                # Save the captured image into the 'images' directory
                cv2.imwrite(f"./images/" + str(id) + "." + username + "." +str(count + numofimages) + ".jpg", gray[y:y + h, x:x + w])

                # Display the image with rectangles around faces
                if DEBUG:
                    cv2.imshow('image', img)

            # Take 30 face samples and stop video. You may increase or decrease the number of
            # images. The more, the better while training the model.
            if count >= numofphotos or timer == 0:
                break

    # Release the camera
    cam.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()
    return count

