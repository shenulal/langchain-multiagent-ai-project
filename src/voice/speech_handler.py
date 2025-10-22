"""
Speech handling for voice input and output
"""

import os
import io
import base64
import tempfile
from typing import Optional
import speech_recognition as sr
import pyttsx3
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

class SpeechHandler:
    """
    Handles speech-to-text and text-to-speech functionality
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize TTS engine
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize the text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            rate = int(os.getenv("SPEECH_RATE", 200))
            volume = float(os.getenv("SPEECH_VOLUME", 0.9))
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            # Try to set a better voice if available
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            self.tts_engine = None
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech audio to text
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        try:
            # Run speech recognition in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor,
                self._recognize_speech,
                audio_data
            )
            
            logger.info(f"Speech recognized: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error in speech-to-text: {str(e)}")
            return "Sorry, I couldn't understand the audio."
    
    def _recognize_speech(self, audio_data: bytes) -> str:
        """
        Perform speech recognition (runs in thread pool)
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                return text
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            return "Sorry, there was an error with the speech recognition service."
        except Exception as e:
            logger.error(f"Error recognizing speech: {str(e)}")
            return "Sorry, there was an error processing the audio."
    
    async def text_to_speech(self, text: str) -> str:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Base64 encoded audio data
        """
        try:
            if not self.tts_engine:
                logger.warning("TTS engine not available")
                return ""
            
            # Run TTS in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                self.executor,
                self._synthesize_speech,
                text
            )
            
            if audio_data:
                # Encode audio as base64 for transmission
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                logger.info(f"Text synthesized to speech: {len(text)} characters")
                return audio_base64
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return ""
    
    def _synthesize_speech(self, text: str) -> Optional[bytes]:
        """
        Perform text-to-speech synthesis (runs in thread pool)
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        try:
            # Create a temporary file for the audio output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Save speech to file
                self.tts_engine.save_to_file(text, temp_file_path)
                self.tts_engine.runAndWait()
                
                # Read the audio file
                with open(temp_file_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                return audio_data
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return None
    
    async def listen_from_microphone(self, timeout: int = 5) -> str:
        """
        Listen for speech from microphone
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Transcribed text
        """
        try:
            if not self.microphone:
                self.microphone = sr.Microphone()
            
            # Run microphone listening in thread pool
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.executor,
                self._listen_microphone,
                timeout
            )
            
            return text
            
        except Exception as e:
            logger.error(f"Error listening from microphone: {str(e)}")
            return "Sorry, I couldn't access the microphone."
    
    def _listen_microphone(self, timeout: int) -> str:
        """
        Listen from microphone (runs in thread pool)
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Transcribed text
        """
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Listening for speech...")
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Microphone speech recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            return "No speech detected within the timeout period."
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand what you said."
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            return "Sorry, there was an error with the speech recognition service."
        except Exception as e:
            logger.error(f"Error listening from microphone: {str(e)}")
            return "Sorry, there was an error accessing the microphone."
    
    def speak_text(self, text: str):
        """
        Speak text immediately (blocking operation)
        
        Args:
            text: Text to speak
        """
        try:
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                logger.info(f"Spoke text: {text[:50]}...")
            else:
                logger.warning("TTS engine not available for immediate speech")
                
        except Exception as e:
            logger.error(f"Error speaking text: {str(e)}")
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        try:
            if self.tts_engine:
                voices = self.tts_engine.getProperty('voices')
                return [{"id": voice.id, "name": voice.name} for voice in voices]
            return []
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set TTS voice by ID"""
        try:
            if self.tts_engine:
                self.tts_engine.setProperty('voice', voice_id)
                logger.info(f"Voice set to: {voice_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting voice: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.tts_engine:
                self.tts_engine.stop()
            self.executor.shutdown(wait=True)
            logger.info("Speech handler cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
