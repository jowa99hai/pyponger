import sys
import pygame

# Game settings
WIDTH, HEIGHT = 800, 600
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 4, 4
FPS = 60


def main(test_mode: bool = False) -> None:
    """Start the PyPonger game.

    Args:
        test_mode: If True, run only a single frame. This is useful for
            automated tests in headless environments.
    """

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('PyPonger')
    clock = pygame.time.Clock()

    # Game objects
    ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2,
                       BALL_SIZE, BALL_SIZE)
    left_paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2,
                              PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH - 20 - PADDLE_WIDTH,
                               HEIGHT // 2 - PADDLE_HEIGHT // 2,
                               PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_vel_x, ball_vel_y = BALL_SPEED_X, BALL_SPEED_Y
    score_left, score_right = 0, 0
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += PADDLE_SPEED
        if keys[pygame.K_UP] and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED

        ball.x += ball_vel_x
        ball.y += ball_vel_y

        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_vel_y *= -1

        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_vel_x *= -1

        if ball.left <= 0:
            score_right += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_vel_x *= -1
        elif ball.right >= WIDTH:
            score_left += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_vel_x *= -1

        screen.fill((0, 100, 0))  # green field
        pygame.draw.rect(screen, (255, 255, 255), left_paddle)
        pygame.draw.rect(screen, (255, 255, 255), right_paddle)
        pygame.draw.ellipse(screen, (255, 255, 255), ball)
        pygame.draw.aaline(screen, (255, 255, 255), (WIDTH//2, 0), (WIDTH//2, HEIGHT))

        score_text = font.render(f"{score_left} : {score_right}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.flip()
        clock.tick(FPS)

        if test_mode:
            # Exit after a single frame when testing.
            running = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
