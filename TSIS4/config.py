SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 400
GRID_SIZE     = 20
GRID_W        = SCREEN_WIDTH  // GRID_SIZE   # 30 cells wide
GRID_H        = SCREEN_HEIGHT // GRID_SIZE   # 20 cells tall
UI_HEIGHT     = 60
FPS           = 60
# Directions
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = ( 1, 0)

# Colors
BLACK      = (0,   0,   0  )
WHITE      = (255, 255, 255)
GREEN      = (0,   220, 0  )
DARK_GREEN = (0,   160, 0  )
RED        = (220, 40,  40 )
DARK_RED   = (120, 0,   0  )   # poison food
YELLOW     = (255, 220, 0  )
ORANGE     = (255, 140, 0  )
BLUE       = (50,  120, 255)
CYAN       = (0,   200, 230)
GRAY       = (120, 120, 120)
DARK_GRAY  = (50,  50,  50 )
PURPLE     = (160, 0,   200)

# DB connection — change to match your setup
DB_HOST = "localhost"
DB_PORT = "1234"
DB_NAME = "snake_db"
DB_USER = "postgres"
DB_PASS = "142536"
