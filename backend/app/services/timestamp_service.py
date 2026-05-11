# backend/app/services/timestamp_service.py
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TimestampService:
    """Extract timestamps from transcripts using pattern matching"""
    
    @staticmethod
    def extract_timestamps_from_text(text: str, query: str) -> List[Dict[str, Any]]:
        """Extract potential timestamps from text based on query"""
        
        timestamps = []
        
        # Pattern for time in HH:MM:SS or MM:SS format
        time_pattern = r'(\d{1,2}:)?(\d{1,2}):(\d{2})'
        
        # Find all time mentions in the text
        matches = re.finditer(time_pattern, text)
        
        for match in matches:
            time_str = match.group(0)
            seconds = TimestampService.time_to_seconds(time_str)
            
            # Get surrounding context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            # Check if context is relevant to query
            if query.lower() in context.lower() or any(word in context.lower() for word in query.lower().split()):
                timestamps.append({
                    "timestamp": seconds,
                    "text": context.strip(),
                    "start_time": seconds,
                    "end_time": seconds + 10
                })
        
        return timestamps[:5]  # Return top 5
    
    @staticmethod
    def time_to_seconds(time_str: str) -> float:
        """Convert time string (HH:MM:SS or MM:SS) to seconds"""
        parts = time_str.split(':')
        
        if len(parts) == 3:
            # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return float(parts[0])