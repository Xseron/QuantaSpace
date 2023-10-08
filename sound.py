import pygame
import numpy as np
import time

pygame.mixer.init(channels=2)

def data_to_sound_properties(data):
    max_values = {
        'mass': 1000,
        'radius': 10000,
        'distance': 100000,
        'gravitation': 100,
        'magnetism': 1000
    }
    
    frequency = np.interp(data['mass'], [0, max_values['mass']], [440, 130])
    duration = np.interp(data['radius'], [0, max_values['radius']], [1, 5])
    volume = np.interp(data['distance'], [0, max_values['distance']], [1, 0.1])
    
    return frequency, duration, volume

def generate_sound(frequency, duration, volume):
    sample_rate = 44100
    t = np.arange(int(sample_rate * duration)) / sample_rate
    wave = 32767 * np.sin(2 * np.pi * frequency * t)
    #A sine wave is generated using the formulated frequency.
    # 32767 is the maximum positive value for 16-bit signed integers, ensuring the highest possible amplitude without distortion.
    # 2 * np.pi * frequency * t determines the wave's frequency, dictating how many cycles the wave completes per second.
    
    stereo_wave = np.array([volume * wave, volume * wave], dtype=np.int16).T
    sound = pygame.sndarray.make_sound(np.ascontiguousarray(stereo_wave))
    return sound


def play_sound(sound):
    sound.play()
    while pygame.mixer.get_busy():
        time.sleep(0.1)
    sound.stop()

user_data = {
    "mass": float(input("Enter mass (10^24 kg): ")),
    "radius": float(input("Enter radius (10^3 km): ")),
    "distance": float(input("Enter distance from sun (10^6 km): ")),
}

freq, dur, vol = data_to_sound_properties(user_data)

sound = generate_sound(freq, dur, vol)
play_sound(sound)