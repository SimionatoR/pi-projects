import dbus
import time

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

def main():
    player_path = get_bluetooth_player_path()
    
    if not player_path:
        print("No media player available. Exiting...")
        return
    
    while True:
        title, artist, album = get_bluetooth_metadata(player_path)
        if title and artist and album:
            print(f"Title: {title}, Artist: {artist}, Album: {album}")
        else:
            print("No metadata available.")
        time.sleep(5)  # Poll every 5 seconds

if __name__ == "__main__":
    main()
