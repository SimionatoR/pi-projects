import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

# Define the size of the LCD (16x2 or 20x4)
lcd_columns = 16
lcd_rows = 2

# Define the Raspberry Pi GPIO pins connected to the LCD
lcd_rs = digitalio.DigitalInOut(board.D26)  # Register Select (RS)
lcd_en = digitalio.DigitalInOut(board.D19)  # Enable (E)
lcd_d4 = digitalio.DigitalInOut(board.D13)  # Data pin 4 (D4)
lcd_d5 = digitalio.DigitalInOut(board.D6)   # Data pin 5 (D5)
lcd_d6 = digitalio.DigitalInOut(board.D5)   # Data pin 6 (D6)
lcd_d7 = digitalio.DigitalInOut(board.D11)  # Data pin 7 (D7)

# Initialize the LCD in 4-bit mode
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
lcd.clear()

# Function to display song info on the LCD
def display_song_info_on_lcd(title, artist):
    lcd.clear()  # Clear the LCD screen
    lcd.message = f"{title[:lcd_columns]}\n{artist[:lcd_columns]}"  # Truncate if necessary

def display_show_message(message):
    try:
        print(f"Message: {message}")
        lcd.clear()
        if isinstance(message, str):
            lcd.message = f"{message[:lcd_columns]}"
    except Exception as e:
        print(f"Error displaying message: {e}")