// Mock AI service for demo mode
// 🏆 Breaking Barriers UK 2026 compliant

export class MockAIService {
  private static responses = [
    "I understand how you're feeling. Can you tell me more about that?",
    "That sounds challenging. How has this been affecting you?",
    "Thank you for sharing that with me. What would you like to explore further?",
    "I hear you. It's important to acknowledge these feelings.",
    "That's a significant insight. How do you feel about that realization?",
    "Let's take a moment to reflect on what you just said.",
    "I'm here to support you. What else is on your mind?",
    "That's a very thoughtful observation. Can you elaborate?",
  ];

  private static responseIndex = 0;

  /**
   * Simulate AI response with delay
   */
  static async getResponse(userMessage: string): Promise<string> {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

    // Cycle through responses
    const response = this.responses[this.responseIndex];
    this.responseIndex = (this.responseIndex + 1) % this.responses.length;

    return response;
  }

  /**
   * Simulate audio response
   */
  static async getAudioResponse(audioData: ArrayBuffer): Promise<ArrayBuffer> {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Return empty audio buffer (in real implementation, this would be TTS audio)
    return new ArrayBuffer(0);
  }

  /**
   * Check if message contains red flags
   */
  static detectRedFlags(message: string): boolean {
    const redFlagKeywords = [
      'suicide', 'kill myself', 'end it all', 'not worth living',
      'hurt myself', 'self-harm', 'want to die'
    ];

    const lowerMessage = message.toLowerCase();
    return redFlagKeywords.some(keyword => lowerMessage.includes(keyword));
  }
}
