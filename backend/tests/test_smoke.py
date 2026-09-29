"""冒烟测试：只覆盖顺利路径，用来确认系统能启动、核心接口能跑通。

这些用例在带缺陷的快照上应当全部通过 —— 它们不涉及边界与失败路径。
缺陷需要靠 README「行为规格」逐条推导后自行补测。
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class FakeAudioProcessor:
    """替身：声明可用，并返回一段形状固定的分析结果。"""

    available = True

    def process_audio_file(self, audio_path):
        return {
            "spectrogram": {
                "spectrogram": [[0.0, -1.0]],
                "times": [0.0],
                "frequencies": [100.0],
                "sample_rate": 22050,
            },
            "animal_analysis": {
                "num_calls": 2,
                "calls": [],
                "mfcc_mean": [0.0],
                "spectral_centroid_mean": 100.0,
                "zero_crossing_rate_mean": 0.01,
                "total_call_duration": 1.5,
            },
            "pump_analysis": {
                "pump_energy_ratio": 0.2,
                "rms_mean": 0.01,
                "rms_std": 0.0,
                "dominant_pump_frequency": 90.0,
            },
            "separated_audio_paths": {"animal": "a.wav", "pump": "p.wav"},
            "duration": 3.0,
        }


class FakeTranscriber:
    available = True

    def process_meeting_audio(self, audio_path, language="zh"):
        return {
            "full_text": "海豚食欲下降。",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "海豚食欲下降。", "speaker": "SPEAKER_00", "words": []}
            ],
            "speakers": ["SPEAKER_00"],
            "speaker_statistics": {
                "SPEAKER_00": {"total_speaking_time": 2.0, "num_segments": 1, "segments": []}
            },
            "formatted_transcript": "**SPEAKER_00**: 海豚食欲下降。",
            "language": language,
            "duration": 2.0,
        }


class FakeEmailSender:
    configured = True

    def send_full_report(self, report_content, meeting_summary):
        return {"care_team": True, "education_department": True}


@pytest.fixture()
def app_module(monkeypatch):
    import main

    monkeypatch.setattr(main, "audio_processor", FakeAudioProcessor())
    monkeypatch.setattr(main, "meeting_transcriber", FakeTranscriber())
    monkeypatch.setattr(main, "email_sender", FakeEmailSender())
    return main


@pytest.fixture()
def client(app_module):
    with TestClient(app_module.app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_root_and_jobs(client):
    assert client.get("/").status_code == 200
    jobs = client.get("/api/jobs")
    assert jobs.status_code == 200
    assert isinstance(jobs.json()["jobs"], list)


def test_upload_audio_happy_path(client, app_module):
    resp = client.post(
        "/api/audio/upload",
        files={"file": ("tank_clip.wav", b"RIFF....WAVEfmt ", "audio/wav")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["original_name"] == "tank_clip.wav"
    assert body["filename"].endswith(".wav")
    assert body["file_size"] == len(b"RIFF....WAVEfmt ")
    assert os.path.exists(os.path.join(app_module.UPLOAD_DIR, body["filename"]))


def test_process_audio_happy_path(client):
    resp = client.post(
        "/api/audio/process",
        files={"file": ("tank_clip.wav", b"RIFF....WAVEfmt ", "audio/wav")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["duration"] == 3.0
    assert body["animal_analysis"]["num_calls"] == 2
    assert body["pump_analysis"]["pump_energy_ratio"] == 0.2
    assert body["output_file"].endswith(".json")
    assert body["spectrogram_data"]["sample_rate"] == 22050


def test_meeting_process_and_report_files(client, app_module):
    resp = client.post(
        "/api/meeting/process",
        files={"meeting_audio": ("meeting.wav", b"RIFF....WAVEfmt ", "audio/wav")},
        data={"animal_type": "海洋哺乳动物", "language": "zh", "send_email": "true"},
    )
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]

    status = client.get("/api/status/" + job_id).json()
    assert status["status"] == "completed"
    result = status["result"]
    assert result["report_file"].endswith(".md")
    assert result["transcript_file"].endswith(".json")
    assert result["report"]["full_markdown"]
    assert os.path.exists(os.path.join(app_module.OUTPUT_DIR, result["report_file"]))
    assert os.path.exists(os.path.join(app_module.OUTPUT_DIR, result["transcript_file"]))


def test_outputs_and_download_roundtrip(client, app_module):
    os.makedirs(app_module.OUTPUT_DIR, exist_ok=True)
    name = "smoke_report_sample.md"
    with open(os.path.join(app_module.OUTPUT_DIR, name), "w", encoding="utf-8") as fh:
        fh.write("# 冒烟样例\n")

    listing = client.get("/api/outputs")
    assert listing.status_code == 200
    names = [item["filename"] for item in listing.json()["files"]]
    assert name in names

    download = client.get("/api/download/" + name)
    assert download.status_code == 200
    assert "冒烟样例" in download.text
