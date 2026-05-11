// frontend/src/components/MediaPlayer.jsx
import React, { useRef, useState, useEffect } from 'react'
import { Play, Pause, Volume2, VolumeX, Maximize, Clock, SkipBack, SkipForward } from 'lucide-react'

function MediaPlayer({ url, timestamps = [], onTimestampClick }) {
  const [playing, setPlaying] = useState(false)
  const [volume, setVolume] = useState(0.8)
  const [muted, setMuted] = useState(false)
  const [played, setPlayed] = useState(0)
  const [duration, setDuration] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const videoRef = useRef(null)

  const handlePlayPause = () => {
    if (playing) {
      videoRef.current.pause()
    } else {
      videoRef.current.play()
    }
    setPlaying(!playing)
  }

  const handleVolumeChange = (e) => {
    const value = parseFloat(e.target.value)
    setVolume(value)
    setMuted(value === 0)
    if (videoRef.current) {
      videoRef.current.volume = value
    }
  }

  const handleMute = () => {
    setMuted(!muted)
    if (videoRef.current) {
      videoRef.current.muted = !muted
    }
  }

  const handleSeek = (e) => {
    const seekTime = parseFloat(e.target.value)
    setPlayed(seekTime / duration)
    setCurrentTime(seekTime)
    if (videoRef.current) {
      videoRef.current.currentTime = seekTime
    }
  }

  const handleProgress = () => {
    if (videoRef.current) {
      const current = videoRef.current.currentTime
      setCurrentTime(current)
      setPlayed(current / duration)
    }
  }

  const handleDuration = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00'
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const jumpToTimestamp = (timestamp) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestamp
      videoRef.current.play()
      setPlaying(true)
      setCurrentTime(timestamp)
      if (onTimestampClick) {
        onTimestampClick(timestamp)
      }
    }
  }

  const skipBackward = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(0, currentTime - 10)
    }
  }

  const skipForward = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.min(duration, currentTime + 10)
    }
  }

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen()
      }
    }
  }

  return (
    <div className="bg-black rounded-lg overflow-hidden">
      <video
        ref={videoRef}
        src={url}
        className="w-full"
        onTimeUpdate={handleProgress}
        onDurationChange={handleDuration}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        controls={false}
      />
      
      {/* Custom Controls */}
      <div className="p-3 bg-gray-900">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={skipBackward} className="text-white hover:text-gray-300">
            <SkipBack className="w-4 h-4" />
          </button>
          
          <button onClick={handlePlayPause} className="text-white hover:text-gray-300">
            {playing ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          
          <button onClick={skipForward} className="text-white hover:text-gray-300">
            <SkipForward className="w-4 h-4" />
          </button>
          
          <div className="flex-1">
            <input
              type="range"
              min={0}
              max={duration}
              value={currentTime}
              onChange={handleSeek}
              className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(currentTime / duration) * 100}%, #4b5563 ${(currentTime / duration) * 100}%, #4b5563 100%)`
              }}
            />
          </div>
          
          <span className="text-xs text-gray-400">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
          
          <button onClick={handleMute} className="text-white hover:text-gray-300">
            {muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
          
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={volume}
            onChange={handleVolumeChange}
            className="w-20 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
          />
          
          <button onClick={handleFullscreen} className="text-white hover:text-gray-300">
            <Maximize className="w-4 h-4" />
          </button>
        </div>
        
        {/* Timestamps Section */}
        {timestamps && timestamps.length > 0 && (
          <div className="border-t border-gray-800 pt-2 mt-2">
            <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
              <Clock className="w-3 h-3" />
              <span>Key moments:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {timestamps.map((ts, idx) => (
                <button
                  key={idx}
                  onClick={() => jumpToTimestamp(ts.timestamp)}
                  className="px-2 py-1 bg-gray-800 hover:bg-blue-600 rounded text-xs text-white transition"
                >
                  {formatTime(ts.timestamp)} - {ts.label || 'Jump to moment'}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MediaPlayer