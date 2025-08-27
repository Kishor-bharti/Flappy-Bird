import random # For generating random numbers
import sys # We will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame imports

# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'assets/sprites/flappy-chad.png'
BACKGROUND = 'assets/sprites/background.png'
BACKGROUND2 = 'assets/sprites/background2.jpg'
PIPE = 'assets/sprites/pipe.png'
HIGH_SCORE = 0  # Global high score variable
current_background = 1  # 1 for background.png, 2 for background2.png

def welcomeScreen():
    """
    Shows welcome images on the screen with high score and title
    """
    # Play intro sound when welcome screen appears
    GAME_SOUNDS['helicopter'].play()
    
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    
    # Font for text rendering
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 20)
    
    # Determine current background to display
    current_bg = GAME_SPRITES['background1'] if current_background == 1 else GAME_SPRITES['background2']
    
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            # If the user presses space or up key, start the game for them
            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                return
        
        # Clear screen first
        SCREEN.fill((0, 0, 0))
        
        # Draw everything every frame with current background
        SCREEN.blit(current_bg, (0, 0))    
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
        SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))    
        
        # Add title text "Flappy Bird Game by Kishor"
        title_text = font_large.render("Flappy Bird", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREENWIDTH//2, 50))
        SCREEN.blit(title_text, title_rect)
        
        author_text = font_medium.render("Game by Kishor", True, (255, 255, 255))
        author_rect = author_text.get_rect(center=(SCREENWIDTH//2, 80))
        SCREEN.blit(author_text, author_rect)
        
        # Add high score display (updated every time)
        highscore_text = font_medium.render(f"High Score: {HIGH_SCORE}", True, (255, 215, 0))  # Gold color
        highscore_rect = highscore_text.get_rect(center=(SCREENWIDTH//2, SCREENHEIGHT - 80))
        SCREEN.blit(highscore_text, highscore_rect)
        
        # Instructions
        instruction_text = font_small.render("Press SPACE or UP to start", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(SCREENWIDTH//2, SCREENHEIGHT - 40))
        SCREEN.blit(instruction_text, instruction_rect)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame():
    global HIGH_SCORE, current_background
    score = 0
    last_background_switch = 0  # Track when we last switched backgrounds
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENHEIGHT/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            # Update high score before returning
            if score > HIGH_SCORE:
                HIGH_SCORE = score
                print(f"New High Score: {HIGH_SCORE}!")
            return     

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}") 
                GAME_SOUNDS['point'].play()
                
                # Check for background switch every 20 scores
                if score > 0 and score % 20 == 0 and score != last_background_switch:
                    # Switch background
                    current_background = 2 if current_background == 1 else 1
                    last_background_switch = score
                    print(f"Background switched to background{current_background} at score {score}!")
                    # Play helicopter sound when switching backgrounds
                    GAME_SOUNDS['helicopter'].play()

        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False            
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        # Clear screen first
        SCREEN.fill((135, 206, 235))  # Sky blue color as fallback
        
        # Use current background
        current_bg = GAME_SPRITES['background1'] if current_background == 1 else GAME_SPRITES['background2']
        SCREEN.blit(current_bg, (0, 0))
        
        # Draw pipes
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        # Draw base
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        
        # Draw player
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        
        # Score display - top right corner
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        
        Xoffset = SCREENWIDTH - width - 10

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, 10))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
            
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def pixelPerfectCollision(sprite1, pos1, sprite2, pos2):
    """
    Check for pixel-perfect collision between two sprites with alpha channels
    """
    # Get the overlapping rectangle
    rect1 = pygame.Rect(pos1, sprite1.get_size())
    rect2 = pygame.Rect(pos2, sprite2.get_size())
    
    if not rect1.colliderect(rect2):
        return False
    
    # Get the overlapping area
    overlap = rect1.clip(rect2)
    
    # Check pixels in the overlapping area
    for x in range(overlap.width):
        for y in range(overlap.height):
            # Calculate positions in both sprites
            pos1_x = overlap.x + x - rect1.x
            pos1_y = overlap.y + y - rect1.y
            pos2_x = overlap.x + x - rect2.x
            pos2_y = overlap.y + y - rect2.y
            
            # Get alpha values at these positions
            try:
                alpha1 = sprite1.get_at((pos1_x, pos1_y))[3]  # Alpha channel
                alpha2 = sprite2.get_at((pos2_x, pos2_y))[3]  # Alpha channel
                
                # If both pixels are not transparent, we have a collision
                if alpha1 > 128 and alpha2 > 128:  # Threshold for "solid" pixels
                    return True
            except IndexError:
                continue  # Skip if out of bounds
    
    return False

def isCollide(playerx, playery, upperPipes, lowerPipes):
    # Check ground collision - use the actual base sprite height
    base_top = GROUNDY
    if playery + GAME_SPRITES['player'].get_height() >= base_top or playery <= 0:
        GAME_SOUNDS['hit'].play()
        return True
    
    player_sprite = GAME_SPRITES['player']
    player_pos = (playerx, playery)
    
    # Check upper pipe collision with pixel-perfect detection
    for pipe in upperPipes:
        pipe_sprite = GAME_SPRITES['pipe'][0]  # Upper pipe (rotated)
        pipe_pos = (pipe['x'], pipe['y'])
        
        if pixelPerfectCollision(player_sprite, player_pos, pipe_sprite, pipe_pos):
            print(f"Pixel-perfect upper pipe collision detected!")
            GAME_SOUNDS['hit'].play()
            return True

    # Check lower pipe collision with pixel-perfect detection
    for pipe in lowerPipes:
        pipe_sprite = GAME_SPRITES['pipe'][1]  # Lower pipe (normal)
        pipe_pos = (pipe['x'], pipe['y'])
        
        if pixelPerfectCollision(player_sprite, player_pos, pipe_sprite, pipe_pos):
            print(f"Pixel-perfect lower pipe collision detected!")
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    gap_size = 120
    offset = SCREENHEIGHT/3
    
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = y2 - gap_size - pipeHeight
    
    pipe = [
        {'x': pipeX, 'y': y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe  
    ]
    return pipe

if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by Kishor Bharti')
    
    # Load and scale number sprites with proper aspect ratio
    number_sprites = []
    for i in range(10):
        num_img = pygame.image.load(f'assets/sprites/{i}.png').convert_alpha()
        scaled_num = pygame.transform.scale(num_img, (24, 36))
        number_sprites.append(scaled_num)
    GAME_SPRITES['numbers'] = tuple(number_sprites)

    # Load and scale message sprite - maintaining square aspect ratio
    message_img = pygame.image.load('assets/sprites/message.png').convert_alpha()
    GAME_SPRITES['message'] = pygame.transform.scale(message_img, (150, 150))
    
    # Load and scale base sprite - maintaining original aspect ratio (860x304)
    base_img = pygame.image.load('assets/sprites/base.png').convert_alpha()
    # Original aspect ratio: 860/304 ≈ 2.83
    base_height = int(SCREENHEIGHT - GROUNDY)
    base_width = int(base_height * 2.83)  # Maintain aspect ratio
    # If calculated width is less than screen width, use screen width
    if base_width < SCREENWIDTH:
        base_width = SCREENWIDTH
    GAME_SPRITES['base'] = pygame.transform.scale(base_img, (base_width, base_height))
    
    # Load and scale pipe sprites - maintaining original aspect ratio (228x821)
    pipe_img = pygame.image.load(PIPE).convert_alpha()
    # Original aspect ratio: 228/821 ≈ 0.278
    pipe_height = 320  # Good height for gameplay
    pipe_width = int(pipe_height * 0.278)  # Maintain aspect ratio
    pipe_scaled = pygame.transform.scale(pipe_img, (pipe_width, pipe_height))
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pipe_scaled, 180), pipe_scaled)

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point.mp3')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh.mp3')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing.mp3')
    GAME_SOUNDS['helicopter'] = pygame.mixer.Sound('assets/audio/helicopter-helicopter.wav')  # New intro sound

    # Load and scale both backgrounds properly - maintaining aspect ratio
    background1_img = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['background1'] = pygame.transform.scale(background1_img, (SCREENWIDTH, SCREENHEIGHT))
    
    background2_img = pygame.image.load(BACKGROUND2).convert()
    GAME_SPRITES['background2'] = pygame.transform.scale(background2_img, (SCREENWIDTH, SCREENHEIGHT))
    
    # Load and scale player sprite - maintaining original aspect ratio (920x920)
    player_img = pygame.image.load(PLAYER).convert_alpha()
    print(f"Original player size: {player_img.get_size()}")
    # Original is square (920x920), so keep it square but smaller
    player_size = 35  # Good size for gameplay
    GAME_SPRITES['player_original'] = pygame.transform.scale(player_img, (player_size, player_size))
    GAME_SPRITES['player'] = GAME_SPRITES['player_original']
    print(f"Scaled player size: {GAME_SPRITES['player'].get_size()}")
    
    print(f"Screen size: {SCREENWIDTH}x{SCREENHEIGHT}")
    print(f"Ground Y position: {GROUNDY}")
    print("Game initialized with fixed aspect ratios!")

    while True:
        welcomeScreen() # Shows welcome screen with high score and title
        mainGame() # Main game function