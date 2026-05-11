// frontend/src/components/VoiceRecorder.jsx
import React, { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Loader2, Send, AlertCircle } from 'lucide-react'

function VoiceRecorder({ onTranscript, onSend, disabled = false }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [supported, setSupported] = useState(true)
  const [permission, setPermission] = useState(null)
  const [error, setError] = useState(null)
  const recognitionRef = useRef(null)

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      setSupported(false)
      setError('Speech recognition not supported. Please use Chrome, Edge, or Safari.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'
    recognition.maxAlternatives = 1
    
    recognition.onstart = () => {
      console.log('🎤 Voice recognition started')
      setIsRecording(true)
      setError(null)
    }
    
    recognition.onend = () => {
      console.log('🔇 Voice recognition ended')
      setIsRecording(false)
    }
    
    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interim = ''
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        const text = result[0].transcript
        
        if (result.isFinal) {
          finalTranscript += text + ' '
        } else {
          interim += text
        }
      }
      
      if (finalTranscript) {
        setTranscript(prev => prev + finalTranscript)
        onTranscript?.(transcript + finalTranscript)
      }
      
      setInterimTranscript(interim)
    }
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      
      switch(event.error) {
        case 'not-allowed':
          setError('Microphone access denied. Please allow microphone permissions.')
          break
        case 'no-speech':
          setError('No speech detected. Please try again.')
          break
        case 'audio-capture':
          setError('No microphone found. Please connect a microphone.')
          break
        default:
          setError(`Error: ${event.error}`)
      }
      
      setIsRecording(false)
    }
    
    recognitionRef.current = recognition
    
    const requestPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        stream.getTracks().forEach(track => track.stop())
        setPermission('granted')
      } catch (err) {
        setPermission('denied')
        setError('Microphone access required for voice input.')
      }
    }
    
    requestPermission()
    
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch (e) {}
      }
    }
  }, [])

  const startRecording = () => {
    setError(null)
    setTranscript('')
    setInterimTranscript('')
    
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start()
      } catch (e) {
        console.log('Recognition already started')
      }
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {}
    }
    setIsRecording(false)
  }

  const clearTranscript = () => {
    setTranscript('')
    setInterimTranscript('')
    onTranscript?.('')
  }

  const handleSend = () => {
    if (transcript.trim()) {
      onSend?.(transcript.trim())
      setTranscript('')
      setInterimTranscript('')
    }
  }

  if (!supported) {
    return (
      <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
        <div className="flex items-center gap-2 text-yellow-800 mb-2">
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">Voice input not supported</span>
        </div>
        <p className="text-sm text-yellow-700">
          Your browser doesn't support speech recognition. Please use Chrome or Edge.
        </p>
      </div>
    )
  }

  const displayText = transcript + (interimTranscript ? ` (${interimTranscript})` : '')

  return (
    <div className="space-y-3">
      {error && (
        <div className="p-3 bg-red-50 rounded-lg border border-red-200">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="flex gap-2">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={disabled}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            <Mic className="w-4 h-4" />
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            disabled={disabled}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition animate-pulse"
          >
            <MicOff className="w-4 h-4" />
            Stop Recording
          </button>
        )}
        
        {displayText && (
          <>
            <button
              onClick={clearTranscript}
              className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Clear
            </button>
            <button
              onClick={handleSend}
              disabled={disabled || !transcript.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </>
        )}
      </div>
      
      {displayText && (
        <div className="p-3 bg-gray-100 rounded-lg">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Transcript:</span> {displayText}
          </p>
        </div>
      )}
      
      {isRecording && (
        <div className="flex items-center gap-2 text-sm text-red-600">
          <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />
          Recording... Speak clearly
        </div>
      )}
    </div>
  )
}

export default VoiceRecorder