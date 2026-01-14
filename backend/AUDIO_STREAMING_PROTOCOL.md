# Audio Streaming Protocol Documentation

## Overview

The AI Therapy Platform uses a custom WebSocket-based audio streaming protocol optimized for real-time therapeutic conversations with Amazon Nova Sonic 2. The protocol supports:

- **Low-latency streaming** (< 200ms target)
- **Adaptive quality** based on network conditions
- **Buffering and flow control** for smooth playback
- **Quality monitoring** and metrics reporting
- **Multi-language support** with automatic detection

🏆 Breaking Barriers UK 2026 compliant

## Architecture

```
Client (Browser)
    ↓ WebSocket
API Gateway WebSocket
    ↓ Lambda
Audio Streaming Service
    ↓ Buffer Management
    ↓ Quality Adaptation
    ↓ Metrics Collection
Nova Sonic 2 Integration
```

## Message Protocol

### Connection Flow

1. **Establish WebSocket Connection**
   ```json
   {
     "type": "connection_established",
     "user_id": "user_123",
     "role": "client",
     "timestamp": "2026-01-14T10:30:00Z"
   }
   ```

2. **Join Session**
   ```json
   {
     "type": "join_session",
     "session_id": "session_abc123"
   }
   ```

3. **Initialize Audio Stream**
   ```json
   {
     "type": "audio_stream_init",
     "session_id": "session_abc123",
     "config": {
       "quality": "medium",
       "format": "opus",
       "sample_rate": 16000,
       "channels": 1
     }
   }
   ```

4. **Stream Ready Confirmation**
   ```json
   {
     "type": "audio_stream_ready",
     "session_id": "session_abc123",
     "config": {
       "format": "opus",
       "sample_rate": 16000,
       "channels": 1,
       "chunk_size_ms": 100,
       "buffer_size_chunks": 5,
       "max_latency_ms": 200.0,
       "quality": "medium",
       "enable_adaptation": true
     },
     "timestamp": "2026-01-14T10:30:01Z"
   }
   ```

### Audio Streaming

#### Send Audio Chunk (Client → Server)

```json
{
  "type": "audio_chunk",
  "chunk_id": "chunk_001",
  "session_id": "session_abc123",
  "sequence_number": 1,
  "audio_data": "base64_encoded_audio_data...",
  "format": "opus",
  "sample_rate": 16000,
  "channels": 1,
  "timestamp": 1705230600.123,
  "duration_ms": 100.0
}
```

#### Audio Chunk Acknowledgment (Server → Client)

```json
{
  "type": "audio_chunk_ack",
  "session_id": "session_abc123",
  "chunk_id": "chunk_001",
  "sequence_number": 1,
  "buffer_fill": 0.6,
  "state": "streaming",
  "timestamp": "2026-01-14T10:30:02Z"
}
```

#### Quality Metrics (Server → Client)

Sent periodically (every 10 chunks) to inform client of streaming quality:

```json
{
  "type": "quality_metrics",
  "session_id": "session_abc123",
  "metrics": {
    "current_latency_ms": 150.5,
    "average_latency_ms": 145.2,
    "packet_loss_rate": 0.01,
    "jitter_ms": 12.3,
    "buffer_underruns": 0,
    "buffer_overruns": 0,
    "chunks_received": 100,
    "chunks_dropped": 1,
    "bytes_transferred": 160000,
    "connection_quality": 0.92
  },
  "timestamp": "2026-01-14T10:30:03Z"
}
```

### Quality Adaptation

When network conditions change, the server automatically adapts quality:

```json
{
  "type": "quality_change",
  "session_id": "session_abc123",
  "old_quality": "high",
  "new_quality": "medium",
  "reason": "Network conditions degraded",
  "new_config": {
    "format": "opus",
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size_ms": 100,
    "buffer_size_chunks": 5
  },
  "timestamp": "2026-01-14T10:30:05Z"
}
```

### Stream Control

#### Pause Stream

```json
{
  "type": "audio_stream_pause",
  "session_id": "session_abc123"
}
```

#### Resume Stream

```json
{
  "type": "audio_stream_resume",
  "session_id": "session_abc123"
}
```

#### Close Stream

```json
{
  "type": "audio_stream_close",
  "session_id": "session_abc123"
}
```

## Audio Formats

### Supported Formats

| Format | Sample Rates | Channels | Use Case |
|--------|-------------|----------|----------|
| **OPUS** (Recommended) | 8kHz, 16kHz, 24kHz, 48kHz | 1-2 | Best compression, low latency |
| PCM 16-bit | 8kHz, 16kHz, 24kHz, 48kHz | 1-2 | Uncompressed, high quality |
| MP3 | 16kHz, 24kHz, 48kHz | 1-2 | Good compression, wider support |
| WAV | 16kHz, 24kHz, 48kHz | 1-2 | Uncompressed, maximum quality |

### Quality Presets

| Preset | Sample Rate | Chunk Size | Buffer Size | Target Latency |
|--------|------------|------------|-------------|----------------|
| **LOW** | 8kHz | 120ms | 3 chunks | < 300ms |
| **MEDIUM** (Default) | 16kHz | 100ms | 5 chunks | < 200ms |
| **HIGH** | 24kHz | 80ms | 7 chunks | < 150ms |
| **ULTRA** | 48kHz | 60ms | 10 chunks | < 100ms |

## Buffering Strategy

### Circular Buffer

The system uses a circular buffer to manage audio chunks:

- **Buffer Size**: Configurable (3-10 chunks based on quality)
- **Fill Threshold**: 50% before transitioning to streaming state
- **Underrun Handling**: Transition to buffering state, request retransmission
- **Overrun Handling**: Drop oldest chunks, log warning

### Buffer States

1. **IDLE**: No audio streaming
2. **BUFFERING**: Filling buffer before playback
3. **STREAMING**: Active playback with sufficient buffer
4. **PAUSED**: Streaming paused by user
5. **ERROR**: Error state requiring recovery

### Adaptive Buffering

Buffer size automatically adjusts based on network conditions:

- **Good connection** (quality > 0.8): Reduce buffer size for lower latency
- **Fair connection** (quality 0.6-0.8): Use default buffer size
- **Poor connection** (quality < 0.6): Increase buffer size for stability

## Quality Monitoring

### Metrics Collected

1. **Latency Metrics**
   - Current latency (ms)
   - Average latency (ms)
   - Jitter (ms)

2. **Packet Loss Metrics**
   - Packet loss rate (0.0-1.0)
   - Chunks received
   - Chunks dropped

3. **Buffer Metrics**
   - Buffer fill level (0.0-1.0)
   - Underrun count
   - Overrun count

4. **Connection Quality**
   - Overall quality score (0.0-1.0)
   - Calculated from latency, packet loss, and jitter

### Quality Adaptation Algorithm

```python
if connection_quality < 0.3:
    # Poor connection - downgrade to LOW
    adapt_to_quality(AudioQuality.LOW)
elif connection_quality < 0.6:
    # Fair connection - use MEDIUM
    adapt_to_quality(AudioQuality.MEDIUM)
elif connection_quality > 0.8:
    # Good connection - upgrade to HIGH
    adapt_to_quality(AudioQuality.HIGH)
```

## Error Handling

### Connection Errors

```json
{
  "type": "error",
  "error": "Connection lost",
  "error_code": "CONNECTION_LOST",
  "timestamp": "2026-01-14T10:30:10Z"
}
```

### Audio Processing Errors

```json
{
  "type": "error",
  "error": "Failed to process audio chunk",
  "error_code": "PROCESSING_ERROR",
  "details": {
    "chunk_id": "chunk_042",
    "sequence_number": 42
  },
  "timestamp": "2026-01-14T10:30:11Z"
}
```

### Recovery Strategies

1. **Buffer Underrun**: Transition to buffering state, continue when buffer fills
2. **Packet Loss**: Request retransmission if critical, otherwise interpolate
3. **Connection Degradation**: Automatically adapt quality downward
4. **Server Error**: Retry with exponential backoff, notify user if persistent

## Performance Targets

### Latency Requirements

- **Target**: < 200ms end-to-end
- **Acceptable**: < 300ms
- **Poor**: > 300ms (triggers quality adaptation)

### Packet Loss Tolerance

- **Excellent**: < 1% packet loss
- **Good**: 1-3% packet loss
- **Acceptable**: 3-5% packet loss
- **Poor**: > 5% packet loss (triggers quality adaptation)

### Bandwidth Requirements

| Quality | Bitrate | Bandwidth (with overhead) |
|---------|---------|---------------------------|
| LOW | ~12 kbps | ~20 kbps |
| MEDIUM | ~24 kbps | ~35 kbps |
| HIGH | ~32 kbps | ~45 kbps |
| ULTRA | ~64 kbps | ~80 kbps |

## Integration with Nova Sonic 2

### Processing Flow

1. Client sends audio chunk via WebSocket
2. Audio Streaming Service buffers and validates chunk
3. Chunk forwarded to Nova Sonic 2 for processing
4. Nova Sonic 2 returns processed audio response
5. Response buffered and sent back to client

### Nova Sonic 2 Messages

#### Processing Notification

```json
{
  "type": "nova_processing",
  "session_id": "session_abc123",
  "chunk_id": "chunk_001",
  "message": "Processing audio with Nova Sonic 2",
  "timestamp": "2026-01-14T10:30:12Z"
}
```

#### Response

```json
{
  "type": "nova_response",
  "session_id": "session_abc123",
  "response_id": "response_001",
  "audio_data": "base64_encoded_response_audio...",
  "format": "opus",
  "sample_rate": 16000,
  "channels": 1,
  "duration_ms": 2500.0,
  "transcript": "I understand how you're feeling...",
  "language": "en",
  "timestamp": "2026-01-14T10:30:14Z"
}
```

## Client Implementation Guidelines

### JavaScript/TypeScript Example

```typescript
// Initialize WebSocket connection
const ws = new WebSocket('wss://api.example.com/ws');

// Join session and initialize audio stream
ws.send(JSON.stringify({
  type: 'join_session',
  session_id: 'session_abc123'
}));

ws.send(JSON.stringify({
  type: 'audio_stream_init',
  session_id: 'session_abc123',
  config: {
    quality: 'medium'
  }
}));

// Capture and send audio chunks
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const audioContext = new AudioContext({ sampleRate: 16000 });
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(1600, 1, 1);
    
    let sequenceNumber = 0;
    
    processor.onaudioprocess = (e) => {
      const audioData = e.inputBuffer.getChannelData(0);
      const int16Array = new Int16Array(audioData.length);
      
      // Convert float32 to int16
      for (let i = 0; i < audioData.length; i++) {
        int16Array[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32768));
      }
      
      // Encode to base64
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(int16Array.buffer)));
      
      // Send chunk
      ws.send(JSON.stringify({
        type: 'audio_chunk',
        chunk_id: `chunk_${sequenceNumber}`,
        session_id: 'session_abc123',
        sequence_number: sequenceNumber++,
        audio_data: base64Audio,
        format: 'pcm_16bit',
        sample_rate: 16000,
        channels: 1,
        timestamp: Date.now() / 1000,
        duration_ms: 100
      }));
    };
    
    source.connect(processor);
    processor.connect(audioContext.destination);
  });

// Handle incoming messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'audio_stream_ready':
      console.log('Stream ready:', message.config);
      break;
    case 'audio_chunk_ack':
      console.log('Chunk acknowledged:', message.sequence_number);
      break;
    case 'quality_metrics':
      console.log('Quality metrics:', message.metrics);
      break;
    case 'quality_change':
      console.log('Quality adapted:', message.new_quality);
      break;
    case 'nova_response':
      // Play response audio
      playAudio(message.audio_data);
      break;
    case 'error':
      console.error('Error:', message.error);
      break;
  }
};
```

## Testing and Validation

### Unit Tests

- Audio chunk encoding/decoding
- Buffer operations (write, read, resize)
- Metrics calculation
- Quality adaptation logic

### Integration Tests

- End-to-end audio streaming
- Quality adaptation under simulated network conditions
- Buffer underrun/overrun handling
- Nova Sonic 2 integration

### Performance Tests

- Latency measurement under various network conditions
- Packet loss tolerance testing
- Concurrent session handling
- Memory usage and leak detection

## Security Considerations

1. **Authentication**: All WebSocket connections require valid JWT tokens
2. **Encryption**: All audio data transmitted over TLS 1.3
3. **Rate Limiting**: Per-connection rate limits to prevent abuse
4. **Data Validation**: All audio chunks validated before processing
5. **Session Isolation**: Audio streams isolated per session

## Monitoring and Observability

### CloudWatch Metrics

- `AudioStreamingLatency`: Average latency per session
- `AudioPacketLoss`: Packet loss rate
- `AudioBufferUnderruns`: Count of buffer underruns
- `AudioBufferOverruns`: Count of buffer overruns
- `ActiveAudioStreams`: Number of active streams
- `AudioQualityScore`: Average connection quality

### Logging

- Stream initialization and closure
- Quality adaptation events
- Buffer underrun/overrun events
- Error conditions and recovery attempts

## Future Enhancements

1. **Codec Negotiation**: Dynamic codec selection based on client capabilities
2. **Forward Error Correction**: FEC for improved packet loss resilience
3. **Jitter Buffer**: Advanced jitter buffer for smoother playback
4. **Multi-track Support**: Separate tracks for different audio sources
5. **Recording**: Optional session recording with consent
