import dbus
import time
import dbus.mainloop.glib
from gi.repository import GLib
import RPi.GPIO as GPIO

'''
--------------------------------------------
------------ SONG DATA FETCHING ------------
--------------------------------------------
'''
# Function to get the media player path dinamically
def get_bluetooth_player_path():
    try:
        # Connect to the system D-Bus
        bus = dbus.SystemBus()
        
        # Access the object manager to get all Bluetooth devices
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        # Iterate over all objects and find a media player
        for path, interfaces in objects.items():
            # Check if this path has a MediaPlayer1 interface
            if "org.bluez.MediaPlayer1" in interfaces:
                print(f"Found media player at path: {path}")
                return path

        print("No media player found.")
        return None
    except Exception as e:
        print(f"Error discovering media player: {e}")
        return None

# Function to read metadata from player_path
def get_bluetooth_metadata(player_path):
    try:
        # Connect to the player object via dbus
        bus = dbus.SystemBus()
        player = bus.get_object("org.bluez", player_path)
        iface = dbus.Interface(player, "org.freedesktop.DBus.Properties")
        
        # Fetch metadata
        metadata = iface.Get("org.bluez.MediaPlayer1", "Track")
        
        # Extract details
        title = metadata.get("Title", "Unknown Title")
        artist = metadata.get("Artist", "Unknown Artist")
        album = metadata.get("Album", "Unknown Album")
        return title, artist, album
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return None, None, None


# Function to get the current playback status (Playing, Paused, etc.)
def get_playback_status(player_path):
    try:
        bus = dbus.SystemBus()
        player = bus.get_object("org.bluez", player_path)
        iface = dbus.Interface(player, "org.freedesktop.DBus.Properties")

        # Get the current playback status
        status = iface.Get("org.bluez.MediaPlayer1", "Status")
        return status
    except Exception as e:
        print(f"Error getting playback status: {e}")
        return None


# Function to handle property changes from the Bluetooth media player
def properties_changed(interface, changed, invalidated, path=None):
    # Check if the changed properties include the 'Track' property
    #print("Properties changed")
    if 'Track' in changed:
        metadata = changed['Track']
        
        # Extract and print song details
        title = metadata.get('Title', 'Unknown Title')
        artist = metadata.get('Artist', 'Unknown Artist')
        album = metadata.get('Album', 'Unknown Album')

        print(f"Now playing: Title: {title}, Artist: {artist}, Album: {album}\n")
'''
---------- SONG DATA FETCHING END ----------
'''  



'''
--------------------------------------------
------------- BUTTONS HANDLING -------------
--------------------------------------------
'''
SKIP_PIN = 17
BACK_PIN = 5
PLAY_PAUSE_PIN = 6

# Function to send media control commands
def send_media_command(command):
    try:
        bus = dbus.SystemBus()
        player_path = get_bluetooth_player_path()
        if not player_path:
            print("No media player available.")
            return

        player = bus.get_object("org.bluez", player_path)
        media_interface = dbus.Interface(player, "org.bluez.MediaPlayer1")
        
        if command == "playpause":
            # Toggle Play/Pause based on current playback status
            status = get_playback_status(player_path)
            if status == "playing":
                media_interface.Pause()
            else:
                media_interface.Play()
        elif command == "next":
            media_interface.Next()
        elif command == "previous":
            media_interface.Previous()

    except Exception as e:
        print(f"Error sending media command: {e}")

# GPIO button press handlers
def skip_button_pressed(channel):
    print("Skip button pressed")
    send_media_command("next")

def back_button_pressed(channel):
    print("Back button pressed")
    send_media_command("previous")

def play_pause_button_pressed(channel):
    print("Play/Pause button pressed")
    send_media_command("playpause")

def setup_gpio():
    try:
        #GPIO.cleanup()  # Ensure GPIO is in a clean state
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SKIP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BACK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PLAY_PAUSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print("GPIO setup complete")

        # Detect button presses
        GPIO.add_event_detect(SKIP_PIN, GPIO.FALLING, callback=skip_button_pressed, bouncetime=300)
        GPIO.add_event_detect(BACK_PIN, GPIO.FALLING, callback=back_button_pressed, bouncetime=300)
        GPIO.add_event_detect(PLAY_PAUSE_PIN, GPIO.FALLING, callback=play_pause_button_pressed, bouncetime=300)
        print("Edge detection added for buttons")
    
    except RuntimeError as e:
        print(f"Error setting up GPIO: {e}")
'''
----------- BUTTONS HANDLING END -----------
'''





def main():
    # Initialize the main loop for D-Bus signal handling
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Set up GPIO Buttons
    setup_gpio()

    # Get media player path
    player_path = get_bluetooth_player_path()
    if not player_path:
        print("No media player available. Exiting...")
        return
    
    try:
        # Connect to player via dbus
        bus = dbus.SystemBus()
        player = bus.get_object("org.bluez", player_path)
        
        # Subscribe to the 'PropertiesChanged' signal from the MediaPlayer1 interface
        bus.add_signal_receiver(
            handler_function=properties_changed,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            path=player_path,
            arg0="org.bluez.MediaPlayer1"
        )

        print("Listening for track changes...")
        # Start the GLib event loop to listen for D-Bus signals
        loop = GLib.MainLoop()
        loop.run()

    except Exception as e:
        print(f"Error setting up signal listener: {e}")
    
    finally:
        GPIO.cleanup()  # Clean up GPIO on exit


if __name__ == "__main__":
    main()
