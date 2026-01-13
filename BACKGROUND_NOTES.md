# uKind Therapeutic AI Companion - Background Notes

**Prepared by:** Reflex Arc  
**Date:** December 2025

## Executive Summary

This document outlines the backend infrastructure required to transform what we have from a standalone prototype into a production-ready therapeutic AI companion. Given the sensitive nature of the content (trauma support, mental health conversations), the backend must prioritise:

1. Data security and encryption - protecting highly sensitive mental health conversations
2. GDPR compliance - meeting UK/EU data protection requirements for health-related data
3. Conversation memory - enabling continuity across sessions for therapeutic effectiveness
4. Secure authentication - protecting user accounts and personal data

The current Unity application handles the user interface, voice synthesis, and real-time interaction. The proposed backend will handle user management, data persistence, and secure API routing.

## Current Architecture

The prototype currently operates with the following components:

• **Unity Application:** Handles all user interaction, voice input/output, visual elements, and chairwork exercises  
• **OpenAI API:** Provides the conversational AI capabilities (GPT-5)  
• **ElevenLabs API:** Text-to-speech voice synthesis  
• **Local Configuration:** API keys and prompts stored in local config files  
• **Local Persistence only:** Conversations are currently saved as a JSON file between sessions (expecting clearing between test sessions with different people as there is no user authentication)

**Key limitation:** Without a backend, each session starts fresh with no memory of previous conversations (if local data files cleared) and has no sense of user ID. As a proof of concept level only (not for distribution) API keys are currently exposed in the Unity client application's configuration. It is vital these are moved to a backend.

## Backend Requirements

### 1. Authentication & User Management

A secure authentication system is essential for identifying users and protecting their data. Given the sensitive nature of mental health conversations, this requires careful consideration.

**Required Features:**
1. Secure user registration and login – email/password with strong password requirements, or OAuth (Google, Apple)
2. Multi-factor authentication (MFA) – recommended for health-related applications
3. Secure session management – JWT tokens with appropriate expiry times
4. Password reset flows – secure email-based recovery
5. Account deletion – GDPR requires users can delete their account and all associated data

**Technical Recommendation:**
Use a managed authentication service such as Auth0, Firebase Authentication, or AWS Cognito. These provide GDPR-compliant authentication out of the box, including secure password storage, MFA support, and audit logging. Building custom authentication is not recommended due to security complexity.

### 2. Conversation Memory & Persistence

For therapeutic effectiveness, it needs to remember previous conversations. This enables the AI to reference past discussions, track progress, and maintain continuity in the therapeutic relationship.

**Data to Store:**
1. Conversation transcripts – full history of user messages and AI responses
2. Session metadata – timestamps, session duration, therapeutic exercises completed
3. Conversation summaries – AI-generated summaries for context in future sessions (reduces token usage)
4. User preferences – voice settings, language, accessibility options
5. Flagged content – records of safeguarding triggers for clinical oversight if applicable

**Technical Recommendation:**
Use an encrypted database solution. PostgreSQL with encryption at rest is recommended, hosted on a GDPR-compliant cloud provider (AWS EU, Azure EU, or Google Cloud EU regions). All conversation data must be encrypted both in transit (TLS 1.3) and at rest (AES-256).

### 3. API Gateway & Security

The backend must act as a secure intermediary between the Unity application and external services (OpenAI, ElevenLabs or equivalents). This prevents API keys from being exposed in the client application.

**Required Functions:**
• API key management - store OpenAI and ElevenLabs keys securely on the server, never in the client
• Request proxying - Unity app sends requests to the backend, which forwards to external APIs
• Rate limiting - prevent abuse and manage API costs
• Request logging - audit trail for compliance (without storing sensitive content in logs)
• Cost monitoring - track API usage per user for billing purposes if needed

## GDPR Compliance Requirements

As this processes special category data (health/mental health information), it falls under the strictest GDPR requirements. The following must be implemented:

1. **Lawful basis for processing** – explicit consent required for health data; consent must be freely given, specific, informed, and unambiguous
2. **Privacy policy** – clear explanation of what data is collected, why, how long it's kept, and who has access
3. **Data Processing Agreement (DPA)** – required with all third-party processors (OpenAI, ElevenLabs, cloud hosting)
4. **Right to access** – users must be able to export all their data
5. **Right to erasure** – users must be able to delete all their data permanently
6. **Data minimisation** – only collect data that is necessary
7. **Storage limitation** – define and enforce data retention periods
8. **Data breach procedures** – 72-hour notification requirement to ICO for breaches
9. **Data Protection Impact Assessment (DPIA)** – mandatory for high-risk processing like health data

**Important:** OpenAI's data processing terms and data residency options should be reviewed carefully. Consider whether conversation data sent to OpenAI constitutes a transfer outside the EU and ensure appropriate safeguards are in place. Consider this for Elevenlabs and any alternatives also.

## Security Architecture

Given the sensitive nature of the data, security must be built into every layer:

### Encryption Requirements
1. **In transit:** TLS 1.3 for all connections (Unity to backend, backend to external APIs)
2. **At rest:** AES-256 encryption for all stored conversation data
3. **Key management:** Use a dedicated key management service (AWS KMS, Azure Key Vault, or HashiCorp Vault)

### Infrastructure Security
• Host in EU data centres only (for GDPR compliance)
• Network isolation – database should not be publicly accessible
• Web Application Firewall (WAF) to protect against common attacks
• Regular security audits and penetration testing
• Automated vulnerability scanning

### Access Controls
• Role-based access control (RBAC) for any admin functions
• Audit logging of all data access
• Principle of least privilege – staff only access what they need

## Recommended Architecture

| Layer | Components & Recommendations |
|-------|------------------------------|
| **Client** | Unity Application (existing) – communicates only with your backend, never directly with OpenAI/ElevenLabs |
| **Authentication** | Auth0 or Firebase Auth - handles login, MFA, password reset, session tokens |
| **API Gateway** | Custom backend (Node.js/Python) or managed (AWS API Gateway) - routes requests, validates tokens, enforces rate limits |
| **Application Layer** | Backend service - manages conversation context, generates summaries, handles safeguarding logic, proxies AI requests |
| **Database** | PostgreSQL (encrypted) hosted in EU - stores users, conversations, preferences |
| **External Services** | OpenAI API, ElevenLabs API - accessed only from backend, never from client |

## Implementation Roadmap

We recommend a phased approach to reduce risk and allow for testing at each stage:

### Phase 1: Foundation (4-6 weeks)
1. Set up cloud infrastructure in EU region
2. Implement authentication service integration
3. Create API gateway to proxy OpenAI/ElevenLabs requests
4. Update Unity app to authenticate and use new API endpoints
5. Basic security audit

### Phase 2: Data Persistence (3-4 weeks)
1. Set up encrypted PostgreSQL database
2. Implement conversation storage and retrieval
3. Build conversation summarisation for context management
4. Implement data export functionality (GDPR right to access)
5. Implement account deletion functionality (GDPR right to erasure)

### Phase 3: Compliance & Hardening (2-3 weeks)
1. Complete Data Protection Impact Assessment (DPIA)
2. Finalise privacy policy and consent flows
3. Sign Data Processing Agreements with all processors
4. Security penetration testing
5. Implement monitoring and alerting

## Budget Considerations

Ongoing costs will include (as an example - not definitive):

• **Cloud hosting:** £200-500/month depending on scale (AWS, Azure, or GCP)
• **Authentication service:** Free tier available for <7,000 users (Auth0), then £20-200/month
• **Database:** £50-150/month for managed PostgreSQL
• **OpenAI API:** Variable based on usage (currently passed through)
• **ElevenLabs API:** Variable based on usage (currently passed through)
• **Security/compliance:** Annual penetration testing (£2,000-5,000), ongoing monitoring tools

## Recommended Next Steps

• Engage a backend developer or agency with experience in healthcare/mental health applications and GDPR compliance
• Consult with a data protection specialist to review the proposed architecture and ensure compliance
• Review OpenAI and ElevenLabs terms regarding health data and data processing agreements
• Define data retention policy - how long should conversations be kept?
• Consider clinical governance - will there be professional oversight of flagged safeguarding content?

---

*For questions about this document or the technical implementation, please contact Reflex Arc.*