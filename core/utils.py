import time, traceback

ERROR_LOG = "error_log.txt"

def log_error(exc_info, context="N/A"):
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"--- LỖI LÚC {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            f.write(f"Ngữ cảnh: {context}\n")
            traceback.print_exception(*exc_info, file=f)
            f.write("-"*80 + "\n\n")
    except Exception as e:
        print("LOG ERROR FAILED:", e)
