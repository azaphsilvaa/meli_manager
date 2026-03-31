import math
import os
import struct
import wave


SOUNDS_DIR = os.path.join("assets", "sounds")


def _write_wave(file_path: str, samples: list[int], sample_rate: int = 44100):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with wave.open(file_path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for sample in samples:
            wav_file.writeframes(struct.pack("<h", sample))


def generate_tone(
    frequency: float,
    duration_seconds: float,
    volume: float = 0.35,
    sample_rate: int = 44100,
) -> list[int]:
    total_samples = int(sample_rate * duration_seconds)
    amplitude = int(32767 * max(0.0, min(volume, 1.0)))

    samples = []

    for i in range(total_samples):
        t = i / sample_rate
        sample = int(amplitude * math.sin(2 * math.pi * frequency * t))
        samples.append(sample)

    return samples


def generate_silence(
    duration_seconds: float,
    sample_rate: int = 44100,
) -> list[int]:
    total_samples = int(sample_rate * duration_seconds)
    return [0] * total_samples


def save_sound(file_name: str, samples: list[int]):
    output_file = os.path.join(SOUNDS_DIR, file_name)
    _write_wave(output_file, samples)
    print(f"✅ Som gerado: {output_file}")


def generate_click_sound():
    samples = []
    samples += generate_tone(920.0, 0.045, 0.22)
    samples += generate_silence(0.01)
    samples += generate_tone(1180.0, 0.035, 0.18)

    save_sound("click.wav", samples)


def generate_loading_sound():
    samples = []
    samples += generate_tone(420.0, 0.10, 0.08)
    samples += generate_silence(0.04)
    samples += generate_tone(520.0, 0.10, 0.08)
    samples += generate_silence(0.06)

    save_sound("loading.wav", samples)


def generate_success_sound():
    samples = []
    samples += generate_tone(740.0, 0.07, 0.20)
    samples += generate_silence(0.02)
    samples += generate_tone(980.0, 0.10, 0.22)

    save_sound("success.wav", samples)


def generate_error_sound():
    samples = []
    samples += generate_tone(320.0, 0.12, 0.20)
    samples += generate_silence(0.03)
    samples += generate_tone(250.0, 0.12, 0.20)

    save_sound("error.wav", samples)


def generate_notification_sound():
    samples = []
    samples += generate_tone(660.0, 0.06, 0.18)
    samples += generate_silence(0.03)
    samples += generate_tone(880.0, 0.08, 0.18)

    save_sound("notification.wav", samples)


def main():
    os.makedirs(SOUNDS_DIR, exist_ok=True)

    generate_click_sound()
    generate_loading_sound()
    generate_success_sound()
    generate_error_sound()
    generate_notification_sound()

    print("✅ Sons padrão gerados com sucesso.")


if __name__ == "__main__":
    main()