import torch
import time
import os
import shutil

device = torch.device(os.environ.get("TORCH_DEVICE", "cpu"))
local_file = "model.pt"

def load_model():
    torch.set_num_threads(8)

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(f"https://models.silero.ai/models/tts/en/v3_en.pt", local_file)

def tts(message, language="en", model="v3_en", speaker="en_44", file_name="test"):
    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    sample_rate = 48_000

    audio_paths = model.save_wav(
        text=message,
        speaker=speaker,
        put_accent=True,
        put_yo=True,
        sample_rate=sample_rate
    )

    # Rename or move the file to the custom file name
    if os.path.exists(audio_paths):
        shutil.move(audio_paths, file_name)
        print(f"Audio saved as: {file_name}")

    return file_name


load_model()

for i in range(44, 100):
    if i % 2 != 0:
        continue

    speaker = f"en_{i}"
    tts("Hello, World!", speaker=speaker, file_name=f"{speaker}_{int(time.time())}.wav")