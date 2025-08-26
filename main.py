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
PIPE = 'assets/sprites/pipe.png'

def welcomeScreen():
    """
    Shows welcome images on the screen
    """
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    
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
        
        # Draw everything every frame (moved outside the event loop)
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
        SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))    
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENHEIGHT/2)  # Fixed: was using SCREENWIDTH instead of SCREENHEIGHT
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

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
        if crashTest:
            return     

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}") 
                GAME_SOUNDS['point'].play()

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
        
        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        
        # Draw pipes without debug borders
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        # Draw base without debug border
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        
        # Draw player without debug border
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        
        # Add motion trail effect to make movement more visible
        if hasattr(mainGame, 'player_trail'):
            mainGame.player_trail.append((playerx + GAME_SPRITES['player'].get_width()//2, playery + GAME_SPRITES['player'].get_height()//2))
            if len(mainGame.player_trail) > 5:  # Keep last 5 positions
                mainGame.player_trail.pop(0)
            
            # Draw trail
            for i, (trail_x, trail_y) in enumerate(mainGame.player_trail):
                pygame.draw.circle(SCREEN, (255, 100, 100), (int(trail_x), int(trail_y)), 3-i)
        else:
            mainGame.player_trail = []
        
        # Debug: Print player position every 60 frames
        if pygame.time.get_ticks() % 1000 < 50:  # Print roughly every second
            print(f"Player at: ({playerx}, {playery}), Pipes at: {[p['x'] for p in upperPipes]}")
        
        # Score display - move to top right corner and make smaller
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        
        # Position score in top right instead of center
        Xoffset = SCREENWIDTH - width - 10  # 10 pixels from right edge

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, 10))  # 10 pixels from top
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    # Adjust collision detection for transparent backgrounds
    # Add some padding to make collision more forgiving
    collision_padding = 5
    
    # Check ground and ceiling collision
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True
    
    # Get player boundaries with padding
    player_left = playerx + collision_padding
    player_right = playerx + GAME_SPRITES['player'].get_width() - collision_padding
    player_top = playery + collision_padding
    player_bottom = playery + GAME_SPRITES['player'].get_height() - collision_padding
    
    # Check upper pipe collision
    for pipe in upperPipes:
        pipe_left = pipe['x']
        pipe_right = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()
        pipe_bottom = pipe['y'] + GAME_SPRITES['pipe'][0].get_height()
        
        # Check if player overlaps with upper pipe
        if (player_right > pipe_left and player_left < pipe_right and 
            player_top < pipe_bottom):
            GAME_SOUNDS['hit'].play()
            return True

    # Check lower pipe collision  
    for pipe in lowerPipes:
        pipe_left = pipe['x']
        pipe_right = pipe['x'] + GAME_SPRITES['pipe'][1].get_width()
        pipe_top = pipe['y']
        
        # Check if player overlaps with lower pipe
        if (player_right > pipe_left and player_left < pipe_right and 
            player_bottom > pipe_top):
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    # Increase the gap between pipes for better gameplay
    gap_size = 120  # Bigger gap between upper and lower pipes
    offset = SCREENHEIGHT/3
    
    # Calculate pipe positions with proper gap
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = y2 - gap_size - pipeHeight  # Upper pipe position with gap
    
    pipe = [
        {'x': pipeX, 'y': y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe  
    ]
    return pipe

if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by Kishor Bharti')
    
    # Load and scale number sprites (scale them down from their original size)
    number_sprites = []
    for i in range(10):
        num_img = pygame.image.load(f'assets/sprites/{i}.png').convert_alpha()
        # Scale numbers to reasonable size (assuming they're also quite large)
        scaled_num = pygame.transform.scale(num_img, (24, 36))  # Much smaller numbers
        number_sprites.append(scaled_num)
    GAME_SPRITES['numbers'] = tuple(number_sprites)

    # Load and scale message sprite (920x920 -> much smaller)
    message_img = pygame.image.load('assets/sprites/message.png').convert_alpha()
    GAME_SPRITES['message'] = pygame.transform.scale(message_img, (150, 150))  # Much smaller
    
    # Load and scale base sprite (860x319 -> fit screen properly with good height)
    base_img = pygame.image.load('assets/sprites/base.png').convert_alpha()
    base_height = int(SCREENHEIGHT - GROUNDY)  # Calculate proper base height
    GAME_SPRITES['base'] = pygame.transform.scale(base_img, (SCREENWIDTH, base_height))
    
    # Load and scale pipe sprites (228x821 -> reasonable game size with better spacing)
    pipe_img = pygame.image.load(PIPE).convert_alpha()
    pipe_scaled = pygame.transform.scale(pipe_img, (52, 320))  # Standard Flappy Bird pipe size
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pipe_scaled, 180), pipe_scaled)

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point.mp3')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh.mp3')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing.mp3')

    # Load and scale background properly (1920x696 -> fit screen)
    background_img = pygame.image.load(BACKGROUND).convert()
    # Scale background to fit screen while maintaining aspect ratio
    GAME_SPRITES['background'] = pygame.transform.scale(background_img, (SCREENWIDTH, SCREENHEIGHT))
    
    # Load and scale player sprite (316x372 -> proper size for transparent background)
    player_img = pygame.image.load(PLAYER).convert_alpha()
    print(f"Original player size: {player_img.get_size()}")  # Debug info
    GAME_SPRITES['player_original'] = pygame.transform.scale(player_img, (40, 30))  # Smaller for better collision detection
    GAME_SPRITES['player'] = GAME_SPRITES['player_original']  # Start with no rotation
    print(f"Scaled player size: {GAME_SPRITES['player'].get_size()}")  # Debug info
    
    # Print all sprite info for debugging
    print(f"Screen size: {SCREENWIDTH}x{SCREENHEIGHT}")
    print(f"Ground Y position: {GROUNDY}")
    
    # Add debug rectangles in the game to see where things are
    print("Game initialized - check the red rectangles to see sprite positions!")

    while True:
        welcomeScreen() # Shows welcome screen to the user until he presses a button
        mainGame() # This is the main game function