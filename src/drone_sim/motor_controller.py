#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
import math


class DroneMotorController(Node):
    """
    4 motorlu drone için motor kontrolcüsü
    Teleop komutlarını motorlara dönüştürür
    """
    
    def __init__(self):
        super().__init__('motor_controller')
        
        # Motor PWM yayıncıları
        self.motor_pubs = [
            self.create_publisher(Float64, f'/drone/motor_{i}_cmd', 10)
            for i in range(1, 5)
        ]
        
        # Teleop komutu abone ol
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Motor hızları (PWM 0-1 arası)
        self.motor_speeds = [0.0, 0.0, 0.0, 0.0]
        
        self.get_logger().info('Motor Controller başlatıldı')
    
    def cmd_vel_callback(self, msg: Twist):
        """
        Geometry_msgs/Twist mesajından motor komutlarını hesapla
        
        linear.z  -> Yükseklik (hover/climb)
        angular.z -> Yaw (dönüş)
        linear.x  -> Pitch (ileri/geri)
        linear.y  -> Roll (sağa/sola)
        """
        
        # Temel hover throttle (tüm motorlar eşit)
        hover_throttle = 0.5  # Dronun havada kalması için
        
        # Komutlardan motor delta değerleri hesapla
        yaw_cmd = msg.angular.z * 0.1
        pitch_cmd = msg.linear.x * 0.2
        roll_cmd = msg.linear.y * 0.2
        throttle_cmd = msg.linear.z * 0.1
        
        # Dört motorun hızı hesapla (X konfigürasyonu)
        # Motor 1: Ön Sol
        self.motor_speeds[0] = hover_throttle + throttle_cmd + pitch_cmd + roll_cmd + yaw_cmd
        
        # Motor 2: Ön Sağ
        self.motor_speeds[1] = hover_throttle + throttle_cmd + pitch_cmd - roll_cmd - yaw_cmd
        
        # Motor 3: Arka Sol
        self.motor_speeds[2] = hover_throttle + throttle_cmd - pitch_cmd + roll_cmd - yaw_cmd
        
        # Motor 4: Arka Sağ
        self.motor_speeds[3] = hover_throttle + throttle_cmd - pitch_cmd - roll_cmd + yaw_cmd
        
        # Hızları 0-1 arasında sınırla
        self.motor_speeds = [max(0.0, min(1.0, speed)) for speed in self.motor_speeds]
        
        # Motor komutlarını yayınla
        for i, pub in enumerate(self.motor_pubs):
            msg_out = Float64()
            msg_out.data = self.motor_speeds[i]
            pub.publish(msg_out)
        
        self.get_logger().debug(f'Motor hızları: {self.motor_speeds}')


def main(args=None):
    rclpy.init(args=args)
    
    controller = DroneMotorController()
    rclpy.spin(controller)
    
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
