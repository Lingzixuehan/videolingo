import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import ffmpeg
import sys
import threading
import queue
import re
from datetime import datetime

def embed_subtitles(video_path, subtitle_path):
    """将字幕嵌入视频文件"""
    try:
        output_path = video_path[:video_path.rfind('.')] + '_with_subs' + video_path[video_path.rfind('.'):]
        # 规范化为绝对路径，然后转换为 POSIX 风格（使用正斜杠），
        # 因为在 Windows 上 ffmpeg 对路径解析更可靠（同时需要转义驱动器冒号）
        abs_sub = os.path.abspath(subtitle_path)
        posix_sub = abs_sub.replace('\\', '/')
        # 转义 Windows 驱动器冒号（例如 C: -> C\:）
        posix_sub = re.sub(r'^([A-Za-z]):', r"\1\\:", posix_sub)
        # 逃避单引号，确保能安全地放入单引号包裹的 filter 参数
        posix_sub = posix_sub.replace("'", r"\'")

        vf_arg = f"subtitles=filename='{posix_sub}'"
        # 记录将要传给 ffmpeg 的 filter 字符串，便于调试
        try:
            log_dir = os.path.dirname(video_path) or os.getcwd()
            with open(os.path.join(log_dir, 'ffmpeg_error.log'), 'a', encoding='utf-8') as lf:
                lf.write(f"[vf] {vf_arg}\n")
        except Exception:
            pass

        # 使用 vf 参数传入 subtitles 过滤器（在 Windows 上更可靠）
        ffmpeg.input(video_path).output(output_path, vf=vf_arg).run(overwrite_output=True)
        return output_path
    except ffmpeg.Error as e:
        stderr = e.stderr.decode(errors='replace') if getattr(e, 'stderr', None) else str(e)
        # 写入到日志文件，便于收集完整的错误信息供调试
        try:
            log_dir = os.path.dirname(video_path) or os.getcwd()
            log_path = os.path.join(log_dir, 'ffmpeg_error.log')
            with open(log_path, 'a', encoding='utf-8') as lf:
                lf.write(f"=== {datetime.now().isoformat()} ===\n")
                lf.write(f"video: {video_path}\n")
                lf.write(f"subtitle: {subtitle_path}\n")
                lf.write("stderr:\n")
                lf.write(stderr + "\n\n")
        except Exception:
            # 忽略日志写入错误
            pass
        print('FFmpeg 错误:', stderr)
        return None

# 用于在主线程和后台线程之间传递状态消息
status_queue = queue.Queue()


def _run_whisper_and_embed(video_path, model, outpath):
    """在后台运行 whisper（通过 `python -m whisper`），实时读取输出并在完成后嵌入字幕。"""
    try:
        cmd = [sys.executable, '-m', 'whisper', video_path, '--model', model, '--language', 'English', '--task', 'translate', '--output_format', 'srt', '--output_dir', outpath]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # 实时读取输出
        for line in proc.stdout:
            status_queue.put(line.strip())
        proc.wait()

        # Whisper 结束后查找生成的 srt
        srt_path = os.path.join(outpath, os.path.splitext(os.path.basename(video_path))[0] + '.srt')
        if os.path.exists(srt_path):
            status_queue.put('字幕生成完成，开始翻译（有道）...')
            # 调用翻译器脚本生成中文与中英双语 srt
            try:
                translator_py = os.path.join(os.path.dirname(__file__), 'whisperTranslator.py')
                proc = subprocess.run([sys.executable, translator_py, srt_path], capture_output=True, text=True, timeout=300)
                # 记录翻译脚本输出到日志
                log_dir = outpath or os.getcwd()
                with open(os.path.join(log_dir, 'whisper_translate.log'), 'a', encoding='utf-8') as lf:
                    lf.write(proc.stdout + '\n' + proc.stderr + '\n')
            except Exception as e:
                status_queue.put(f'翻译过程出错: {e}')
                proc = None

            # 以中文 srt 作为嵌入源
            zh_srt = os.path.join(outpath, os.path.splitext(os.path.basename(video_path))[0] + '-zh.srt')
            if os.path.exists(zh_srt):
                status_queue.put('开始嵌入中文字幕...')
                out_video = embed_subtitles(video_path, zh_srt)
                if out_video:
                    status_queue.put(f'嵌入完成：{out_video}')
                else:
                    status_queue.put('字幕嵌入失败，请检查 ffmpeg 日志')
            else:
                status_queue.put('未找到生成的中文字幕文件，嵌入取消')
        else:
            status_queue.put('字幕文件未找到，可能是 Whisper 处理失败')
    except Exception as e:
        status_queue.put(f'后台处理出错: {e}')


def _poll_status():
    """从队列取消息并更新 UI。"""
    updated = False
    try:
        while True:
            msg = status_queue.get_nowait()
            # 将最后一条消息显示到状态标签；可扩展为日志窗口
            status_label.config(text=msg)
            updated = True
    except queue.Empty:
        pass
    # 如果还有未处理的后台任务，继续轮询
    if updated or not status_queue.empty():
        root.after(200, _poll_status)

# 设置文件选择
def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        path_label.config(text=file_path)

# 调用whisper进行语音转文字并嵌入字幕
def whisper():
    # 判断是否选择了文件
    if path_label.cget("text") == "文件路径":
        messagebox.showinfo(title='提示', message='请先选择文件')
        return
    
    video_path = path_label.cget("text")
    # 找到文件夹路径
    outpath = os.path.dirname(video_path)
    print(f"输出路径: {outpath}")
    
    # 获得选择的语言模型
    model = model_dropdown_value.get()
    
    # 更新状态
    status_label.config(text="正在提取字幕...")
    root.update()
    
    try:
        # 合成命令行语句并执行
        cmd = f'start cmd /k "conda activate whisper-env && whisper "{video_path}" --model {model} --language English --task translate --output_format srt --output_dir "{outpath}" && EXIT"'
        print(f"执行命令: {cmd}")
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        
        # 获取生成的字幕文件路径
        srt_path = os.path.join(outpath, os.path.splitext(os.path.basename(video_path))[0] + '.srt')

        if os.path.exists(srt_path):
            status_label.config(text="正在翻译字幕（有道）...")
            root.update()
            # 调用翻译脚本（whisperTranslator.py）生成中文和中英双语 srt
            try:
                translator_py = os.path.join(os.path.dirname(__file__), 'whisperTranslator.py')
                proc = subprocess.run([sys.executable, translator_py, srt_path], capture_output=True, text=True, timeout=300)
                # 追加日志
                try:
                    with open(os.path.join(outpath, 'whisper_translate.log'), 'a', encoding='utf-8') as lf:
                        lf.write(proc.stdout + '\n' + proc.stderr + '\n')
                except Exception:
                    pass
            except Exception as e:
                messagebox.showerror(title='错误', message=f'翻译过程出错：\n{e}')
                status_label.config(text="翻译失败")
                return

            # 使用中文 srt 作为嵌入源
            zh_srt = os.path.join(outpath, os.path.splitext(os.path.basename(video_path))[0] + '-zh.srt')
            if os.path.exists(zh_srt):
                status_label.config(text="正在嵌入中文字幕...")
                root.update()
                output_path = embed_subtitles(video_path, zh_srt)
                if output_path:
                    messagebox.showinfo(title='成功', message=f'处理完成！\n带字幕的视频已保存到：\n{output_path}')
                    status_label.config(text="处理完成")
                else:
                    messagebox.showerror(title='错误', message='字幕嵌入失败，请检查FFmpeg是否正确安装')
                    status_label.config(text="字幕嵌入失败")
            else:
                messagebox.showerror(title='错误', message='未找到生成的中文字幕文件，嵌入取消')
                status_label.config(text="翻译生成失败")
        else:
            messagebox.showerror(title='错误', message='字幕提取失败，请检查视频文件和Whisper环境')
            status_label.config(text="字幕提取失败")
    except Exception as e:
        print(f"错误: {str(e)}")
        messagebox.showerror(title='错误', message=f'处理过程中出错：\n{str(e)}')
        status_label.config(text="处理失败")

# 添加程序入口
if __name__ =='__main__':
    root = tk.Tk()
    root.title("Videolingo")
    # 设置背景颜色
    root.config(bg="#F7EFE5")
    root.geometry("640x480")

    ################################语言模型选择################################
    # 窗口的最上面空一行
    ttk.Label(root).pack(pady=10)
    # 创建行的模块，以将模型选择的标签和下拉列表框放在一起
    model_row_frame = ttk.Frame(root)
    model_row_frame.pack(pady=10)
    # 创建模型标签
    model_dropdown_label = ttk.Label(model_row_frame, text="选择语言模型：", font=("微软雅黑", 14))
    model_dropdown_label.pack(side="left")
    # 创建模型选择拉列表
    model_options = ["tiny", "base", "small", "medium", "large"]
    model_dropdown_value = tk.StringVar(value=model_options[0])
    model_dropdown = ttk.Combobox(model_row_frame, textvariable=model_dropdown_value, justify="center", values=model_options, width=20, foreground="#FD5825", font=("微软雅黑", 14))
    model_dropdown.pack(side="left", padx=10)
    # 翻译引擎选择（已移除）
    ################################视频文件选择################################
    # 创建文件选择按钮
    # 创建行的模块，以将语言选择的标签和下拉列表框放在一起
    file_row_frame = ttk.Frame(root)
    file_row_frame.pack(pady=10)
    # 创建模型标签
    filepath_label = ttk.Label(file_row_frame, text="选择视频文件：", font=("微软雅黑", 14))
    filepath_label.pack(side="left")
    filepath_button = tk.Button(file_row_frame, text="...", command=browse_file, width=10, bg="#3FABAF", fg="#F7EFE5", font=("微软雅黑", 14, "bold"))
    filepath_button.pack(side="left", padx=10)
    # 创建文件路径标签，标签居中对齐
    path_label = ttk.Label(root, text="文件路径", font=("微软雅黑", 14), justify="center")
    path_label.pack(pady=10)
    ################################状态显示################################
    # 创建状态标签
    status_label = ttk.Label(root, text="就绪", font=("微软雅黑", 12))
    status_label.pack(pady=5)
    
    ################################操作按钮################################
    whisper_Trans_button = tk.Button(root, text="提取并嵌入字幕", command=whisper, width=20, bg="#3FABAF", fg="#F7EFE5", font=("微软雅黑", 14, "bold"))
    whisper_Trans_button.pack(pady=10)    
    # 显示主窗口
    root.mainloop()

