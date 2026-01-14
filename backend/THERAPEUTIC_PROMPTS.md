# Therapeutic Prompt Service Documentation

## Overview

The Therapeutic Prompt Service provides comprehensive, context-aware therapeutic conversation prompts for the AI Therapy Platform. It supports multiple therapeutic approaches, languages, cultural contexts, and includes A/B testing capabilities for continuous improvement.

🏆 Breaking Barriers UK 2026 compliant

## Features

### 1. Multiple Therapeutic Approaches

The service supports 8 evidence-based therapeutic approaches:

- **Cognitive Behavioral Therapy (CBT)**: Focus on thought patterns and behaviors
- **Person-Centered Therapy**: Rogerian approach with unconditional positive regard
- **Mindfulness-Based**: MBSR/MBCT techniques for present-moment awareness
- **Solution-Focused Brief Therapy (SFBT)**: Focus on solutions and strengths
- **Psychodynamic**: Insight-oriented therapy
- **Dialectical Behavioral Therapy (DBT)**: Emotion regulation and distress tolerance
- **Acceptance and Commitment Therapy (ACT)**: Values-based action
- **Trauma-Informed Care**: Safety-first approach for trauma survivors

### 2. Context-Aware Selection

Prompts adapt to different conversation contexts:

- **Initial Session**: Building rapport and establishing trust
- **Ongoing Session**: Regular therapeutic work
- **Crisis Intervention**: Immediate safety and stabilization
- **Closure Session**: Termination and consolidation
- **Check-In**: Brief status updates
- **Emotional Distress**: Extra support and validation
- **Goal Setting**: SMART goals and planning
- **Progress Review**: Celebrating achievements

### 3. Multi-Language Support

Native support for:
- English (en)
- Spanish (es)
- French (fr)
- German (de)

Each language includes culturally appropriate therapeutic phrases and expressions.

### 4. Cultural Sensitivity

Prompts adapt to cultural contexts:

- **Western Individualistic**: Independence and self-actualization
- **Eastern Collectivistic**: Family and community focus
- **Latin American**: Familismo and personalismo values
- **Middle Eastern**: Religious and family honor considerations
- **African**: Community and traditional healing
- **South Asian**: Family obligations and intergenerational dynamics
- **Indigenous**: Traditional healing and historical trauma awareness
- **Neutral**: Universal therapeutic principles

### 5. Safety Guardrails

All prompts include comprehensive safety guidelines:

- Red flag detection (self-harm, suicide, abuse)
- Crisis resource information
- Professional boundary maintenance
- Appropriate escalation protocols
- Confidentiality guidelines

### 6. A/B Testing Framework

Built-in A/B testing for continuous improvement:

- Consistent client-to-version assignment
- Performance tracking and metrics
- Success rate monitoring
- Automatic version selection based on performance

## Usage

### Basic Usage

```python
from backend.src.services.therapeutic_prompt_service import (
    therapeutic_prompt_service,
    PromptSelectionCriteria,
    TherapeuticApproach,
    ConversationContext,
    CulturalContext
)

# Create selection criteria
criteria = PromptSelectionCriteria(
    approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
    context=ConversationContext.INITIAL_SESSION,
    language="en",
    cultural_context=CulturalContext.NEUTRAL
)

# Select prompt
prompt_version, metadata = therapeutic_prompt_service.select_prompt(
    criteria=criteria,
    client_id="client_123",
    enable_ab_testing=True
)

# Use the prompt
system_prompt = prompt_version.prompt_text
```

### Integration with Nova Sonic 2

```python
from backend.src.config.nova_sonic_config import nova_sonic_client

# Create session with therapeutic prompt
session_config = nova_sonic_client.create_session(
    session_id="session_456",
    client_id="client_123",
    language="en",
    approach="cognitive_behavioral",
    context="initial_session",
    cultural_context="neutral"
)

# The session will automatically use the appropriate therapeutic prompt
```

### Adding Custom Prompts

```python
# Add a custom prompt version for A/B testing
version_id = therapeutic_prompt_service.add_prompt_version(
    approach=TherapeuticApproach.COGNITIVE_BEHAVIORAL,
    context=ConversationContext.ONGOING_SESSION,
    language="en",
    cultural_context=CulturalContext.NEUTRAL,
    custom_prompt="Additional therapeutic guidance...",
    metadata={"experiment": "enhanced_cbt_v2"}
)
```

### Updating Performance Metrics

```python
# After a session completes
therapeutic_prompt_service.update_prompt_performance(
    version_id=prompt_version.version_id,
    success=True,
    feedback_score=0.85
)
```

### Getting Analytics

```python
# Get prompt usage analytics
analytics = therapeutic_prompt_service.get_prompt_analytics()

print(f"Total versions: {analytics['total_versions']}")
print(f"Total usage: {analytics['total_usage']}")
print(f"Top performing versions: {analytics['top_performing_versions']}")
```

### Language-Specific Phrases

```python
# Get therapeutic phrases for a language
phrases = therapeutic_prompt_service.get_language_phrases("es")

# Use in conversation
validation_phrase = phrases["validation"][0]  # "Te escucho"
empathy_phrase = phrases["empathy"][0]  # "Eso suena muy difícil"
```

## Prompt Structure

Each prompt consists of:

1. **Base Approach Prompt**: Core therapeutic principles for the approach
2. **Context Addition**: Specific guidance for the conversation context
3. **Cultural Addition**: Cultural sensitivity considerations
4. **Language Note**: Communication in the target language
5. **Safety Guidelines**: Universal safety and red flag detection rules

Example structure:

```
[Base CBT Prompt]
- Help clients identify negative thought patterns
- Guide cognitive restructuring
- Teach coping strategies
...

[Context: Initial Session]
- Build rapport and trust
- Explain confidentiality
- Gather background information
...

[Cultural: Latin American]
- Value familismo (family-centered values)
- Recognize importance of personalismo
- Respect traditional gender roles
...

[Language: Spanish]
Communicate in Spanish with culturally appropriate expressions.

[Safety Guidelines]
CRITICAL SAFETY GUIDELINES:
- NEVER encourage self-harm or violence
- IMMEDIATELY flag red flags
- Provide crisis resources
...
```

## Performance Metrics

The service tracks:

- **Usage Count**: Number of times each prompt version is used
- **Success Rate**: Percentage of successful sessions
- **Performance Score**: Weighted combination of success rate and feedback
- **Connection Quality**: A/B test assignment consistency

## Best Practices

### 1. Always Specify Cultural Context

```python
# Good: Specific cultural context
criteria = PromptSelectionCriteria(
    approach=TherapeuticApproach.PERSON_CENTERED,
    context=ConversationContext.ONGOING_SESSION,
    language="es",
    cultural_context=CulturalContext.LATIN_AMERICAN
)

# Acceptable: Neutral for unknown context
criteria = PromptSelectionCriteria(
    approach=TherapeuticApproach.PERSON_CENTERED,
    context=ConversationContext.ONGOING_SESSION,
    language="es",
    cultural_context=CulturalContext.NEUTRAL
)
```

### 2. Use Crisis Context Appropriately

```python
# Detect crisis situations
if client_mentions_self_harm or client_mentions_suicide:
    criteria = PromptSelectionCriteria(
        approach=TherapeuticApproach.TRAUMA_INFORMED,
        context=ConversationContext.CRISIS_INTERVENTION,
        language=client_language,
        cultural_context=client_cultural_context
    )
```

### 3. Enable A/B Testing for Optimization

```python
# Always provide client_id for A/B testing
prompt_version, metadata = therapeutic_prompt_service.select_prompt(
    criteria=criteria,
    client_id=client_id,  # Important for consistent assignment
    enable_ab_testing=True
)
```

### 4. Update Performance Metrics

```python
# After each session
therapeutic_prompt_service.update_prompt_performance(
    version_id=metadata['version_id'],
    success=session_was_successful,
    feedback_score=client_feedback_score
)
```

## Validation

Run the validation script to test the service:

```bash
python3 backend/validate_therapeutic_prompts.py
```

This validates:
- Service initialization
- Prompt selection for all approaches
- Multi-language support
- Crisis intervention
- Cultural sensitivity
- A/B testing
- Safety guidelines
- Language phrases
- Analytics
- Prompt library content

## Requirements

Validates requirements:
- **3.4**: Therapeutic best practices through system prompts
- **10.7**: Multi-language and cultural adaptation

## Architecture

```
TherapeuticPromptService
├── TherapeuticPromptLibrary
│   ├── BASE_PROMPTS (8 approaches)
│   ├── CONTEXT_ADDITIONS (8 contexts)
│   ├── CULTURAL_ADDITIONS (7 cultures)
│   ├── LANGUAGE_PHRASES (4 languages)
│   └── SAFETY_GUIDELINES (universal)
├── Prompt Version Management
│   ├── Version creation
│   ├── Version selection
│   └── Version deactivation
├── A/B Testing
│   ├── Client assignment
│   ├── Consistent routing
│   └── Performance tracking
└── Analytics
    ├── Usage metrics
    ├── Performance scores
    └── Top performers
```

## Future Enhancements

Potential improvements:
1. Machine learning-based prompt optimization
2. Real-time prompt adaptation based on session progress
3. Additional therapeutic approaches (EMDR, IFS, etc.)
4. More languages (Mandarin, Arabic, Hindi, etc.)
5. Client preference learning
6. Therapist feedback integration
7. Automated prompt generation using LLMs
8. Regional dialect support

## Support

For issues or questions:
- Check the validation script output
- Review the analytics dashboard
- Consult the design document: `.kiro/specs/ai-therapy-platform/design.md`
- Review requirements: `.kiro/specs/ai-therapy-platform/requirements.md`
