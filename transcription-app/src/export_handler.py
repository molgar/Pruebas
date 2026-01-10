"""
Export Handler for Transcriptions
Supports TXT, SRT, and VTT export formats
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import timedelta


class TranscriptionSegment:
    """Represents a segment of transcribed text with timing and speaker info"""

    def __init__(
        self,
        text: str,
        start_time: float,
        end_time: float,
        speaker: Optional[str] = None
    ):
        """
        Initialize a transcription segment

        Args:
            text: The transcribed text
            start_time: Start time in seconds
            end_time: End time in seconds
            speaker: Optional speaker label
        """
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.speaker = speaker

    def __repr__(self):
        speaker_info = f" [{self.speaker}]" if self.speaker else ""
        return f"<Segment {self.start_time:.2f}-{self.end_time:.2f}s{speaker_info}: {self.text[:30]}...>"


class ExportHandler:
    """Handles exporting transcriptions to various formats"""

    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        """
        Format timestamp for SRT format (HH:MM:SS,mmm)

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def format_timestamp_vtt(seconds: float) -> str:
        """
        Format timestamp for VTT format (HH:MM:SS.mmm)

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    @staticmethod
    def export_txt(segments: List[TranscriptionSegment], filepath: str, include_speakers: bool = True) -> bool:
        """
        Export transcription as plain text

        Args:
            segments: List of transcription segments
            filepath: Output file path
            include_speakers: Whether to include speaker labels

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for segment in segments:
                    if include_speakers and segment.speaker:
                        f.write(f"[{segment.speaker}] {segment.text}\n")
                    else:
                        f.write(f"{segment.text}\n")
            return True
        except Exception as e:
            print(f"Error exporting TXT: {e}")
            return False

    @staticmethod
    def export_srt(segments: List[TranscriptionSegment], filepath: str, include_speakers: bool = True) -> bool:
        """
        Export transcription as SRT subtitle file

        Args:
            segments: List of transcription segments
            filepath: Output file path
            include_speakers: Whether to include speaker labels

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    # Subtitle number
                    f.write(f"{i}\n")

                    # Timestamp
                    start = ExportHandler.format_timestamp_srt(segment.start_time)
                    end = ExportHandler.format_timestamp_srt(segment.end_time)
                    f.write(f"{start} --> {end}\n")

                    # Text with optional speaker
                    if include_speakers and segment.speaker:
                        f.write(f"[{segment.speaker}] {segment.text}\n")
                    else:
                        f.write(f"{segment.text}\n")

                    # Blank line between subtitles
                    f.write("\n")
            return True
        except Exception as e:
            print(f"Error exporting SRT: {e}")
            return False

    @staticmethod
    def export_vtt(segments: List[TranscriptionSegment], filepath: str, include_speakers: bool = True) -> bool:
        """
        Export transcription as VTT (WebVTT) subtitle file

        Args:
            segments: List of transcription segments
            filepath: Output file path
            include_speakers: Whether to include speaker labels

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # VTT header
                f.write("WEBVTT\n\n")

                for segment in segments:
                    # Timestamp
                    start = ExportHandler.format_timestamp_vtt(segment.start_time)
                    end = ExportHandler.format_timestamp_vtt(segment.end_time)
                    f.write(f"{start} --> {end}\n")

                    # Text with optional speaker
                    if include_speakers and segment.speaker:
                        f.write(f"<v {segment.speaker}>{segment.text}\n")
                    else:
                        f.write(f"{segment.text}\n")

                    # Blank line between cues
                    f.write("\n")
            return True
        except Exception as e:
            print(f"Error exporting VTT: {e}")
            return False

    @staticmethod
    def export_json(segments: List[TranscriptionSegment], filepath: str) -> bool:
        """
        Export transcription as JSON (for advanced use cases)

        Args:
            segments: List of transcription segments
            filepath: Output file path

        Returns:
            True if successful
        """
        try:
            import json

            data = {
                'segments': [
                    {
                        'text': seg.text,
                        'start_time': seg.start_time,
                        'end_time': seg.end_time,
                        'speaker': seg.speaker,
                        'duration': seg.end_time - seg.start_time
                    }
                    for seg in segments
                ],
                'total_duration': max([seg.end_time for seg in segments]) if segments else 0,
                'segment_count': len(segments)
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False

    @staticmethod
    def export(
        segments: List[TranscriptionSegment],
        filepath: str,
        format: str = 'txt',
        include_speakers: bool = True
    ) -> bool:
        """
        Export transcription to specified format

        Args:
            segments: List of transcription segments
            filepath: Output file path
            format: Export format ('txt', 'srt', 'vtt', 'json')
            include_speakers: Whether to include speaker labels

        Returns:
            True if successful
        """
        format = format.lower()

        if format == 'txt':
            return ExportHandler.export_txt(segments, filepath, include_speakers)
        elif format == 'srt':
            return ExportHandler.export_srt(segments, filepath, include_speakers)
        elif format == 'vtt':
            return ExportHandler.export_vtt(segments, filepath, include_speakers)
        elif format == 'json':
            return ExportHandler.export_json(segments, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    @staticmethod
    def create_segments_from_text(text: str, chunk_duration: float = 3.0) -> List[TranscriptionSegment]:
        """
        Create segments from plain text (for simple transcriptions without timing)

        Args:
            text: Plain transcribed text
            chunk_duration: Estimated duration per segment in seconds

        Returns:
            List of transcription segments
        """
        # Split by sentences or newlines
        import re
        sentences = re.split(r'[.!?]\s+|\n+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        segments = []
        current_time = 0.0

        for sentence in sentences:
            # Estimate duration based on word count (rough approximation)
            word_count = len(sentence.split())
            duration = max(chunk_duration, word_count * 0.3)  # ~0.3 seconds per word

            segment = TranscriptionSegment(
                text=sentence,
                start_time=current_time,
                end_time=current_time + duration
            )
            segments.append(segment)
            current_time += duration

        return segments
