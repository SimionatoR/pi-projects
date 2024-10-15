import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# Function to handle property changes from the Bluetooth media player
def properties_changed(interface, changed, invalidated, path):
    # Check if the changed properties include the 'Track' property
    if 'Track' in changed:
        metadata = changed['Track']
        
        # Extract and print song details
        title = metadata.get('Title', 'Unknown Title')
        artist = metadata.get('Artist', 'Unknown Artist')
        album = metadata.get('Album', 'Unknown Album')

        print(f"Now playing: Title: {title}, Artist: {artist}, Album: {album}")

# Function to get the media player path dynamically
def get_bluetooth_player_path():
    try:
        # Connect to the system D-Bus
        bus = dbus.SystemBus()
        
        # Access the object manager to get all Bluetooth devices
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        # Iterate over all objects and find a media player
        for path, interfaces in objects.items():
            if "org.bluez.MediaPlayer1" in interfaces:
                print(f"Found media player at path: {path}")
                return path

        print("No media player found.")
        return None
    except Exception as e:
        print(f"Error discovering media player: {e}")
        return None

def main():
    # Initialize the main loop for D-Bus signal handling
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Get the media player path
    player_path = get_bluetooth_player_path()
    
    if not player_path:
        print("No media player available. Exiting...")
        return

    try:
        # Connect to the player object via dbus
        bus = dbus.SystemBus()
        player = bus.get_object("org.bluez", player_path)

        # Subscribe to the 'PropertiesChanged' signal from the MediaPlayer1 interface
        bus.add_signal_receiver(
            handler_function=properties_changed,
            signal_name="PropertiesChanged",
            dbus_interface="org.freedesktop.DBus.Properties",
            path=player_path
        )

        print("Listening for track changes...")
        # Start the GLib event loop to listen for D-Bus signals
        loop = GLib.MainLoop()
        loop.run()

    except Exception as e:
        print(f"Error setting up signal listener: {e}")

if __name__ == "__main__":
    main()
