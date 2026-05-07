import os
import wave
from pathlib import Path

from google import genai
from google.genai import types


def load_env_file(path: Path) -> None:
    """Tiny .env loader (no extra dependency). KEY=VALUE per line."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


SCRIPT_DIR = Path(__file__).resolve().parent
load_env_file(SCRIPT_DIR / ".env")

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit(
        "GEMINI_API_KEY 가 설정되어 있지 않습니다. "
        f"{SCRIPT_DIR / '.env'} 파일에 GEMINI_API_KEY=... 형태로 추가하세요."
    )

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents="안녕하세요, 테스트 음성입니다.",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
            )
        ),
    ),
)

if not response.candidates or not response.candidates[0].content.parts:
    raise RuntimeError("응답에 오디오 데이터가 없습니다.")

audio = response.candidates[0].content.parts[0].inline_data.data
output_path = SCRIPT_DIR / "output.wav"
with wave.open(str(output_path), "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(audio)

print(f"{output_path} 생성 완료 ({len(audio)} bytes)")
