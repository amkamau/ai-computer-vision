from onvif import ONVIFClient


class PTZCamera:
    def __init__(self, host, port, username, password, profile_index=0):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.client = None
        self.media = None
        self.ptz = None
        self.profile = None

        self.connect(profile_index)

    def connect(self, profile_index=0):
        """Connect to the camera and initialize ONVIF services."""
        self.client = ONVIFClient(self.host, self.port, self.username, self.password )
        self.media = self.client.media()
        self.ptz = self.client.ptz()

        profiles = self.media.GetProfiles()

        if not profiles:
            raise RuntimeError("No ONVIF media profiles found.")

        if profile_index >= len(profiles):
            raise ValueError(
                f"Profile index {profile_index} does not exist. "
                f"Available profiles: {len(profiles)}"
            )

        self.profile = profiles[profile_index]

        print(f"Connected to PTZ camera: {self.host}")
        print(f"Profile: {self.profile.Name}")
        print(f"Token: {self.profile.token}")

    @staticmethod
    def _clamp(value, minimum=-1.0, maximum=1.0):
        """Keep a value within the ONVIF velocity range."""
        return max(minimum, min(maximum, value))

    def move(self, pan=0.0, tilt=0.0, zoom=0.0):
        """
        Continuous PTZ movement.

        pan:
            -1.0 = left
             0.0 = no pan
             1.0 = right

        tilt:
            -1.0 = down
             0.0 = no tilt
             1.0 = up

        zoom:
            -1.0 = zoom out
             0.0 = no zoom
             1.0 = zoom in
        """

        pan = self._clamp(pan)
        tilt = self._clamp(tilt)
        zoom = self._clamp(zoom)

        self.ptz.ContinuousMove(
            ProfileToken=self.profile.token,
            Velocity={
                "PanTilt": {
                    "x": pan,
                    "y": tilt
                },
                "Zoom": {
                    "x": zoom
                }
            }
        )

    def pan_left(self, speed=0.5):
        self.move(pan=-self._clamp(speed))

    def pan_right(self, speed=0.5):
        self.move(pan=self._clamp(speed))

    def tilt_up(self, speed=0.5):
        self.move(tilt=self._clamp(speed))

    def tilt_down(self, speed=0.5):
        self.move(tilt=-self._clamp(speed))

    def zoom_in(self, speed=0.5):
        self.move(zoom=self._clamp(speed))

    def zoom_out(self, speed=0.5):
        self.move(zoom=-self._clamp(speed))

    def stop(self, pan_tilt=True, zoom=True):
        """Stop PTZ movement."""

        self.ptz.Stop(
            ProfileToken=self.profile.token,
            PanTilt=pan_tilt,
            Zoom=zoom
        )