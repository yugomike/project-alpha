"""Combine multiple item audio clips into one dated episode file."""

from pydub import AudioSegment

PAUSE_MS = 1000  # brief pause between items so they don't blend together


def assemble_episode(clip_paths, output_path):
    """Concatenate audio clips (one per item) into a single episode file,
    with a short pause between each so items don't blend together."""
    pause = AudioSegment.silent(duration=PAUSE_MS)
    episode = AudioSegment.empty()
    for i, path in enumerate(clip_paths):
        if i > 0:
            episode += pause
        episode += AudioSegment.from_mp3(path)
    episode.export(output_path, format="mp3")