
class TextToSpeech_:
    # Set your Deepgram API Key and desired voice model
    DG_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    MODEL_NAME = "aura-helios-en"  # Example model name, change as needed
#    MODEL_NAME = "nova-2"#"aura-helios-en"  # Example model name, change as needed

    @staticmethod
    def is_installed(lib_name: str) -> bool:
        lib = shutil.which(lib_name)
        return lib is not None

   
    def speak(self, text):
        if not self.is_installed("ffplay"):
            raise ValueError("ffplay not found, necessary to stream audio.")

        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={self.MODEL_NAME}&performance=true&encoding=linear16&sample_rate=24000"
        headers = {
            "Authorization": f"Token {self.DG_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }

        try:
            response = requests.post(DEEPGRAM_URL, stream=True, headers=headers, json=payload)
            response.raise_for_status()  # Проверка на наличие HTTP ошибок

            player_command = ["ffplay", "-autoexit", "-", "-nodisp"]
            player_process = subprocess.Popen(
                player_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,  # Изменено для получения ошибок
            )

            start_time = time.time()
            first_byte_time = None

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                        ttfb = int((first_byte_time - start_time) * 1000)
                        print(f"TTS Time to First Byte (TTFB): {ttfb}ms\n")
                    player_process.stdin.write(chunk)
                    player_process.stdin.flush()

            if player_process.stdin:
                player_process.stdin.close()
            player_process.wait()

            # Проверка на ошибки ffplay
            stderr = player_process.stderr.read().decode()
            if stderr:
                print(f"ffplay ошибки: {stderr}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP ошибка: {http_err} - {response.text}")
        except Exception as e:
            print(f"Произошла ошибка при синтезе речи: {e}")

            