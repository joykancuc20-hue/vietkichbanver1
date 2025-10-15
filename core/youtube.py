import os, tempfile, subprocess

def get_transcript(url: str, lang: str = "vi"):
    """Lấy phụ đề tự động (auto subtitles) bằng yt-dlp nếu có.
    Thử ngôn ngữ `lang`, nếu không có sẽ thử 'en'. Trả về text or raise Exception.
    """
    tmpdir = tempfile.mkdtemp()
    for code in [lang, "en"]:
        cmd = [
            "yt-dlp", "--skip-download",
            "--write-auto-sub", "--sub-lang", code,
            "--convert-subs", "srt",
            "-o", os.path.join(tmpdir, "%(id)s.%(ext)s"),
            url
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        # tìm file .srt trong tmpdir
        srt_path = None
        for name in os.listdir(tmpdir):
            if name.endswith(".srt"):
                srt_path = os.path.join(tmpdir, name)
                break
        if srt_path and os.path.exists(srt_path):
            lines = []
            with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line: 
                        continue
                    if line.isdigit():
                        continue
                    if "-->" in line:
                        continue
                    lines.append(line)
            return "\n".join(lines)
    raise Exception("Không tìm thấy phụ đề tự động (auto-sub) cho video này.")
