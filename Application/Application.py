# version 1.0.0 Author: Nathaniel Bates

import pygame, sys, os, cv2, time
import numpy as np
from datetime import datetime
from PIL import Image
from face_taker import runFaceScan, faceScanSetUp
from face_train import train
from face_recognizer import face_check, image_check

DEBUG = False
FPS = 60
USERNAMEMAXCHAR = 25
PASSWORDMAXCHAR = 30
MINPASSWORDLENGTH = 5
MINUSERNAMELENGTH = 5

UPDATEPHOTONUM = 10
STARTPHOTONUM = 30
MINPHOTOSFORFACEID = 10
PROFILEIMAGEWIDTH = 213

FACEIDCHECKTIME = 4
FACEIDTHRESHOLD = 85
FACE_ID_COOLDOWN_DURATION = 8

SCREEN = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Face Recognition Application")
icon_surf = pygame.Surface((32, 32))
icon = pygame.image.load("UI images/icon4.png")
icon = pygame.transform.scale(icon, (100, 100))
pygame.display.set_icon(icon)

for i in range(2):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        break
def createData():

    passwords = {}
    accounts = []
    directory = "Passwords"
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            username, ext = os.path.splitext(filename)
            accounts.append(username)
            if ext.lower() == '.txt':
                with open(filepath, 'r') as file:
                    password = file.read().strip()
                    passwords[username] = password

    return passwords, accounts
def DeleteAccount(accountname):

    file_path = "ProfileImages/"+accountname+".jpg"  # Replace with the path to your file
    filepath2 = "Passwords/"+accountname+".txt"
    filepaths = [file_path, filepath2]
    for file_path in filepaths:
        if os.path.exists(file_path):
            # Delete the file
            try:
                os.remove(file_path)  # or os.unlink(file_path)
            except:
                print(f"File '{file_path}'")
        else:
            print(f"File '{file_path}' does not exist.")


    for thispath in os.listdir("images/"):
        parts = thispath.split('.')
        # Extract the text between the dots
        if accountname == parts[1]:
            id = parts[0]
            os.remove("images/"+thispath)

    source_path = "UI images/Account Deleted.jpg"
    destination_dir = "images"
    new_name = id+".AccountDeleted"
    img = Image.open(source_path)
    _, ext = os.path.splitext(source_path)
    new_file_path = os.path.join(destination_dir, new_name + ext)
    img.save(new_file_path)
    img.close()

class TextPopUp:

    def __init__(self):
        pygame.init()
        # Colors
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)

        # Text properties
        self.font = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 16)
        self.text_surface = None
        self.text_rect = None
        self.flytoposition = SCREEN.get_height() - 25

        # Animation properties
        self.start_time = time.time()
        self.delta_y = 2  # Speed of movement in pixels/frame
        self.flyingDown = False
        self.flyingUp = False
        self.waiting = False

    def updateTextPosition(self):

        if self.flyingDown and not self.waiting and not self.flyingUp:
            if self.text_rect.y < SCREEN.get_height() - 10:
                # Update text position
                self.text_rect.y += self.delta_y
                # Draw text
                SCREEN.blit(self.text_surface, self.text_rect)
                pygame.display.update()
            else:
                self.reset()
        if self.flyingUp and not self.waiting and not self.flyingDown:
            if self.text_rect.y > self.flytoposition:
                # Update text position
                self.text_rect.y -= self.delta_y
                # Draw text
                SCREEN.blit(self.text_surface, self.text_rect)
                pygame.display.update()
            else:
                self.waiting = True
                self.flyingDown = False
                self.flyingUp = False
        if self.waiting:
            SCREEN.blit(self.text_surface, self.text_rect)
            pygame.display.update()

    def reset(self):

        self.timer = 0
        self.text_surface = None
        self.text_rect = None
        self.flyingDown = False
        self.flyingUp = False
        self.waiting = False
    def drawCurrentPopUp(self):

        if self.text_surface is not None and self.text_rect is not None:
            # Update text position
            self.updateTextPosition()
            self.flyingUp = True

            if self.waiting:
                elapsed_time = time.time() - self.start_time
                if elapsed_time >= 1:
                    self.timer -= 1
                    self.start_time = time.time()

            if self.timer <= 0:
                self.waiting = False
                self.flyingDown = True
                self.flyingUp = False

    def AddText(self, text, duration):
        self.reset()
        if self.text_surface is None:
            # Create new text surface and rectangle
            self.text_surface = self.font.render(text, True, self.RED)
            self.text_rect = self.text_surface.get_rect(center=(SCREEN.get_width() // 2, SCREEN.get_height() + 30))
            self.timer = duration
            self.start_time = time.time()

class OuterLogins:
    def __init__(self, direction):
        self.direction = direction
        self.active = True
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.font = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 15)
        self.font2 = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 40)

        self.radius = 50  # or any other suitable radius
        self.offset = 200
        self.yval = 160

    def draw(self, leftusername, rightusername):

        leftusername_text = self.font.render(leftusername, True, (0, 0, 0))
        rightusername_text = self.font.render(rightusername, True, (0, 0, 0))

        if self.direction == "right":
            self.rect = pygame.Rect(SCREEN.get_width() / 2 + self.offset - self.radius, self.yval, self.radius*2, self.radius*2)
            SCREEN.blit(rightusername_text, (self.rect.x + self.radius - rightusername_text.get_width()/2, self.rect.y + self.radius*2 + 20))
            self.drawicon(rightusername, "right")
        else:
            self.rect = pygame.Rect(SCREEN.get_width() / 2 - self.offset - self.radius, self.yval, self.radius*2, self.radius*2)
            SCREEN.blit(leftusername_text, (self.rect.x + self.radius - leftusername_text.get_width()/2, self.rect.y + self.radius*2 + 20))
            self.drawicon(leftusername, "left")


    def drawicon(self, username, direction):
        try:
            self.profileimage = pygame.image.load("ProfileImages/"+username+".jpg")
        except:
            self.profileimage = None

        if direction == "left":
            offset = self.offset *-1
        else:
            offset = self.offset

        if self.profileimage != None:

            # ---------------
            aspect_ratio = self.profileimage.get_width() / self.profileimage.get_height()
            new_width = int(aspect_ratio * self.radius * 2)
            new_height = int(self.radius * 2)
            profile_image = pygame.transform.scale(self.profileimage, (new_width, new_height))

            transparent_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            transparent_surface.fill((200, 200, 200))
            pygame.draw.circle(transparent_surface, (255, 255, 255, 0), (new_width // 2, new_height // 2),
                               new_height // 2)
            profile_image.blit(transparent_surface, (0, 0))
            SCREEN.blit(profile_image, (SCREEN.get_width() / 2 - self.radius*2 + offset + 34, self.yval))
            pygame.draw.circle(SCREEN, (0, 0, 0), (SCREEN.get_width() / 2 + offset, self.yval + self.radius), self.radius, 5)

        else:
            questionmark = self.font2.render("?", (0, 0, 0), True)
            pygame.draw.circle(SCREEN, (80, 80, 80), (SCREEN.get_width() / 2 + offset, self.yval + self.radius), self.radius)
            SCREEN.blit(questionmark,(SCREEN.get_width() / 2 - questionmark.get_width() / 2 + offset, 160 + self.radius / 2 + 5))

class CreateAccount:

    def __init__(self, Accounts, text_display):

        self.font = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 18)
        self.width = 200
        self.height = 25
        self.accounts = Accounts
        self.username = ""
        self.password = ""
        self.confirmpassword = ""
        self.active_input = ""
        self.startwidth = 200
        self.cameraFlashValue = 0
        self.flash = False
        self.text_display = text_display
        self.usernamerect = pygame.Rect(SCREEN.get_width() / 2 - self.width / 2, 300, self.width, self.height)
        self.passwordrect = pygame.Rect(SCREEN.get_width() / 2 - self.width / 2, 340, self.width, self.height)
        self.confirmpasswordrect = pygame.Rect(SCREEN.get_width() / 2 - self.width / 2, 380, self.width, self.height)
        self.create_account_text = self.font.render("MAKE ACCOUNT", True, (0, 0, 0))
        self.create_account_button = pygame.Rect(SCREEN.get_width() / 2 - self.create_account_text.get_width() / 2, 420, self.create_account_text.get_width(), 25)
        self.profile_image = None
        self.cameraFlashSpeed = 5
        self.radius = 80
    def draw(self):

        self.cameraFlash()
        radius = self.radius  # or any other suitable radius
        if cap.isOpened():

            ret, frame = cap.read()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))
            aspect_ratio = frame_surface.get_width() / frame_surface.get_height()
            new_width = int(aspect_ratio * radius * 2)
            new_height = int(radius * 2)

            if self.profile_image is None:
                profile_image = pygame.transform.scale(frame_surface, (new_width, new_height))
            else:
                profile_image = pygame.transform.scale(self.profile_image, (new_width, new_height))

            transparent_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            transparent_surface.fill((200, 200, 200))
            pygame.draw.circle(transparent_surface, (255, 255, 255, self.cameraFlashValue), (new_width // 2, new_height // 2),
                               new_height // 2)
            profile_image.blit(transparent_surface, (0, 0))
            profile_image = pygame.transform.flip(profile_image, True, False)
            SCREEN.blit(profile_image, (SCREEN.get_width() // 2 - new_width // 2, 120))
            pygame.draw.circle(SCREEN, (0, 0, 0), (SCREEN.get_width() // 2, 120 + new_height // 2), new_height // 2, 5)
        else:
            pygame.draw.circle(SCREEN, (120, 120, 120), (SCREEN.get_width() / 2, 120 + radius), radius, radius)

        username_text = self.font.render(self.username, True, (0, 0, 0))
        password_text = self.font.render("*" * len(self.password), True, (0, 0, 0))
        confirm_password_text = self.font.render("*" * len(self.confirmpassword), True, (0, 0, 0))

        if password_text.get_width() > self.startwidth:
            self.passwordrect.width = password_text.get_width() + 20
        else:
            self.passwordrect.width = self.startwidth

        if username_text.get_width() > self.startwidth:
            self.usernamerect.width = username_text.get_width() + 20
        else:
            self.usernamerect.width = self.startwidth

        if confirm_password_text.get_width() > self.startwidth:
            self.confirmpasswordrect.width = confirm_password_text.get_width() + 20
        else:
            self.confirmpasswordrect.width = self.startwidth

        self.passwordrect.x = SCREEN.get_width() / 2 - self.passwordrect.width / 2
        self.usernamerect.x = SCREEN.get_width() / 2 - self.usernamerect.width / 2
        self.confirmpasswordrect.x = SCREEN.get_width() / 2 - self.confirmpasswordrect.width / 2

        input_rects = [self.usernamerect, self.passwordrect, self.confirmpasswordrect]
        input_names = ["username", "password", "confirmpassword"]
        colors = [(120, 120, 120), (80, 80, 80)]
        results = []

        for rect, name in zip(input_rects, input_names):
            color = colors[0] if self.active_input == name else colors[1]
            results.append(color)

        pygame.draw.rect(SCREEN, results[0], self.usernamerect)
        pygame.draw.rect(SCREEN, results[1], self.passwordrect)
        pygame.draw.rect(SCREEN, results[2], self.confirmpasswordrect)

        pygame.draw.circle(SCREEN, results[1], (self.passwordrect.x, self.passwordrect.y + self.passwordrect.height/2), self.passwordrect.height/2)
        pygame.draw.circle(SCREEN, results[1], (self.passwordrect.x + self.passwordrect.width, self.passwordrect.y + self.passwordrect.height/2), self.passwordrect.height/2)
        pygame.draw.circle(SCREEN, results[0], (self.usernamerect.x, self.usernamerect.y + self.usernamerect.height/2), self.usernamerect.height/2)
        pygame.draw.circle(SCREEN, results[0], (self.usernamerect.x + self.usernamerect.width, self.usernamerect.y + self.usernamerect.height/2), self.usernamerect.height/2)
        pygame.draw.circle(SCREEN, results[2], (self.confirmpasswordrect.x, self.confirmpasswordrect.y + self.confirmpasswordrect.height/2), self.confirmpasswordrect.height/2)
        pygame.draw.circle(SCREEN, results[2], (self.confirmpasswordrect.x + self.confirmpasswordrect.width, self.confirmpasswordrect.y + self.confirmpasswordrect.height/2), self.confirmpasswordrect.height/2)

        SCREEN.blit(self.create_account_text, (self.create_account_button.centerx - self.create_account_text.get_width()/2, self.create_account_button.centery - 3))
        offset = 5
        SCREEN.blit(username_text, (self.usernamerect.center[0] - username_text.get_width()/2, self.usernamerect.y + offset))
        SCREEN.blit(password_text, (self.passwordrect.center[0] - password_text.get_width()/2, self.passwordrect.y + offset -2))
        SCREEN.blit(confirm_password_text, (self.confirmpasswordrect.center[0] - confirm_password_text.get_width()/2, self.confirmpasswordrect.y + offset - 2))

        if len(self.password) == 0 and self.active_input != "password":
            password_text2 = self.font.render("Type password", True, (200, 200, 200))
            SCREEN.blit(password_text2, (self.passwordrect.center[0] - password_text2.get_width()/2, self.passwordrect.y + offset))
        if len(self.confirmpassword) == 0 and self.active_input != "confirmpassword":
            confirm_password_text2 = self.font.render("Retype password", True, (200, 200, 200))
            SCREEN.blit(confirm_password_text2,(self.confirmpasswordrect.center[0] - confirm_password_text2.get_width() / 2, self.confirmpasswordrect.y + offset))

        if len(self.username) == 0 and self.active_input != "username":
            username_text2 = self.font.render("Type username", True, (200, 200, 200))
            SCREEN.blit(username_text2, (self.usernamerect.center[0] - username_text2.get_width()/2, self.usernamerect.y + offset))

        self.text_display.drawCurrentPopUp()

    def cameraFlash(self):

        if self.flash:
            self.cameraFlashValue = 255
            self.flash = False
        else:
            if self.cameraFlashValue != 0:
                if self.cameraFlashValue - self.cameraFlashSpeed < 0:
                    self.cameraFlashValue = 0
                else:
                    self.cameraFlashValue -= self.cameraFlashSpeed


    def create_profile_image(self):

        ret, frame = cap.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))
        aspect_ratio = frame_surface.get_width() / frame_surface.get_height()
        new_width = int(aspect_ratio * self.radius * 2)
        new_height = int(self.radius * 2)
        profile_image = pygame.transform.scale(frame_surface, (new_width, new_height))
        self.profile_image = profile_image

    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if self.active_input == "username":
                        self.active_input = "password"
                    elif self.active_input == "password":
                        self.active_input = "confirmpassword"
                    elif self.active_input == "confirmpassword":
                        self.active_input = "username"

                elif event.key == pygame.K_RETURN:
                    X, Y = self.createAccount()
                    return X, Y

                elif event.key == pygame.K_ESCAPE:
                    if self.active_input == "" and self.profile_image == None:
                        return False, True
                    else:
                        self.cameraFlashValue = 0
                        self.active_input = ""
                        self.profile_image = None

                elif event.key == pygame.K_SPACE and self.active_input == "" and self.profile_image == None:

                    self.flash = True
                    self.create_profile_image()

                elif self.active_input == "username":
                    if event.key == pygame.K_BACKSPACE:
                        # Handle backspace
                        if len(self.username) > 0:
                            self.username = self.username[:-1]
                    elif event.key < 256:
                        # Check if the pressed key is a printable character
                        char = chr(event.key)
                        skip = True
                        if event.key == pygame.K_SPACE:
                            if len(self.username.replace(" ", "")) == 0:
                                skip = False

                        if char.isprintable() and len(self.username) < USERNAMEMAXCHAR and skip:  # Check for printable character excluding space
                            # Allow both uppercase and lowercase characters
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT or pygame.key.get_mods() & pygame.KMOD_CAPS:
                                self.username += char.upper()
                            else:
                                self.username += char.lower()

                if self.active_input == "password":
                    if event.key == pygame.K_BACKSPACE:
                        # Handle backspace
                        if len(self.password) > 0:
                            self.password = self.password[:-1]
                    elif event.key < 256:
                        # Check if the pressed key is a printable character
                        char = chr(event.key)
                        if char.isprintable() and char != ' ' and len(self.password) < PASSWORDMAXCHAR:  # Check for printable character excluding space
                            # Allow both uppercase and lowercase characters
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT or pygame.key.get_mods() & pygame.KMOD_CAPS:
                                self.password += char.upper()
                            else:
                                self.password += char.lower()

                if self.active_input == "confirmpassword":
                    if event.key == pygame.K_BACKSPACE:
                        # Handle backspace
                        if len(self.confirmpassword) > 0:
                            self.confirmpassword = self.confirmpassword[:-1]
                    elif event.key < 256:
                        # Check if the pressed key is a printable character
                        char = chr(event.key)
                        if char.isprintable() and char != ' ' and len(
                                self.confirmpassword) < PASSWORDMAXCHAR:  # Check for printable character excluding space
                            # Allow both uppercase and lowercase characters
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT or pygame.key.get_mods() & pygame.KMOD_CAPS:
                                self.confirmpassword += char.upper()
                            else:
                                self.confirmpassword += char.lower()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.passwordrect.collidepoint(mouse_pos):
                    self.active_input = "password"
                if self.usernamerect.collidepoint(mouse_pos):
                    self.active_input = "username"
                if self.confirmpasswordrect.collidepoint(mouse_pos):
                    self.active_input = "confirmpassword"
                elif not self.passwordrect.collidepoint(mouse_pos) and not self.usernamerect.collidepoint(mouse_pos):
                    self.active_input = ""
                if self.create_account_button.collidepoint(mouse_pos):
                    X, Y = self.createAccount()
                    return X, Y

            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        return False, False

    def createAccount(self):

        Result = self.CheckUserNameAvailable()
        if Result:
            if self.profile_image == None:
                self.create_profile_image()

            if self.profile_image.get_width() > PROFILEIMAGEWIDTH:
                new_width = PROFILEIMAGEWIDTH
                crop_x = (self.profile_image.get_width() - new_width) // 2
                crop_y = 0
                crop_width = PROFILEIMAGEWIDTH
                crop_height = self.profile_image.get_height()
                self.profile_image = self.profile_image.subsurface((crop_x, crop_y, crop_width, crop_height))
            image_data = pygame.surfarray.array3d(self.profile_image)
            rotated_image_data = np.rot90(image_data, k=3)
            # Convert RGB to BGR (OpenCV uses BGR format)
            image_data = cv2.cvtColor(rotated_image_data, cv2.COLOR_RGB2BGR)
            Continue = image_check(image_data)
            if Continue:
                with open("Passwords/" + self.username + ".txt", "w") as file:
                    file.write(self.password)
                cv2.imwrite("ProfileImages/" + self.username + ".jpg", image_data)
                file.close()
                self.details, self.accounts = createData()

                lst = []
                for path in os.listdir("images"):
                    lst.append(path)
                sorted_list = sorted(lst, reverse=True)
                if len(lst) == 0:
                    largest_prefix = 0
                else:
                    largest_prefix = int(sorted_list[0].split('.')[0])
                # Example usage:
                my_list = ["0.0", "4.3", "2.1", "1.9"]
                numphotos = faceScanSetUp(self, largest_prefix + 1, self.username, SCREEN)
                if numphotos < MINPHOTOSFORFACEID:
                    self.text_display.AddText("Not enough photos for account creation, please try again and stare into camera", 5)
                    DeleteAccount(self.username)
                    self.profile_image = None
                    return False, False
                else:
                    self.text_display.AddText("FACE ID added for "+self.username, 5)
                    return True, False
            else:
                self.text_display.AddText("Face is already in use for another account", 5)
                return False, False
        else:
            return False, False
    def CheckUserNameAvailable(self):

        _, accounts = createData()
        accounts = [account.lower().replace(" ", "") for account in accounts]
        # Now modified_accounts contains the modified strings
        if self.username.lower().replace(" ", "") in accounts:
            self.username = ""
            self.text_display.AddText("Username already in use!", 3)

        else:
            if len(self.password) >= MINPASSWORDLENGTH:
                if len(self.username) >= MINUSERNAMELENGTH:
                    if self.password == self.confirmpassword or DEBUG:
                        return True
                    else:
                        self.active_input = ""
                        self.password = ""
                        self.confirmpassword = ""
                        self.text_display.AddText("Passwords dont match!", 3)
                else:
                    self.text_display.AddText("Username not long enough!", 3)
            else:
                self.text_display.AddText("Password not long enough!", 3)
                self.password = ""
                self.confirmpassword = ""
    def run(self):

        Loop = True
        while Loop:
            SCREEN.fill((200, 200, 200))
            self.draw()
            pygame.display.update()
            AccountCreated, Exit = self.handle_events()
            if AccountCreated:
                return True
            if Exit:
                return False
            clock.tick(FPS)
class UserLogin:
    def __init__(self, Details, Accounts):
        pygame.init()
        self.details = Details
        self.accounts = Accounts
        self.selectedAccount = 0
        self.usernamefont = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 28)
        self.font = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 18)
        self.font2 = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 50)
        self.text_display = TextPopUp()
        self.width = 200
        self.height = 25
        self.timecheck = 0
        self.cooldowns = {}
        if len(self.accounts) > 0:
            self.username = self.accounts[self.selectedAccount]
        else:
            self.username = "No Accounts"
        self.password = ""
        self.active_input = ""
        self.set_up()
    def refresh_values(self):

        self.details, self.accounts = createData()
        self.set_up()

        if len(self.accounts) > 0:
            self.username = self.accounts[self.selectedAccount]
        else:
            self.username = "No Accounts"
        train()
    def set_up(self):

        self.usernamerect = pygame.Rect(SCREEN.get_width()/2 - self.width/2, 250, self.width, self.height)
        self.login_button = pygame.Rect(SCREEN.get_width()/2 - 100/2, 350, 100, 25)
        self.create_account_text = self.font.render("CREATE ACCOUNT", True, (0, 0, 0))
        self.create_account_button = pygame.Rect(SCREEN.get_width()/2 - self.create_account_text.get_width()/2, 380, self.create_account_text.get_width(), 25)
        self.face_ID_button = pygame.Rect(SCREEN.get_width()/2 - 15, 420, 30, 30)
        self.faceidimage = pygame.image.load("UI images/faceidimage.png")
        self.faceidimage = pygame.transform.scale(self.faceidimage, (self.face_ID_button.width, self.face_ID_button.height))
        self.leftaccount = None
        self.rightaccount = None
        self.face_id_cooldown = 0

        if len(self.accounts) == 2:
            self.leftaccount = OuterLogins("left")
            self.rightaccount = None

        if len(self.accounts) > 2:
            self.leftaccount = OuterLogins("left")
            self.rightaccount = OuterLogins("right")
    def handle_events(self):

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if self.active_input == "password" and len(self.accounts) > 0:
                    if event.key == pygame.K_BACKSPACE:
                        # Handle backspace
                        if len(self.password) > 0:
                            self.password = self.password[:-1]
                    elif event.key < 256:
                        # Check if the pressed key is a printable character
                        char = chr(event.key)
                        if char.isprintable() and char != ' ':  # Check for printable character excluding space
                            # Allow both uppercase and lowercase characters
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT or pygame.key.get_mods() & pygame.KMOD_CAPS:
                                self.password += char.upper()
                            else:
                                self.password += char.lower()
                    if event.key == pygame.K_RETURN:
                        Result = self.checkPasswordUserName()
                        if Result == False:
                            self.password = ""
                        elif Result:
                            return True
                    if event.key == pygame.K_ESCAPE:
                        self.active_input = ""

            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_time = time.time()
                mouse_pos = pygame.mouse.get_pos()
                if self.passwordrect.collidepoint(mouse_pos):
                    self.active_input = "password"
                elif not self.passwordrect.collidepoint(mouse_pos):
                    self.active_input = ""
                if self.login_button.collidepoint(mouse_pos):
                    Result = self.checkPasswordUserName()
                    if Result == False:
                        self.password = ""
                    elif Result:
                        return True
                if self.create_account_button.collidepoint(mouse_pos):
                    New = CreateAccount(self.accounts, self.text_display)
                    Created = New.run()
                    if Created:
                        self.refresh_values()

                if self.face_ID_button.collidepoint(mouse_pos) and current_time >= self.face_id_cooldown:
                    self.face_id_cooldown = current_time + FACE_ID_COOLDOWN_DURATION  # Set cooldown
                    if len(self.accounts) > 0:
                        confidence, normalised = face_check(FACEIDCHECKTIME, SCREEN, self)
                        try:
                            max_user = max(normalised, key=normalised.get)
                            parts = max_user.split('.')
                            id = parts[0].strip()  # Get the ID part
                            username = parts[1].strip()
                        except:
                            self.text_display.AddText("No face was detected, please Enter Password or Try again", 5)
                            id = -1
                        try:
                            print("EXPECTED USER ",username)
                            print(confidence)
                            if self.username == username:
                                if confidence.get(max_user) > FACEIDTHRESHOLD:
                                    self.text_display.AddText("Face ID succesful, Welcome " + username, 6)
                                    numphotos = runFaceScan(self, SCREEN, id, UPDATEPHOTONUM, username, False)
                                    # numphotos does not matter here as it just scans to improve the ML
                                    train()
                                    with open("Passwords/"+username+".txt", "r") as file:
                                        password = file.readline()
                                    self.password = password
                                else:
                                    self.text_display.AddText("Face not recongised / Face not clear enough", 4)
                            else:
                                if confidence.get(max_user) > FACEIDTHRESHOLD:
                                    self.text_display.AddText("Please select correct account", 4)
                                else:
                                    self.text_display.AddText("Face not recongised / Face not clear enough", 4)

                        except:
                            pass # No faces seen error
                    else:
                        self.text_display.AddText("No account selected", 4)

                if self.leftaccount != None and self.leftaccount.rect.collidepoint(mouse_pos):
                    if self.selectedAccount > 0:
                        self.selectedAccount -= 1
                    else:
                        self.selectedAccount = len(self.accounts) - 1
                    self.username = self.accounts[self.selectedAccount]
                    self.password = ""
                elif self.rightaccount != None and self.rightaccount.rect.collidepoint(mouse_pos):
                    if self.selectedAccount < len(self.accounts) - 1:
                        self.selectedAccount += 1
                    else:
                        self.selectedAccount = 0
                    self.username = self.accounts[self.selectedAccount]
                    self.password = ""

            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    def draw(self):
        try:
            self.profileimage = pygame.image.load("ProfileImages/"+self.username+".jpg")
        except:
            self.profileimage = None

        radius = 60  # or any other suitable radius
        if self.profileimage != None:

            aspect_ratio = self.profileimage.get_width() / self.profileimage.get_height()
            new_width = int(aspect_ratio * radius * 2)
            new_height = int(radius * 2)
            profile_image = pygame.transform.scale(self.profileimage, (new_width, new_height))

            transparent_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            transparent_surface.fill((200, 200, 200))
            pygame.draw.circle(transparent_surface, (255, 255, 255, 0), (new_width // 2, new_height // 2),
                               new_height // 2)
            profile_image.blit(transparent_surface, (0, 0))
            SCREEN.blit(profile_image, (SCREEN.get_width() // 2 - new_width // 2, 120))
            pygame.draw.circle(SCREEN, (0, 0, 0), (SCREEN.get_width() // 2, 120 + new_height // 2), new_height // 2, 5)
        else:
            questionmark = self.font2.render("?", (0, 0, 0), True)
            pygame.draw.circle(SCREEN, (120, 120, 120), (SCREEN.get_width() / 2, 120 + radius), radius)
            SCREEN.blit(questionmark, (SCREEN.get_width()/2 - questionmark.get_width()/2, 120 + radius/2 + 5))

        self.passwordrect = pygame.Rect(SCREEN.get_width()/2 - self.width/2, 310, self.width, self.height)
        username_text = self.usernamefont.render(self.username, True, (0, 0, 0))
        password_text = self.font.render("*" * len(self.password), True, (0, 0, 0))
        login_text = self.font.render("LOGIN", True, (0, 0, 0))

        Left = ""
        Right = ""
        try:
            if self.selectedAccount > 0:
                Left = self.accounts[self.selectedAccount-1]
            else:
                Left = self.accounts[len(self.accounts)-1]
        except:
            pass

        try:
            if self.selectedAccount < len(self.accounts) - 1:
                Right = self.accounts[self.selectedAccount+1]
            else:
                Right = self.accounts[0]
        except:
            pass

        if self.leftaccount != None:
            self.leftaccount.draw(Left, Right)
        if self.rightaccount != None:
            self.rightaccount.draw(Left, Right)

        if password_text.get_width() > self.passwordrect.width:
            self.passwordrect.width = password_text.get_width() + 20
            self.passwordrect.x = SCREEN.get_width()/2 - self.passwordrect.width/2
        else:
            self.passwordrect.width = 200


        if self.active_input == "password" and len(self.accounts) > 0:
            colour = (120, 120, 120)
        else:
            colour = (80, 80, 80)

        pygame.draw.rect(SCREEN, colour, self.passwordrect)
        pygame.draw.circle(SCREEN, colour, (self.passwordrect.x, self.passwordrect.y + self.passwordrect.height/2), self.passwordrect.height/2)
        pygame.draw.circle(SCREEN, colour, (self.passwordrect.x + self.passwordrect.width, self.passwordrect.y + self.passwordrect.height/2), self.passwordrect.height/2)

        rect = pygame.Rect(self.face_ID_button.x + 4, self.face_ID_button.y + 4, self.face_ID_button.width - 8, self.face_ID_button.height - 8)
        if time.time() >= self.face_id_cooldown:
            pygame.draw.rect(SCREEN, (180, 180, 180), rect)
        else:
            pygame.draw.rect(SCREEN, (120, 120, 120), rect)
        SCREEN.blit(self.faceidimage, (self.face_ID_button.x, self.face_ID_button.y))
        pygame.draw.rect(SCREEN, (200, 200, 200), self.login_button)
        SCREEN.blit(login_text, (self.login_button.centerx - login_text.get_width()/2, self.login_button.centery))
        SCREEN.blit(self.create_account_text, (self.create_account_button.centerx - self.create_account_text.get_width()/2, self.create_account_button.centery - 3))
        #pygame.draw.rect(SCREEN, "red", self.create_account_button)
        offset = 5
        SCREEN.blit(username_text, (self.usernamerect.center[0] - username_text.get_width()/2, self.usernamerect.center[1] - username_text.get_height()/2))
        SCREEN.blit(password_text, (self.passwordrect.center[0] - password_text.get_width()/2, self.passwordrect.center[1] - password_text.get_height()/2))
        if len(self.password) == 0 and self.active_input != "password":
            password_text2 = self.font.render("Type password", True, (200, 200, 200))
            SCREEN.blit(password_text2, (self.passwordrect.center[0] - password_text2.get_width()/2, self.passwordrect.y +2))

        self.text_display.drawCurrentPopUp()

    def checkPasswordUserName(self):

        username = self.username
        password = self.password

        if username in self.details:
            if password == self.details[username]:
                return True
            else:
                if len(password) == 0:
                    self.text_display.AddText("Please enter password", 3)
                else:
                    self.text_display.AddText("Details incorrect", 3)
                return False
        else:
            return None

    def run(self):

        current_time = pygame.time.get_ticks()
        last_execution_time = self.cooldowns.get("handle_events", 0)
        if current_time - last_execution_time >= 200:
            getattr(self, "handle_events")()  # Call the method dynamically using getattr
            self.cooldowns["handle_events"] = current_time
        self.draw()
        Login = self.handle_events()
        if Login is not None:
            self.password = ""
            self.active_input = ""
            self.text_display.reset()
            return self.username


class Account:

    def __init__(self, accountname):
        self.accountname = accountname
        self.display_text = TextPopUp()
        self.font = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 56)
        self.font2 = pygame.font.Font("UI images/Inconsolata-Regular.ttf", 25)
        self.logoutrect = pygame.Rect(10, SCREEN.get_height() - 100, 120, 40)
        self.deleteaccount = pygame.Rect(10, SCREEN.get_height() - 50, 200, 40)

    def event_handler(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.logoutrect.collidepoint(mouse_pos):
                    return True
                if self.deleteaccount.collidepoint(mouse_pos):
                    DeleteAccount(self.accountname)
                    return True

    def draw(self):

        pygame.draw.rect(SCREEN, "grey", self.logoutrect)
        pygame.draw.rect(SCREEN, "grey", self.deleteaccount)

        current_time = datetime.now().strftime("%H:%M:%S")
        logouttext = self.font2.render("Log Out", True, "white")
        SCREEN.blit(logouttext, (self.logoutrect.center[0] - logouttext.get_width()/2, self.logoutrect.center[1] - logouttext.get_height()/2))

        deleteaccount = self.font2.render("Delete Account", True, "red")
        SCREEN.blit(deleteaccount, (self.deleteaccount.center[0] - deleteaccount.get_width() / 2,self.deleteaccount.center[1] - deleteaccount.get_height() / 2))

        # Draw current time text
        time_text = self.font.render(current_time, True, "white")
        SCREEN.blit(time_text, (SCREEN.get_width() - time_text.get_width() - 20, SCREEN.get_height() - time_text.get_height() - 20))

        self.display_text.drawCurrentPopUp()


    def run(self):

        self.draw()
        goback = self.event_handler()
        return goback

running = True
clock = pygame.time.Clock()

Details, Accounts = createData()
Login = UserLogin(Details, Accounts)

while running:

    SCREEN.fill((200, 200, 200))
    accountName = Login.run()
    pygame.display.update()

    if accountName != None:
        running2 = True
        account = Account(accountName)
        if accountName == None:
            accountName = "" # For Debugging
        account.display_text.AddText("Signed in as " + accountName, 5)
        while running2:
            SCREEN.fill((200, 200, 200))
            goback = account.run()
            if goback:
                Login.refresh_values()
                running2 = False
            pygame.display.update()

    clock.tick(FPS)


