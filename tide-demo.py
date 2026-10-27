import math
import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1250, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visual Tide Demonstration: Sun, Earth, and Moon Forces")

# Colors
BLACK = (10, 10, 25)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
BLUE = (30, 144, 255)
OCEAN_BLUE = (0, 119, 190)
SOLAR_GOLD = (255, 200, 50)
GRAY = (180, 180, 180)
RED = (255, 60, 60)
TEXT_COLOR = (220, 220, 240)
GAUGE_BG = (25, 25, 45)

# Clock for smooth framerate
clock = pygame.time.Clock()

# Simulation Parameters
earth_center = (WIDTH // 2 - 80, HEIGHT // 2)
earth_radius = 55
moon_orbit_radius = 230
sun_distance = 500

# Speeds and Ratios (Earth rotates exactly 28 times per 1 Moon orbit)
base_moon_speed = 0.002
earth_moon_ratio = 28.0

# Simulation State & Controls
moon_enabled = True
time_scale = 1.0          # Controlled by the slider (0.1x to 5.0x)
moon_angle = 0.0
earth_rotation = 0.0
dragging_slider = False

# UI Elements Setup
button_rect = pygame.Rect(WIDTH - 250, 25, 215, 40)
slider_track = pygame.Rect(25, HEIGHT - 55, 220, 8)
slider_min = 0.1
slider_max = 5.0

# Vertical Tide Gauge Setup (Moved inward so text fits nicely on the right)
gauge_x = WIDTH - 180
gauge_y = 120
gauge_w = 26
gauge_h = 460

def val_to_x(val):
    fraction = (val - slider_min) / (slider_max - slider_min)
    return slider_track.x + int(fraction * slider_track.width)

def x_to_val(x):
    fraction = max(0.0, min(1.0, (x - slider_track.x) / slider_track.width))
    return slider_min + fraction * (slider_max - slider_min)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if button_rect.collidepoint(event.pos):
                    moon_enabled = not moon_enabled
                elif slider_track.collidepoint(event.pos) or pygame.Rect(slider_track.x - 10, slider_track.y - 10, slider_track.width + 20, slider_track.height + 20).collidepoint(event.pos):
                    dragging_slider = True
                    time_scale = x_to_val(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_slider = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                time_scale = x_to_val(event.pos[0])

    screen.fill(BLACK)

    # Advance simulation angles based on time_scale
    delta_moon = base_moon_speed * time_scale
    if moon_enabled:
        moon_angle += delta_moon
    
    earth_rotation += delta_moon * earth_moon_ratio

    # Positions
    sun_pos = (earth_center[0] - sun_distance, earth_center[1])
    moon_x = earth_center[0] + moon_orbit_radius * math.cos(moon_angle)
    moon_y = earth_center[1] + moon_orbit_radius * math.sin(moon_angle)
    moon_pos = (int(moon_x), int(moon_y))

    # --- 1. DRAW SUN & RAYS ---
    pygame.draw.circle(screen, YELLOW, sun_pos, 45)
    for i in range(8):
        angle = i * (math.pi / 4)
        rx1 = sun_pos[0] + int(55 * math.cos(angle))
        ry1 = sun_pos[1] + int(55 * math.sin(angle))
        rx2 = sun_pos[0] + int(68 * math.cos(angle))
        ry2 = sun_pos[1] + int(68 * math.sin(angle))
        pygame.draw.line(screen, YELLOW, (rx1, ry1), (rx2, ry2), 3)

    # --- 2. DRAW MOON ORBIT PATH ---
    if moon_enabled:
        pygame.draw.circle(screen, (45, 45, 65), earth_center, moon_orbit_radius, 1)

    # --- 3. CALCULATE & DRAW TIDE BULGES ---
    dx_sun = sun_pos[0] - earth_center[0]
    dy_sun = sun_pos[1] - earth_center[1]
    sun_dir_angle = math.atan2(dy_sun, dx_sun)

    num_points = 180
    tide_points = []
    solar_only_points = []
    base_tide_radius = earth_radius + 6

    lunar_amplitude = 12 if moon_enabled else 0
    solar_amplitude = 8

    for i in range(num_points):
        theta = i * (2 * math.pi / num_points)
        lunar_effect = lunar_amplitude * math.cos(2 * (theta - moon_angle))
        solar_effect = solar_amplitude * math.cos(2 * (theta - sun_dir_angle))

        # Combined tide shape (Blue polygon)
        r = base_tide_radius + lunar_effect + solar_effect
        px = earth_center[0] + r * math.cos(theta)
        py = earth_center[1] + r * math.sin(theta)
        tide_points.append((px, py))

        # Solar component reference shape (Gold ring)
        r_solar = base_tide_radius + solar_effect
        spx = earth_center[0] + r_solar * math.cos(theta)
        spy = earth_center[1] + r_solar * math.sin(theta)
        solar_only_points.append((spx, spy))

    # Render combined ocean tide polygon
    pygame.draw.polygon(screen, OCEAN_BLUE, tide_points)
    pygame.draw.polygon(screen, SOLAR_GOLD, solar_only_points, 1)

    # --- 4. DRAW EARTH & ROTATING MERIDIANS ---
    pygame.draw.circle(screen, BLUE, earth_center, earth_radius)
    
    # Calculate exact tide level above the red dot (spoke index 0)
    main_spoke_angle = earth_rotation
    red_dot_x = earth_center[0] + earth_radius * math.cos(main_spoke_angle)
    red_dot_y = earth_center[1] + earth_radius * math.sin(main_spoke_angle)

    # Water height offset at the red dot's angle
    red_dot_lunar = lunar_amplitude * math.cos(2 * (main_spoke_angle - moon_angle))
    red_dot_solar = solar_amplitude * math.cos(2 * (main_spoke_angle - sun_dir_angle))
    current_tide_offset = red_dot_lunar + red_dot_solar

    for i in range(6):
        meridian_angle = earth_rotation + i * (math.pi / 3)
        mx = earth_center[0] + earth_radius * math.cos(meridian_angle)
        my = earth_center[1] + earth_radius * math.sin(meridian_angle)
        pygame.draw.line(screen, (100, 200, 255), earth_center, (int(mx), int(my)), 1)
        
        if i == 0:
            pygame.draw.circle(screen, RED, (int(red_dot_x), int(red_dot_y)), 5)

    # --- 5. DRAW MOON ---
    if moon_enabled:
        pygame.draw.circle(screen, GRAY, moon_pos, 16)

    # --- 6. LABELS & UI TEXT ---
    font = pygame.font.SysFont("Arial", 15)
    title_font = pygame.font.SysFont("Arial", 20, bold=True)

    screen.blit(title_font.render("SUN", True, YELLOW), (sun_pos[0] - 20, sun_pos[1] - 65))
    screen.blit(title_font.render("EARTH", True, WHITE), (earth_center[0] - 30, earth_center[1] + 70))
    if moon_enabled:
        screen.blit(title_font.render("MOON", True, WHITE), (moon_pos[0] - 22, moon_pos[1] - 35))

    instructions = [
        "Tide Simulation Overview:",
        "• Red Dot: Tracks local point on Earth.",
        "• Vertical Gauge (Right): Displays local tide height at the Red Dot.",
        "• Gold Ring: Constant Solar Bulge baseline.",
    ]
    
    y_offset = 25
    for line in instructions:
        txt_surf = font.render(line, True, TEXT_COLOR)
        screen.blit(txt_surf, (25, y_offset))
        y_offset += 22

    # --- 7. DRAW TOGGLE BUTTON ---
    button_color = (34, 139, 34) if moon_enabled else (178, 34, 34)
    pygame.draw.rect(screen, button_color, button_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, button_rect, 2, border_radius=6)

    btn_text = "Moon: ON (Click to Hide)" if moon_enabled else "Moon: OFF (Click to Show)"
    btn_surf = font.render(btn_text, True, WHITE)
    screen.blit(
        btn_surf,
        (
            button_rect.x + (button_rect.width - btn_surf.get_width()) // 2,
            button_rect.y + (button_rect.height - btn_surf.get_height()) // 2,
        ),
    )

    # --- 8. DRAW TIME SPEED SLIDER ---
    slider_label = font.render(f"Time Speed: {time_scale:.2f}x", True, TEXT_COLOR)
    screen.blit(slider_label, (slider_track.x, slider_track.y - 24))

    pygame.draw.rect(screen, (80, 80, 110), slider_track, border_radius=4)
    handle_x = val_to_x(time_scale)
    handle_rect = pygame.Rect(handle_x - 6, slider_track.y - 6, 12, 20)
    pygame.draw.rect(screen, WHITE, handle_rect, border_radius=4)

    # --- 9. DRAW VERTICAL TIDE HEIGHT GAUGE ---
    max_possible_offset = 20.0
    tide_ratio = (current_tide_offset + max_possible_offset) / (2 * max_possible_offset)
    tide_ratio = max(0.0, min(1.0, tide_ratio))

    fill_height = int(tide_ratio * gauge_h)

    # Gauge background container
    pygame.draw.rect(screen, GAUGE_BG, (gauge_x, gauge_y, gauge_w, gauge_h), border_radius=4)
    
    # Active water level fill
    fill_rect = pygame.Rect(gauge_x, gauge_y + gauge_h - fill_height, gauge_w, fill_height)
    pygame.draw.rect(screen, OCEAN_BLUE, fill_rect, border_radius=4)

    # Outer border & ticks
    pygame.draw.rect(screen, WHITE, (gauge_x, gauge_y, gauge_w, gauge_h), 2, border_radius=4)
    
    # High / Mid / Low Tide Tick Marks
    pygame.draw.line(screen, RED, (gauge_x - 5, gauge_y), (gauge_x + gauge_w + 5, gauge_y), 2)
    pygame.draw.line(screen, WHITE, (gauge_x - 5, gauge_y + gauge_h // 2), (gauge_x + gauge_w + 5, gauge_y + gauge_h // 2), 1)
    pygame.draw.line(screen, GRAY, (gauge_x - 5, gauge_y + gauge_h), (gauge_x + gauge_w + 5, gauge_y + gauge_h), 2)

    # Gauge Labels (Positioned cleanly with ample margin on the right)
    gauge_title = font.render("LOCAL TIDE HEIGHT", True, TEXT_COLOR)
    screen.blit(gauge_title, (gauge_x - 15, gauge_y - 30))

    label_high = font.render("HIGH", True, RED)
    label_low = font.render("LOW", True, GRAY)
    screen.blit(label_high, (gauge_x + gauge_w + 8, gauge_y - 8))
    screen.blit(label_low, (gauge_x + gauge_w + 8, gauge_y + gauge_h - 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()