"""
Fire TV Bluetooth Remote for Android
Requires: kivy, pyjnius, plyer
Install: pip install kivy pyjnius plyer
Build: buildozer (see buildozer.spec)
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from jnius import autoclass, cast
from plyer import notification
import time

# Android Bluetooth classes
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
UUID = autoclass('java.util.UUID')

# HID keycodes for Fire TV
KEYCODE_DPAD_UP = 19
KEYCODE_DPAD_DOWN = 20
KEYCODE_DPAD_LEFT = 21
KEYCODE_DPAD_RIGHT = 22
KEYCODE_DPAD_CENTER = 23  # OK/Select
KEYCODE_BACK = 4
KEYCODE_HOME = 3
KEYCODE_MENU = 82
KEYCODE_MEDIA_PLAY_PAUSE = 85
KEYCODE_MEDIA_REWIND = 89
KEYCODE_MEDIA_FAST_FORWARD = 90


class BTController:
    """Handle Bluetooth HID connection to Fire TV"""
    
    def __init__(self):
        self.adapter = BluetoothAdapter.getDefaultAdapter()
        self.socket = None
        self.device = None
        # Standard HID UUID
        self.HID_UUID = UUID.fromString("00001124-0000-1000-8000-00805f9b34fb")
        
    def scan_devices(self):
        """Return list of paired devices"""
        if not self.adapter:
            return []
        bonded = self.adapter.getBondedDevices().toArray()
        devices = []
        for device in bonded:
            name = device.getName()
            addr = device.getAddress()
            if 'Fire TV' in name or 'AFTM' in name or 'AFT' in name:
                devices.append((name, addr))
        return devices
    
    def connect(self, address):
        """Connect to Fire TV device"""
        try:
            self.device = self.adapter.getRemoteDevice(address)
            self.socket = self.device.createRfcommSocketToServiceRecord(self.HID_UUID)
            self.socket.connect()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def send_keycode(self, keycode):
        """Send Android keycode to Fire TV"""
        if not self.socket or not self.socket.isConnected():
            return False
        
        try:
            # Build HID report for keycode
            # Format: [modifier, reserved, keycode1-6]
            report = bytearray([0, 0, keycode, 0, 0, 0, 0, 0])
            self.socket.getOutputStream().write(report)
            time.sleep(0.05)
            # Release key
            release = bytearray([0, 0, 0, 0, 0, 0, 0, 0])
            self.socket.getOutputStream().write(release)
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            return False


class FireTVRemoteApp(App):
    """Main Kivy app for Fire TV remote"""
    
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.bt = BTController()
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Status label
        self.status_label = Label(
            text='Not Connected',
            size_hint=(1, 0.1),
            color=(1, 0.3, 0.3, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Connect button
        connect_btn = Button(
            text='Connect to Fire TV',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 1, 1)
        )
        connect_btn.bind(on_press=self.connect_device)
        main_layout.add_widget(connect_btn)
        
        # Control buttons layout
        controls = BoxLayout(orientation='vertical', spacing=5)
        
        # Top row: Home, Back, Menu
        top_row = BoxLayout(size_hint=(1, 0.15))
        top_row.add_widget(self.make_button('HOME', KEYCODE_HOME))
        top_row.add_widget(self.make_button('BACK', KEYCODE_BACK))
        top_row.add_widget(self.make_button('MENU', KEYCODE_MENU))
        controls.add_widget(top_row)
        
        # D-pad navigation - using text instead of unicode arrows
        dpad = GridLayout(cols=3, size_hint=(1, 0.4), spacing=5)
        dpad.add_widget(Label())  # Empty
        dpad.add_widget(self.make_button('UP', KEYCODE_DPAD_UP))
        dpad.add_widget(Label())  # Empty
        dpad.add_widget(self.make_button('LEFT', KEYCODE_DPAD_LEFT))
        dpad.add_widget(self.make_button('OK', KEYCODE_DPAD_CENTER, 
                                         color=(1, 0.8, 0, 1)))
        dpad.add_widget(self.make_button('RIGHT', KEYCODE_DPAD_RIGHT))
        dpad.add_widget(Label())  # Empty
        dpad.add_widget(self.make_button('DOWN', KEYCODE_DPAD_DOWN))
        dpad.add_widget(Label())  # Empty
        controls.add_widget(dpad)
        
        # Media controls - using text
        media_row = BoxLayout(size_hint=(1, 0.15))
        media_row.add_widget(self.make_button('<<', KEYCODE_MEDIA_REWIND))
        media_row.add_widget(self.make_button('PLAY', KEYCODE_MEDIA_PLAY_PAUSE))
        media_row.add_widget(self.make_button('>>', KEYCODE_MEDIA_FAST_FORWARD))
        controls.add_widget(media_row)
        
        main_layout.add_widget(controls)
        
        return main_layout
    
    def make_button(self, text, keycode, color=(0.3, 0.3, 0.3, 1)):
        """Create a control button"""
        btn = Button(
            text=text,
            background_color=color,
            font_size='18sp',
            bold=True
        )
        btn.bind(on_press=lambda x: self.send_key(keycode))
        return btn
    
    def connect_device(self, instance):
        """Connect to first available Fire TV"""
        devices = self.bt.scan_devices()
        
        if not devices:
            self.status_label.text = 'No Fire TV found. Pair device first.'
            self.status_label.color = (1, 0.3, 0.3, 1)
            return
        
        # Try first device
        name, addr = devices[0]
        self.status_label.text = f'Connecting to {name}...'
        
        if self.bt.connect(addr):
            self.status_label.text = f'Connected: {name}'
            self.status_label.color = (0.3, 1, 0.3, 1)
            notification.notify(
                title='Fire TV Remote',
                message=f'Connected to {name}'
            )
        else:
            self.status_label.text = 'Connection failed'
            self.status_label.color = (1, 0.3, 0.3, 1)
    
    def send_key(self, keycode):
        """Send keycode to Fire TV"""
        if self.bt.send_keycode(keycode):
            print(f"Sent keycode: {keycode}")
        else:
            self.status_label.text = 'Not connected!'
            self.status_label.color = (1, 0.3, 0.3, 1)
    
    def on_stop(self):
        """Cleanup on app close"""
        self.bt.disconnect()


if __name__ == '__main__':
    FireTVRemoteApp().run()
