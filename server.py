import os
import glob
import tempfile
import shutil
import queue
import json
import threading
from flask import Flask, request, jsonify, render_template, Response, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "downloader_cache")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

os.environ["PATH"] = BASE_DIR + os.pathsep + os.environ.get("PATH", "")

HAS_FFMPEG = shutil.which("ffmpeg") is not None or os.path.exists(os.path.join(BASE_DIR, "ffmpeg.exe"))

progress_queues = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/fetch", methods=["POST"])
def fetch_media():
    try:
        data = request.get_json(silent=True) or {}
        url = data.get("url")

        if not url:
            return jsonify({"error": "Lütfen geçerli bir bağlantı girin."}), 400

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'ffmpeg_location': BASE_DIR
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            raw_formats = info.get("formats", [])
            quality_options = []
            seen_res = set()

            for f in raw_formats:
                vcodec = f.get("vcodec", "none")
                if vcodec != "none":
                    h = f.get("height") or 0
                    w = f.get("width") or 0
                    res = max(h, w)
                    
                    if res > 0 and res not in seen_res:
                        seen_res.add(res)
                        quality_options.append({
                            "format_id": f"res_{res}",
                            "label": f"{res}p Video",
                            "res": res,
                            "type": "video"
                        })

            quality_options = sorted(quality_options, key=lambda x: x["res"], reverse=True)

            if not quality_options:
                quality_options.append({
                    "format_id": "best",
                    "label": "En İyi Kalite",
                    "res": 9999,
                    "type": "video"
                })

            quality_options.append({
                "format_id": "audio_only",
                "label": "Sadece Ses (MP3)",
                "res": -1,
                "type": "audio"
            })

            return jsonify({
                "title": info.get("title", "video"),
                "thumbnail": info.get("thumbnail"),
                "qualities": quality_options
            })

    except Exception as e:
        return jsonify({"error": f"Bilgi alınamadı: {str(e)}"}), 500

@app.route("/api/start-download", methods=["POST"])
def start_download():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    format_id = data.get("format_id")
    title = data.get("title", "video")

    if not url or not format_id:
        return jsonify({"error": "Eksik parametre."}), 400

    task_id = str(os.urandom(8).hex())
    q = queue.Queue()
    progress_queues[task_id] = q

    def background_download():
        safe_name = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip() or "video"
        out_template = os.path.join(DOWNLOAD_DIR, f"{safe_name}_%(id)s.%(ext)s")

        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                percent = int(round((downloaded / total) * 100)) if total > 0 else 0
                speed = d.get('_speed_str', 'Bilinmiyor')
                eta = d.get('_eta_str', 'Bilinmiyor')
                
                q.put({
                    "status": "downloading",
                    "percent": percent,
                    "speed": speed,
                    "eta": eta
                })
            elif d['status'] == 'finished':
                q.put({
                    "status": "processing",
                    "percent": 100,
                    "message": "Ses ve görüntü birleştiriliyor..."
                })

        ydl_opts = {
            'outtmpl': out_template,
            'quiet': False,  
            'no_warnings': False,
            'ffmpeg_location': BASE_DIR,
            'progress_hooks': [progress_hook]
        }

        if format_id == "audio_only":
            ydl_opts.update({
                'format': 'ba/b',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            })
        elif format_id.startswith("res_"):
            res_val = format_id.split("_")[1]
            
            ydl_opts.update({
                'format': f"bv*[height<={res_val}]+ba/b[height<={res_val}]/b",
                'merge_output_format': 'mp4'
            })
        else:
            ydl_opts.update({
                'format': 'bv*+ba/b',
                'merge_output_format': 'mp4'
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get("id")
                matched = glob.glob(os.path.join(DOWNLOAD_DIR, f"{safe_name}_{video_id}.*"))
                
                if matched:
                    q.put({
                        "status": "completed",
                        "filename": os.path.basename(matched[0]),
                        "filepath": matched[0]
                    })
                else:
                    q.put({"status": "error", "message": "Dosya bulunamadı."})
        except Exception as e:
            q.put({"status": "error", "message": str(e)})

    threading.Thread(target=background_download, daemon=True).start()
    return jsonify({"task_id": task_id})

@app.route("/api/progress/<task_id>")
def progress_stream(task_id):
    def generate():
        q = progress_queues.get(task_id)
        if not q:
            yield f"data: {json.dumps({'status': 'error', 'message': 'Task bulunamadı'})}\n\n"
            return

        while True:
            try:
                data = q.get(timeout=60)
                yield f"data: {json.dumps(data)}\n\n"
                if data["status"] in ["completed", "error"]:
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'status': 'error', 'message': 'Zaman aşımı'})}\n\n"
                break
        
        if task_id in progress_queues:
            del progress_queues[task_id]

    return Response(generate(), mimetype="text/event-stream")

@app.route("/api/get-file")
def get_file():
    filepath = request.args.get("path")
    if not filepath or not os.path.exists(filepath):
        return "Dosya bulunamadı", 404

    filename = os.path.basename(filepath)

    @after_this_request
    def cleanup(response):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        return response

    return send_file(filepath, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    PORT = 8080
    print(f"\n🚀 Servis Hazır: http://localhost:{PORT}")
    print(f"🎬 FFmpeg Durumu: {'AKTİF' if HAS_FFMPEG else 'BULUNAMADI'}\n")
    app.run(debug=True, host="0.0.0.0", port=PORT)