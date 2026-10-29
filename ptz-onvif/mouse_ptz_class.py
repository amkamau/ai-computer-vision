class MousePTZController:
    def __init__(self, camera, max_speed=0.8, deadzone=0.05):
        self.camera = camera
        self.max_speed = max_speed
        self.deadzone = deadzone

    def update(self, mouse_x, mouse_y, frame_width, frame_height):

        center_x = frame_width / 2
        center_y = frame_height / 2

        # Distance from center as percentage
        x = (mouse_x - center_x) / center_x
        y = (mouse_y - center_y) / center_y

        # Deadzone around center
        if abs(x) < self.deadzone:
            x = 0

        if abs(y) < self.deadzone:
            y = 0

        # Convert percentage to PTZ speed
        pan_speed = x * self.max_speed
        tilt_speed = -y * self.max_speed

        self.camera.move(
            pan=pan_speed,
            tilt=tilt_speed
        )