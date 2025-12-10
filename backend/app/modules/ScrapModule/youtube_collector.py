import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import isodate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...model.youtube_model import YouTubeVideo, YouTubeBatch, YouTubeThumbnail

logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.youtube = None
        
        if api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=api_key)
            except Exception as e:
                logger.error(f"Error initializing YouTube API: {e}")
        
        self.search_queries = [
            'Sri Lanka news',
            'Sri Lanka economy',
            'Sri Lanka politics',
            'Colombo',
            'Sri Lanka travel',
            'Sri Lanka business',
            'Sri Lanka cricket',
            'Sri Lanka weather'
        ]
    
    def search_videos(self, query: str, max_results: int = 10) -> List[YouTubeVideo]:
        """Search YouTube videos for a query"""
        if not self.youtube:
            logger.warning("YouTube API not initialized")
            return []
        
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='date',
                relevanceLanguage='en',
                regionCode='LK'
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                try:
                    video_id = item['id']['videoId']
                    video_details = self.get_video_details(video_id)
                    
                    if video_details:
                        videos.append(video_details)
                    
                except Exception as e:
                    logger.error(f"Error processing video {item.get('id', {}).get('videoId')}: {e}")
                    continue
            
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error for query '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube for '{query}': {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[YouTubeVideo]:
        """Get detailed information about a specific video"""
        if not self.youtube:
            return None
        
        try:
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            item = video_response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # Parse thumbnails
            thumbnails = {}
            for quality, thumb_data in snippet.get('thumbnails', {}).items():
                thumbnails[quality] = YouTubeThumbnail(
                    url=thumb_data['url'],
                    width=thumb_data.get('width', 0),
                    height=thumb_data.get('height', 0)
                )
            
            # Parse duration
            duration = content_details.get('duration', 'PT0M')
            if duration:
                duration = isodate.parse_duration(duration)
                duration_str = str(duration)
            else:
                duration_str = "PT0M"
            
            # Parse published date
            published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
            
            video = YouTubeVideo(
                video_id=video_id,
                title=snippet['title'],
                description=snippet.get('description', ''),
                channel_id=snippet['channelId'],
                channel_title=snippet['channelTitle'],
                published_at=published_at,
                thumbnails=thumbnails,
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)),
                comment_count=int(statistics.get('commentCount', 0)),
                duration=duration_str,
                category_id=snippet.get('categoryId', '0'),
                tags=snippet.get('tags', []),
                default_audio_language=snippet.get('defaultAudioLanguage'),
                metadata={
                    'etag': item.get('etag', ''),
                    'kind': item.get('kind', '')
                }
            )
            
            return video
            
        except HttpError as e:
            logger.error(f"YouTube API error for video {video_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting video details for {video_id}: {e}")
            return None
    
    def get_channel_videos(self, channel_id: str, max_results: int = 20) -> List[YouTubeVideo]:
        """Get videos from a specific channel"""
        if not self.youtube:
            return []
        
        try:
            search_response = self.youtube.search().list(
                channelId=channel_id,
                part='id,snippet',
                maxResults=max_results,
                order='date',
                type='video'
            ).execute()
            
            videos = []
            for item in search_response.get('items', []):
                try:
                    video_id = item['id']['videoId']
                    video_details = self.get_video_details(video_id)
                    
                    if video_details:
                        videos.append(video_details)
                    
                except Exception as e:
                    logger.error(f"Error processing channel video: {e}")
                    continue
            
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error for channel {channel_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting channel videos for {channel_id}: {e}")
            return []
    
    def get_trending_videos(self, region_code: str = "LK") -> List[YouTubeVideo]:
        """Get trending videos for Sri Lanka"""
        if not self.youtube:
            return []
        
        try:
            videos_response = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=20
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                try:
                    snippet = item['snippet']
                    statistics = item.get('statistics', {})
                    content_details = item.get('contentDetails', {})
                    
                    # Parse thumbnails
                    thumbnails = {}
                    for quality, thumb_data in snippet.get('thumbnails', {}).items():
                        thumbnails[quality] = YouTubeThumbnail(
                            url=thumb_data['url'],
                            width=thumb_data.get('width', 0),
                            height=thumb_data.get('height', 0)
                        )
                    
                    # Parse duration
                    duration = content_details.get('duration', 'PT0M')
                    if duration:
                        duration = isodate.parse_duration(duration)
                        duration_str = str(duration)
                    else:
                        duration_str = "PT0M"
                    
                    # Parse published date
                    published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                    
                    video = YouTubeVideo(
                        video_id=item['id'],
                        title=snippet['title'],
                        description=snippet.get('description', ''),
                        channel_id=snippet['channelId'],
                        channel_title=snippet['channelTitle'],
                        published_at=published_at,
                        thumbnails=thumbnails,
                        view_count=int(statistics.get('viewCount', 0)),
                        like_count=int(statistics.get('likeCount', 0)),
                        comment_count=int(statistics.get('commentCount', 0)),
                        duration=duration_str,
                        category_id=snippet.get('categoryId', '0'),
                        tags=snippet.get('tags', []),
                        default_audio_language=snippet.get('defaultAudioLanguage'),
                        metadata={
                            'etag': item.get('etag', ''),
                            'kind': item.get('kind', ''),
                            'is_trending': True
                        }
                    )
                    
                    videos.append(video)
                    
                except Exception as e:
                    logger.error(f"Error processing trending video: {e}")
                    continue
            
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error for trending videos: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting trending videos: {e}")
            return []
    
    def collect_youtube_data(self) -> YouTubeBatch:
        """Main method to collect YouTube data"""
        logger.info("Starting YouTube data collection...")
        
        all_videos = []
        
        # Search for videos using queries
        for query in self.search_queries:
            try:
                videos = self.search_videos(query, max_results=5)
                all_videos.extend(videos)
                logger.info(f"Collected {len(videos)} videos for query: {query}")
                
            except Exception as e:
                logger.error(f"Error processing query {query}: {e}")
                continue
        
        # Get trending videos
        try:
            trending_videos = self.get_trending_videos()
            all_videos.extend(trending_videos)
            logger.info(f"Collected {len(trending_videos)} trending videos")
        except Exception as e:
            logger.error(f"Error getting trending videos: {e}")
        
        # Remove duplicates
        unique_videos = self._remove_duplicates(all_videos)
        
        batch = YouTubeBatch(
            videos=unique_videos,
            search_query="multiple",
            scrape_timestamp=datetime.now()
        )
        
        logger.info(f"Total unique videos collected: {len(unique_videos)}")
        return batch
    
    def _remove_duplicates(self, videos: List[YouTubeVideo]) -> List[YouTubeVideo]:
        """Remove duplicate videos"""
        seen_videos = set()
        unique_videos = []
        
        for video in videos:
            if video.video_id not in seen_videos:
                seen_videos.add(video.video_id)
                unique_videos.append(video)
        
        return unique_videos

    