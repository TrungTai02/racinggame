import cv2
import time
import numpy as np
import hand as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pygame
from pygame.locals import *
import random
import threading
import time
pygame.init()


cap = cv2.VideoCapture(0)
pTime = 0

detector = htm.handDetector(detectionCon=0) # Độ tin cậy phát hiện tay 70%

# Xử lý màu nền
GRAY = (100, 100, 100)
GREEN = (76, 208, 23)
YELLOW = (255, 232, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)

# Tạo cửa sổ game
WIDTH = 500
HEIGHT = 500
SCREEN_SIZE = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Racing Game')

# Khởi tạo biến
game_over = False
speed = 2
score = 0

# Đường xe chạy (vạch kẻ trắng)
ROAD_WIDTH = 300
STREET_WIDTH = 10
STREET_HEIGHT = 50

# Lan đường
LANE_LEFT = 150
LANE_CENTER = 250
LANE_RIGHT = 350
lanes = [LANE_LEFT, LANE_CENTER, LANE_RIGHT]


# Road and edge
ROAD = (100, 0, ROAD_WIDTH, HEIGHT)
LEFT_EDGE = (95, 0, STREET_WIDTH, HEIGHT)
RIGHT_EDGE = (395, 0, STREET_WIDTH, HEIGHT)

# Vị trí ban đầu của xe
PLAYER_X = 250
PLAYER_Y = 400

# Khai báo các hằng số màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Khai báo các hằng số kích thước màn hình
screen = pygame.display.set_mode((800, 600))


# Khai báo các hằng số kích thước button
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# Khởi tạo Pygame
pygame.init()

# Tạo cửa sổ game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chọn chế độ điều khiển')

# Font chữ cho button
font = pygame.font.Font(None, 36)
lock = threading.Lock()

# Hàm vẽ button
def draw_button(text, x, y, color):
    button_surface = pygame.Surface((BUTTON_WIDTH, BUTTON_HEIGHT))
    button_surface.fill(color)
    button_rect = button_surface.get_rect()
    button_rect.topleft = (x, y)
    screen.blit(button_surface, button_rect)
    
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = button_rect.center
    screen.blit(text_surface, text_rect)
    
    return button_rect
# Hàm xác định phần trên camera dựa vào tọa độ x
def determine_section(x, width):
    if x < width // 3:
        return "left"
    elif x < 2 * width // 3:
        return "center"
    else:
        return "right"

# Hàm chọn chế độ điều khiển
def select_control_mode():
    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if camera_button_rect.collidepoint(mouse_pos):
                    return "camera"

        # Vẽ button cho chọn chế độ
  
        camera_button_rect = draw_button("Camera", WIDTH/2 - BUTTON_WIDTH/2, HEIGHT/2 + BUTTON_HEIGHT, RED)

        pygame.display.flip()
# Hàm đếm ngược và hiển thị thông báo
def countdown():
    screen.fill((255, 255, 255, 0))
    global countdown_finished
    font = pygame.font.Font(pygame.font.get_default_font(), 64)
    for i in range(3, 0, -1):
        text = font.render(str(i), True, BLACK)
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)  # Tạm dừng 1 giây
        screen.fill(WHITE)
        pygame.display.flip()

    # Hiển thị "Go!"
    text = font.render("Go!", True, GREEN)
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(500)  # Tạm dừng 0.5 giây


# Chọn chế độ điều khiển
control_mode = select_control_mode()
print("Chế độ điều khiển đã chọn:", control_mode)
# Sau khi chọn chế độ điều khiển, thực hiện đếm ngược
countdown()

def control_game_with_camera():
    while True:  
        ret, frame = cap.read()
        frame = detector.findHands(frame)
        lmList = detector.findPosition(frame, draw=False)  # Phát hiện vị trí, đẩy vào list các vị trí
        if len(lmList)!= 0:
            x2, y2 = lmList[8][1], lmList[8][2]  # Lấy tọa độ x, y của điểm trên ngón trỏ

            # Vẽ 1 đường tròn trên 2 đầu ngón cái và ngón trỏ
            cv2.circle(frame, (x2, y2), 15, (255, 0, 255), -1)
            current_lane = LANE_CENTER if player.rect.center[0] < LANE_CENTER else (LANE_LEFT if player.rect.center[0] < LANE_RIGHT else LANE_RIGHT)
            # Xác định phần của màn hình mà ngón trỏ đang ở
            section = determine_section(x2, frame.shape[1])
            if section == "left":
                player.rect.x = LANE_RIGHT
            if section == "right":
                player.rect.x = LANE_LEFT
            if section == "center":
                player.rect.x = LANE_CENTER

        # Vẽ đường kẻ để chia màn hình thành 3 phần
        cv2.line(frame, (frame.shape[1] // 3, 0), (frame.shape[1] // 3, frame.shape[0]), (0, 255, 255), 2)
        cv2.line(frame, (2 * frame.shape[1] // 3, 0), (2 * frame.shape[1] // 3, frame.shape[0]), (0, 255, 255), 2)
        
        # Lật ngược hình ảnh
        frame = cv2.flip(frame, flipCode=1)
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord("q"):  # Độ trễ 1/1000s , nếu bấm q sẽ thoát
            break
    cap.release()  # Giải phóng camera
    cv2.destroyAllWindows()  # Đóng tất cả các cửa sổ của OpenCV


    
    # Đối tượng xe lưu thông - vehicle
class Vehicle(pygame.sprite.Sprite):
        def __init__(self, image, x, y):
            pygame.sprite.Sprite.__init__(self)
            # Scale image
            image_scale = 45 / image.get_rect().width
            new_width = image.get_rect().width * image_scale
            new_height = image.get_rect().height * image_scale
            self.image = pygame.transform.scale(image, (int(new_width), int(new_height)))
            self.rect = self.image.get_rect()
            self.rect.center = [x, y]

    # Đối tượng xe player
class PlayerVehicle(Vehicle):
        def __init__(self, x, y):
            image = pygame.image.load('images/car.png')
            super().__init__(image, x, y)

    # Sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()


    # Tạo xe người chơi
player = PlayerVehicle(PLAYER_X, PLAYER_Y)
player_group.add(player)

    # Load hình ảnh các loại xe lưu thông
image_names = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for name in image_names:
    image = pygame.image.load('images/' + name)
    vehicle_images.append(image)

    # Load hình va chạm
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()


def control_game_with_pygame():
    # Vòng lặp sử lý game
    global section
    section = None
    global lane_move_y
    lane_move_y = 0
    speed = 1
    global score 
    global game_over
    running = True
    while running:
        for event in pygame.event.get():    
            section = control_game_with_camera()
            if event.type == QUIT:
                running = False  
        # Kiểm tra va chạm khi điều khiển
        for vehicle in vehicle_group:
            if pygame.sprite.collide_rect(player, vehicle):
                game_over = True

        # Kiểm tra va chạm khi đứng yên
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            game_over = True
            crash_rect.center = [player.rect.center[0], player.rect.top]

        # Vẽ địa hình cỏ
        screen.fill(GREEN)
        # Vẽ road đường chạy
        pygame.draw.rect(screen, GRAY, ROAD)
        # Vẽ hành lang
        pygame.draw.rect(screen, YELLOW, LEFT_EDGE)
        pygame.draw.rect(screen, YELLOW, RIGHT_EDGE)
        # Vẽ lane đường
        lane_move_y += speed * 2
        if lane_move_y >= STREET_HEIGHT * 2:
            lane_move_y = 0
        for y in range(STREET_HEIGHT * -2, HEIGHT, STREET_HEIGHT * 2):
            pygame.draw.rect(screen, WHITE, (LANE_LEFT + 45, y + lane_move_y, STREET_WIDTH, STREET_HEIGHT))
            pygame.draw.rect(screen, WHITE, (LANE_CENTER + 45, y + lane_move_y, STREET_WIDTH, STREET_HEIGHT))

        # Vẽ xe người chơi
        player_group.draw(screen)

    

        # Vẽ phương tiện giao thông xuất hiện ngẫu nhiên trên đường
        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False
            if add_vehicle:
            
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                # Chọn ngẫu nhiên hướng di chuyển của xe
                vehicle = Vehicle(image, lane, HEIGHT / -2)
                vehicle_group.add(vehicle)

        # Cho xe công cộng được chạy
        for vehicle in vehicle_group:
            vehicle.rect.y += speed
        
        # Hàm vẽ một nhóm xe lưu thông
        def add_vehicle_group():
            for _ in range(2):  # Số lượng xe trong nhóm
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, random.randint(-200, -50))  # Random vị trí ban đầu của xe
                vehicle_group.add(vehicle)

        # Remove vehicle
        if vehicle.rect.top >= HEIGHT:
            vehicle.kill()
            score += 1
            # Tăng tốc độ khó - chạy
            if score > 0 and score % 5 == 0:
                speed += 0.2
                if score > 3:  # Kiểm tra điểm số vượt quá 
                    add_vehicle_group()  # Thêm một nhóm xe lưu thông
        
        
        # Vẽ nhóm xe lưu thông
        vehicle_group.draw(screen)

        # Hiển thị điểm cho người chơi
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render(f'Score: {score}', True, WHITE)
        text_rect = text.get_rect()
        text_rect.center = (50, 40)
        screen.blit(text, text_rect)

        if game_over:
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, RED, (0, 50, WIDTH, 100))
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render(f'Game over! Play again? (Y/ N)', True, WHITE)
            text_rect = text.get_rect()
            text_rect.center = (WIDTH/2, 100)
            screen.blit(text, text_rect)

        # Cập nhật màn hình
        pygame.display.update()

        # Vòng lặp chờ người chơi chọn
        while game_over:
            for event in pygame.event.get():
                if event.type == QUIT:
                    game_over = False
                    running = False

                if event.type == KEYDOWN:
                    if event.key == K_y:
                        # Reset game
                        game_over = False
                        score = 0
                        speed = 0.5
                        vehicle_group.empty()
                        player.rect.center = [PLAYER_X, PLAYER_Y]
                    elif event.key ==  K_n:
                        # Exit game
                        game_over = False
                        running = False


    # Kết thúc pygame
    pygame.quit()



camera_thread = threading.Thread(target=control_game_with_camera)
pygame_thread = threading.Thread(target=control_game_with_pygame)

# Khởi chạy luồng camera trước
camera_thread.start()
# Chờ 3 giây
time.sleep(3)

pygame_thread.start()
