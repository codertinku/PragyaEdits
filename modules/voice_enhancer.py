import subprocess
def ffmpeg_denoise_normalize(input_wav, output_wav, denoise_level=0.4):
    cmd = ["ffmpeg","-y","-i", str(input_wav), "-af","loudnorm=I=-16:TP=-1.5:LRA=11", str(output_wav)]
    subprocess.run(cmd, check=False)
    return str(output_wav)
