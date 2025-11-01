def build_filter_chain(target_res="1080x1920", mood="neutral"):
    base = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    look = "unsharp=5:5:0.8:5:5:0,vignette=PI/6:0.5"
    fade = "fade=t=in:st=0:d=0.3,fade=t=out:st=duration-0.3:d=0.3"
    if mood in ("energetic","happy"):
        return f"{base},{look},{fade}"
    elif mood in ("calm","sad"):
        return f"{base},eq=contrast=1.0:brightness=-0.02:saturation=0.9,{look},{fade}"
    else:
        return f"{base},{look},{fade}"
