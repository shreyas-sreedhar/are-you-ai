"""
CSV-based local storage for video and message analysis
Simple file-based storage for hackathon demo
"""
import csv
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class CSVStorage:
    """Simple CSV storage for analysis data"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize CSV storage with data directory"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.videos_file = self.data_dir / "videos.csv"
        self.messages_file = self.data_dir / "messages.csv"
        
        # Initialize CSV files with headers if they don't exist
        self._init_videos_csv()
        self._init_messages_csv()
        
        logger.info(f"CSV Storage initialized at: {self.data_dir.absolute()}")
    
    def _init_videos_csv(self):
        """Initialize videos CSV with headers"""
        if not self.videos_file.exists():
            with open(self.videos_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'video_id',
                    'platform',
                    'video_title',
                    'is_likely_fake',
                    'confidence_score',
                    'reasoning',
                    'analysis_result'
                ])
            logger.info("Created videos.csv")
    
    def _init_messages_csv(self):
        """Initialize messages CSV with headers"""
        if not self.messages_file.exists():
            with open(self.messages_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'sender',
                    'platform',
                    'message_text',
                    'scam_risk_score',
                    'risk_level',
                    'detected_scam_types',
                    'reasoning',
                    'analysis_result'
                ])
            logger.info("Created messages.csv")
    
    def save_video_analysis(self, video_data: Dict[str, Any]):
        """Save video analysis to CSV"""
        try:
            with open(self.videos_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    video_data.get('video_id', 'unknown'),
                    video_data.get('platform', 'youtube'),
                    video_data.get('video_title', ''),
                    video_data.get('is_likely_fake', False),
                    video_data.get('confidence_score', 0.0),
                    video_data.get('reasoning', ''),
                    json.dumps(video_data.get('analysis_result', {}))
                ])
            logger.info(f"Saved video analysis: {video_data.get('video_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save video analysis: {e}")
            return False
    
    def save_message_analysis(self, message_data: Dict[str, Any]):
        """Save message analysis to CSV"""
        try:
            with open(self.messages_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                detected_types = message_data.get('detected_scam_types', [])
                writer.writerow([
                    datetime.now().isoformat(),
                    message_data.get('sender', 'Unknown'),
                    message_data.get('platform', 'unknown'),
                    message_data.get('message_text', '')[:500],  # Limit length
                    message_data.get('scam_risk_score', 0.0),
                    message_data.get('risk_level', 'LOW'),
                    json.dumps(detected_types),
                    message_data.get('reasoning', ''),
                    json.dumps(message_data.get('analysis_result', {}))
                ])
            logger.info(f"Saved message analysis from: {message_data.get('sender')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save message analysis: {e}")
            return False
    
    def get_all_videos(self) -> List[Dict[str, Any]]:
        """Read all video analyses from CSV"""
        videos = []
        try:
            if not self.videos_file.exists():
                return videos
            
            with open(self.videos_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        videos.append({
                            'timestamp': row['timestamp'],
                            'video_id': row['video_id'],
                            'platform': row['platform'],
                            'video_title': row['video_title'],
                            'is_likely_fake': row['is_likely_fake'].lower() == 'true',
                            'confidence_score': float(row['confidence_score']),
                            'reasoning': row['reasoning'],
                            'analysis_result': json.loads(row['analysis_result']) if row['analysis_result'] else {}
                        })
                    except Exception as e:
                        logger.warning(f"Skipped malformed video row: {e}")
                        continue
        except Exception as e:
            logger.error(f"Failed to read videos CSV: {e}")
        
        return videos
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Read all message analyses from CSV"""
        messages = []
        try:
            if not self.messages_file.exists():
                return messages
            
            with open(self.messages_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        messages.append({
                            'timestamp': row['timestamp'],
                            'sender': row['sender'],
                            'platform': row['platform'],
                            'message_text': row['message_text'],
                            'scam_risk_score': float(row['scam_risk_score']),
                            'risk_level': row['risk_level'],
                            'detected_scam_types': json.loads(row['detected_scam_types']) if row['detected_scam_types'] else [],
                            'reasoning': row['reasoning'],
                            'analysis_result': json.loads(row['analysis_result']) if row['analysis_result'] else {}
                        })
                    except Exception as e:
                        logger.warning(f"Skipped malformed message row: {e}")
                        continue
        except Exception as e:
            logger.error(f"Failed to read messages CSV: {e}")
        
        return messages
    
    def get_metrics(self) -> Dict[str, int]:
        """Calculate metrics from CSV data"""
        videos = self.get_all_videos()
        messages = self.get_all_messages()
        
        videos_protected = len(videos)
        fake_videos = sum(1 for v in videos if v['is_likely_fake'])
        # Count all saved messages (MEDIUM, HIGH, CRITICAL)
        scam_messages = len(messages)
        
        # Recent alerts (last 24h high-risk items)
        from datetime import timedelta
        now = datetime.now()
        one_day_ago = now - timedelta(days=1)
        
        active_alerts = 0
        for video in videos:
            try:
                timestamp = datetime.fromisoformat(video['timestamp'])
                if timestamp >= one_day_ago and video['is_likely_fake'] and video['confidence_score'] >= 0.7:
                    active_alerts += 1
            except:
                pass
        
        for message in messages:
            try:
                timestamp = datetime.fromisoformat(message['timestamp'])
                # Count MEDIUM, HIGH, and CRITICAL from last 24h
                if timestamp >= one_day_ago and message['risk_level'] in ['MEDIUM', 'HIGH', 'CRITICAL']:
                    active_alerts += 1
            except:
                pass
        
        return {
            'videos_protected': videos_protected,
            'scams_detected': fake_videos + scam_messages,
            'messages_analyzed': len(messages),
            'active_alerts': active_alerts
        }
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent high-risk alerts"""
        alerts = []
        
        # Get fake videos
        videos = self.get_all_videos()
        for video in videos:
            if video['is_likely_fake']:
                alerts.append({
                    'id': f"video_{video['video_id']}_{video['timestamp']}",
                    'timestamp': video['timestamp'],
                    'type': 'video',
                    'source': video['platform'],
                    'title': video['video_title'],
                    'risk_level': 'HIGH' if video['confidence_score'] >= 0.7 else 'MEDIUM',
                    'description': video['reasoning'],
                    'confidence': video['confidence_score']
                })
        
        # Get scam messages (show all saved messages - MEDIUM, HIGH, CRITICAL)
        messages = self.get_all_messages()
        for message in messages:
            # Show all messages that were saved (already filtered as suspicious)
            alerts.append({
                'id': f"message_{message['sender']}_{message['timestamp']}",
                'timestamp': message['timestamp'],
                'type': 'message',
                'source': message['platform'],
                'title': f"Scam message from {message['sender']}",
                'risk_level': message['risk_level'],
                'description': message['reasoning'],
                'confidence': message['scam_risk_score']
            })
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return alerts[:limit]


# Singleton instance
_csv_storage = None

def get_csv_storage() -> CSVStorage:
    """Get or create CSV storage singleton"""
    global _csv_storage
    if _csv_storage is None:
        _csv_storage = CSVStorage()
    return _csv_storage

