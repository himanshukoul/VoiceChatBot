import whisper
import pyaudio
import wave
import threading
import time
import os
import queue
import sys
from datetime import datetime

# Cross-platform keyboard input
import os
if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty
    import select

class RealTimeTranscriber:
    def __init__(self, model_size="base", chunk_duration=2, show_numbers=True):
        print(f"Loading Whisper model: {model_size}...")
        self.model = whisper.load_model(model_size)
        print(" Model loaded successfully!")

        self.chunk_duration = chunk_duration
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000

        self.is_running = False
        self.audio_queue = queue.Queue()
        self.audio = pyaudio.PyAudio()

        self.chunk_counter = 0
        self.word_counter = 0
        self.current_line_length = 0
        self.max_line_length = 70
        self.show_numbers = show_numbers

    def setup_keyboard_input(self):
        """Setup non-blocking keyboard input"""
        if os.name != 'nt':
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())

    def restore_keyboard_input(self):
        """Restore normal keyboard input"""
        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def check_for_keypress(self):
        """Check for keypress in a non-blocking way"""
        if os.name == 'nt':
            return msvcrt.kbhit()
        else:
            return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def record_continuously(self):
        """Continuously record audio in chunks"""
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        try:
            while self.is_running:
                frames = []
                for _ in range(0, int(self.rate / self.chunk_size * self.chunk_duration)):
                    if not self.is_running:
                        break
                    try:
                        data = stream.read(self.chunk_size, exception_on_overflow=False)
                        frames.append(data)
                    except Exception as e:
                        print(f"\n Audio read error: {e}")
                        continue

                if frames and self.is_running:
                    self.chunk_counter += 1
                    filename = f"temp_chunk_{self.chunk_counter}.wav"

                    try:
                        wf = wave.open(filename, 'wb')
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio.get_sample_size(self.format))
                        wf.setframerate(self.rate)
                        wf.writeframes(b''.join(frames))
                        wf.close()

                        self.audio_queue.put(filename)
                    except Exception as e:
                        print(f"\n Audio save error: {e}")

        except Exception as e:
            print(f"\n Recording error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def transcribe_continuously(self):
        """Continuously transcribe audio chunks"""
        while self.is_running:
            try:
                filename = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                result = self.model.transcribe(filename, fp16=False)
                text = result["text"].strip()
                if text:
                    words = text.split()
                    for word in words:
                        self.display_word(word)
            except Exception as e:
                pass

            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass

            self.audio_queue.task_done()

    def display_word_with_numbers(self, word):
        self.word_counter += 1
        word_with_number = f"{self.word_counter}.{word} "

        if self.current_line_length + len(word_with_number) > self.max_line_length:
            print()
            self.current_line_length = 0

        print(word_with_number, end='', flush=True)
        self.current_line_length += len(word_with_number)

        if self.word_counter % 10 == 0:
            print()
            self.current_line_length = 0

    def display_word_without_numbers(self, word):
        if word and word.strip():
            print(word.strip() + " ", end='', flush=True)

    def display_word(self, word):
        if self.show_numbers:
            self.display_word_with_numbers(word)
        else:
            self.display_word_without_numbers(word)

    def start_streaming(self):
        print("  Real-time Speech-to-Text Streaming")
        print("=" * 60)
        print(" Starting to listen...")
        print(" Words will appear below as you speak")
        print("  Press ANY KEY to stop")
        print("=" * 60)
        print()

        self.setup_keyboard_input()
        self.is_running = True

        recording_thread = threading.Thread(target=self.record_continuously)
        recording_thread.daemon = True
        recording_thread.start()

        transcription_thread = threading.Thread(target=self.transcribe_continuously)
        transcription_thread.daemon = True
        transcription_thread.start()

        try:
            while self.is_running:
                if self.check_for_keypress():
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_streaming()

    def stop_streaming(self):
        print(f"\n\n Stopping transcription...")
        print(f" Total words transcribed: {self.word_counter}")

        self.is_running = False

        self.restore_keyboard_input()
        time.sleep(1)

        remaining_files = 0
        while not self.audio_queue.empty():
            try:
                filename = self.audio_queue.get_nowait()
                if os.path.exists(filename):
                    os.remove(filename)
                remaining_files += 1
            except:
                break

        for i in range(1, self.chunk_counter + 1):
            temp_file = f"temp_chunk_{i}.wav"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    remaining_files += 1
                except:
                    pass

        if remaining_files > 0:
            print(f"Cleaned up {remaining_files} temporary files")

        try:
            self.audio.terminate()
        except:
            pass

        print(" Transcription stopped successfully!")

def main():
    print("🗿" * 60)
    print("Display format options:")
    print("  1. With word numbers (1.Hello 2.world 3.this)")
    print("  2. Without numbers (Hello world this is natural text)")

    format_choice = input("\nChoose display format (1-2, default=1): ").strip()
    show_numbers = format_choice != "2"

    models = {
        "1": ("tiny", "Fastest, least accurate"),
        "2": ("base", "Good balance - recommended"),
        "3": ("small", "Better accuracy, slower"),
        "4": ("medium", "High accuracy, much slower"),
        "5": ("large", "Best accuracy, very slow")
    }

    print("\nModel options:")
    for key, (model, desc) in models.items():
        print(f"  {key}. {model} - {desc}")

    model_choice = input("\nChoose model (1-5, default=2): ").strip()
    model_size = models.get(model_choice, ("base", ""))[0]

    print(f"\nResponse time options:")
    print("  1. Ultra-fast  - very responsive")
    print("  2. Fast  - recommended for real-time")
    print("  3. Balanced  - good accuracy vs speed")
    print("  4. Slower - better for complex speech")

    duration_choice = input("Choose response time (1-4, default=2): ").strip()
    duration_map = {"1": 1, "2": 2, "3": 3, "4": 5}
    chunk_duration = duration_map.get(duration_choice, 2)

    display_type = "with numbers" if show_numbers else "without numbers"
    print(f"\nConfiguration: {model_size} model, {chunk_duration}s chunks, {display_type}")
    print("  Make sure your microphone is working and not muted!")

    input("\nPress Enter to start streaming transcription...")

    try:
        transcriber = RealTimeTranscriber(
            model_size=model_size,
            chunk_duration=chunk_duration,
            show_numbers=show_numbers
        )
        transcriber.start_streaming()

    except KeyboardInterrupt:
        print("\n Interrupted")
    except Exception as e:
        print(f"\n Error: {e}")

if __name__ == "__main__":
    main()
