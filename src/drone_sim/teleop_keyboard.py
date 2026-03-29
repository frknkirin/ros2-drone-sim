#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty


class TeleopKeyboard(Node):
    """Klavye ile drone kontrolü"""
    
    def __init__(self):
        super().__init__('teleop_keyboard')
        
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info('Teleop Keyboard başlatıldı')
        self.get_logger().info('''
        Kontrol tuşları:
        W/A/S/D - İleri/Sola/Geri/Sağa
        Space   - Yüksekçe çık
        Ctrl    - Alçal
        Q/E     - Saat yönü/Ters dön
        X       - Durdur
        ''')
        
        self.twist = Twist()
        self.get_settings = termios.tcgetattr(sys.stdin)
        
        try:
            tty.setraw(sys.stdin.fileno())
            self.read_keyboard()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.get_settings)
    
    def read_keyboard(self):
        """Klavye girişini oku"""
        while rclpy.ok():
            ch = sys.stdin.read(1)
            
            if ch == 'w':
                self.twist.linear.x = 0.5
            elif ch == 's':
                self.twist.linear.x = -0.5
            elif ch == 'a':
                self.twist.linear.y = 0.5
            elif ch == 'd':
                self.twist.linear.y = -0.5
            elif ch == ' ':
                self.twist.linear.z = 0.5
            elif ch == '\x03':  # Ctrl+C
                self.twist.linear.z = -0.5
            elif ch == 'q':
                self.twist.angular.z = 0.5
            elif ch == 'e':
                self.twist.angular.z = -0.5
            elif ch == 'x':
                self.twist = Twist()
            
            self.pub.publish(self.twist)


def main(args=None):
    rclpy.init(args=args)
    teleop = TeleopKeyboard()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
