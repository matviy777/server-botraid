import pygame
import socketio

WIDTH, HEIGHT = 700, 500

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Камінь Ножиці Папір")

font = pygame.font.SysFont("Arial", 30)
room_font = pygame.font.SysFont("Arial", 22)

socket = socketio.Client()

clock = pygame.time.Clock()


def ask_room_name():
    """Екран введення назви кімнати перед початком гри."""
    room_name = ""
    input_active = True

    input_box = pygame.Rect(
        WIDTH // 2 - 150,
        HEIGHT // 2 - 25,
        300,
        50
    )

    while input_active:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    if room_name.strip():
                        input_active = False

                elif event.key == pygame.K_BACKSPACE:
                    room_name = room_name[:-1]

                else:
                    if len(room_name) < 20 and event.unicode.isprintable():
                        room_name += event.unicode

        screen.fill((40, 40, 40))

        title = font.render(
            "Введіть назву кімнати",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 90
            )
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            input_box,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            input_box,
            width=2,
            border_radius=6
        )

        text_surface = font.render(
            room_name,
            True,
            (0, 0, 0)
        )

        screen.blit(
            text_surface,
            (
                input_box.x + 10,
                input_box.y +
                (input_box.height - text_surface.get_height()) // 2
            )
        )

        hint = room_font.render(
            "Enter — приєднатись",
            True,
            (200, 200, 200)
        )

        screen.blit(
            hint,
            (
                WIDTH // 2 - hint.get_width() // 2,
                HEIGHT // 2 + 40
            )
        )

        pygame.display.flip()
        clock.tick(30)

    return room_name.strip()


# Введення назви кімнати
room = ask_room_name()

status = "Підключення..."
result = ""

my_choice = None
enemy_choice = None

# Чи вже зроблений вибір
choice_made = False

# Який саме варіант вибраний
selected_choice = None


# =========================
# Завантаження картинок
# =========================

rock_img = pygame.image.load("./images/rock.png")
paper_img = pygame.image.load("./images/paper.png")
scissors_img = pygame.image.load("./images/scissors.png")


# Розмір картинок
rock_img = pygame.transform.scale(
    rock_img,
    (160, 160)
)

paper_img = pygame.transform.scale(
    paper_img,
    (160, 160)
)

scissors_img = pygame.transform.scale(
    scissors_img,
    (160, 160)
)


# =========================
# Кнопки
# =========================

buttons = {

    "rock": {
        "image": rock_img,
        "rect": rock_img.get_rect(
            topleft=(60, 260)
        )
    },

    "paper": {
        "image": paper_img,
        "rect": paper_img.get_rect(
            topleft=(270, 260)
        )
    },

    "scissors": {
        "image": scissors_img,
        "rect": scissors_img.get_rect(
            topleft=(480, 260)
        )
    }
}


# =========================
# Socket.IO
# =========================

@socket.event
def connect():
    global status

    status = "Підключено"

    socket.emit(
        "join",
        {
            "room": room
        }
    )


@socket.on("joined")
def joined(data):
    global status

    status = f"Ви гравець №{data['player']}"


@socket.on("game_start")
def game_start():
    global status
    global choice_made
    global result
    global enemy_choice
    global selected_choice

    status = "Гра почалась"

    choice_made = False
    selected_choice = None

    result = ""
    enemy_choice = None


@socket.on("player_left")
def player_left():
    global status

    status = "Суперник вийшов"


@socket.on("room_full")
def room_full():
    global status

    status = "Кімната заповнена"


@socket.on("round_result")
def round_result(data):
    global result
    global enemy_choice
    global choice_made
    global status
    global selected_choice

    enemy_choice = data["enemy_choice"]

    if data["result"] == "draw":
        result = "Нічия!"

    elif data["result"] == "win":
        result = "Перемога!"

    else:
        result = "Поразка!"

    # Можна робити вибір у наступному раунді
    choice_made = False

    # Скидаємо виділення після завершення раунду
    selected_choice = None

    status = "Гра почалась"

    print(result)


# =========================
# Підключення до сервера
# =========================

socket.connect("http://localhost:5000")


# =========================
# Основний цикл гри
# =========================

running = True

while running:

    # =========================
    # Обробка подій
    # =========================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if status == "Гра почалась" and not choice_made:

                chosen = None

                # Камінь
                if buttons["rock"]["rect"].collidepoint(event.pos):
                    chosen = "rock"

                # Папір
                elif buttons["paper"]["rect"].collidepoint(event.pos):
                    chosen = "paper"

                # Ножиці
                elif buttons["scissors"]["rect"].collidepoint(event.pos):
                    chosen = "scissors"

                # Якщо вибір зроблено
                if chosen:

                    # Запам'ятовуємо вибраний варіант
                    selected_choice = chosen

                    socket.emit(
                        "choice",
                        {
                            "room": room,
                            "choice": chosen
                        }
                    )

                    choice_made = True

                    status = "Очікуємо суперника..."


    # =========================
    # Фон
    # =========================

    screen.fill((40, 40, 40))


    # =========================
    # Статус гри
    # =========================

    txt = font.render(
        status,
        True,
        (255, 255, 255)
    )

    screen.blit(
        txt,
        (30, 30)
    )


    # =========================
    # Назва кімнати
    # =========================

    room_txt = room_font.render(
        f"Кімната: {room}",
        True,
        (200, 200, 200)
    )

    screen.blit(
        room_txt,
        (
            WIDTH - room_txt.get_width() - 20,
            20
        )
    )


    # =========================
    # КАРТИНКИ + КОНТУРИ
    # =========================

    for name, button in buttons.items():

        # Якщо ця картинка вибрана
        if selected_choice == name:

            # Чорний контур навколо вибраної картинки
            border_rect = button["rect"].inflate(10, 10)

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                border_rect,
                width=5,
                border_radius=5
            )

        # Малюємо картинку
        screen.blit(
            button["image"],
            button["rect"]
        )


    # =========================
    # ТЕКСТ ПІД КАРТИНКАМИ
    # =========================

    # Якщо вибраний варіант — чорний текст.
    # Інші варіанти — білий текст.

    rock_color = (
        (0, 0, 0)
        if selected_choice == "rock"
        else (255, 255, 255)
    )

    paper_color = (
        (0, 0, 0)
        if selected_choice == "paper"
        else (255, 255, 255)
    )

    scissors_color = (
        (0, 0, 0)
        if selected_choice == "scissors"
        else (255, 255, 255)
    )


    rock_text = font.render(
        "Камінь",
        True,
        rock_color
    )

    paper_text = font.render(
        "Папір",
        True,
        paper_color
    )

    scissors_text = font.render(
        "Ножиці",
        True,
        scissors_color
    )


    # Камінь
    screen.blit(
        rock_text,
        (
            buttons["rock"]["rect"].centerx -
            rock_text.get_width() // 2,
            buttons["rock"]["rect"].bottom + 5
        )
    )


    # Папір
    screen.blit(
        paper_text,
        (
            buttons["paper"]["rect"].centerx -
            paper_text.get_width() // 2,
            buttons["paper"]["rect"].bottom + 5
        )
    )


    # Ножиці
    screen.blit(
        scissors_text,
        (
            buttons["scissors"]["rect"].centerx -
            scissors_text.get_width() // 2,
            buttons["scissors"]["rect"].bottom + 5
        )
    )


    # =========================
    # Вибір суперника
    # =========================

    if enemy_choice:

        screen.blit(
            font.render(
                f"Суперник: {enemy_choice}",
                True,
                (255, 255, 255)
            ),
            (30, 150)
        )


    # =========================
    # Результат
    # =========================

    if result:

        screen.blit(
            font.render(
                result,
                True,
                (255, 255, 0)
            ),
            (30, 220)
        )


    # Оновлення екрану
    pygame.display.flip()


# =========================
# Завершення
# =========================

socket.disconnect()
pygame.quit()