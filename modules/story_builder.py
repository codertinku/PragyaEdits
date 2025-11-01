def compose_story(highlights, transcript_json, max_total_sec=45):
    out, total = [], 0.0
    for h in highlights:
        dur = max(0.3, h["end"]-h["start"])
        if total + dur > max_total_sec: break
        out.append(h); total += dur
    return out or highlights[:1]
