# LiveKit Docs

> LiveKit is an open source platform for developers building realtime media applications. It makes it easy to integrate audio, video, text, data, and AI models while offering scalable realtime infrastructure built on top of WebRTC.

## Overview

LiveKit contains these primary components:

- [Open source WebRTC SFU](https://github.com/livekit/livekit), with a hosted global mesh version available as [LiveKit Cloud](https://cloud.livekit.io)
- [Open source AI Agents Framework](https://github.com/livekit/agents) for building realtime and Voice AI agents in Python (Node.js beta also [available](https://github.com/livekit/agents-js))
- [Realtime SDKs](https://docs.livekit.io/home/client/connect.md) to make it easy to add realitme audio, video, and data to your apps (available for Web, iOS, Android, Flutter, React Native, Unity, Python, Node.js, Rust, and more))
- [Telephony integration](https://docs.livekit.io/sip.md) built on SIP for integrating telephony into LiveKit rooms

For greater detail, see [Intro to LiveKit](https://docs.livekit.io/home/get-started/intro-to-livekit.md).

The following document is a comprehensive list of all available documentation and examples for LiveKit.

## Home

### Get Started

- [Intro to LiveKit](https://docs.livekit.io/home/get-started/intro-to-livekit.md): An overview of the LiveKit ecosystem.
- [Rooms, participants, and tracks](https://docs.livekit.io/home/get-started/api-primitives.md): Guide to the core API primitives in LiveKit.
- [Authentication](https://docs.livekit.io/home/get-started/authentication.md): Learn how to authenticate your users to LiveKit sessions.

### CLI

- [Installing CLI](https://docs.livekit.io/home/cli/cli-setup.md): Install the LiveKit CLI and test your setup using an example frontend application.
- [Bootstrapping an application](https://docs.livekit.io/home/cli/templates.md): Create and initialize an app from a convenient set of templates.

### LiveKit SDKs

- [Connecting to LiveKit](https://docs.livekit.io/home/client/connect.md): Learn how to connect with realtime SDKs.

#### Realtime media

- [Overview](https://docs.livekit.io/home/client/tracks.md): Audio and video media exchange between participants.
- [Camera & microphone](https://docs.livekit.io/home/client/tracks/publish.md): Publish realtime audio and video from any device.
- [Screen sharing](https://docs.livekit.io/home/client/tracks/screenshare.md): Publish your screen with LiveKit.
- [Subscribing to tracks](https://docs.livekit.io/home/client/tracks/subscribe.md): Play and render realtime media tracks in your application.
- [Noise & echo cancellation](https://docs.livekit.io/home/client/tracks/noise-cancellation.md): Achieve crystal-clear audio for video conferencing and voice AI.
- [End-to-end encryption](https://docs.livekit.io/home/client/tracks/encryption.md): Secure your realtime media tracks with E2EE.
- [Codecs & more](https://docs.livekit.io/home/client/tracks/advanced.md): Advanced audio and video topics.

#### Realtime text & data

- [Overview](https://docs.livekit.io/home/client/data.md): Exchange text, files, and custom data between participants.
- [Sending text](https://docs.livekit.io/home/client/data/text-streams.md): Use text streams to send any amount of text between participants.
- [Sending files & bytes](https://docs.livekit.io/home/client/data/byte-streams.md): Use byte streams to send files, images, or any other kind of data between participants.
- [Remote method calls](https://docs.livekit.io/home/client/data/rpc.md): Use RPC to execute custom methods on other participants in the room and await a response.
- [Data packets](https://docs.livekit.io/home/client/data/packets.md): Low-level API for high frequency or advanced use cases.

#### State synchronization

- [Overview](https://docs.livekit.io/home/client/state.md)
- [Participant attributes](https://docs.livekit.io/home/client/state/participant-attributes.md): A key-value store for per-participant state.
- [Room metadata](https://docs.livekit.io/home/client/state/room-metadata.md): Share application-specific state with all participants.
- [Handling events](https://docs.livekit.io/home/client/events.md): Observe and respond to events in the LiveKit SDK.

#### Platform-specific quickstarts

- [Overview](https://docs.livekit.io/home/quickstarts.md)
- [Next.js](https://docs.livekit.io/home/quickstarts/nextjs.md): Get started with LiveKit and Next.js
- [React](https://docs.livekit.io/home/quickstarts/react.md): Get started with LiveKit and React.
- [JavaScript](https://docs.livekit.io/home/quickstarts/javascript.md): Get started with LiveKit and JavaScript
- [Unity (WebGL)](https://docs.livekit.io/home/quickstarts/unity-web.md): Get started with LiveKit and Unity (WebGL)
- [Swift](https://docs.livekit.io/home/quickstarts/swift.md): Get started with LiveKit on iOS using SwiftUI
- [Android (Compose)](https://docs.livekit.io/home/quickstarts/android-compose.md): Get started with LiveKit and Android using Jetpack Compose
- [Android](https://docs.livekit.io/home/quickstarts/android.md): Get started with LiveKit and Android
- [Flutter](https://docs.livekit.io/home/quickstarts/flutter.md): Get started with LiveKit and Flutter
- [React Native](https://docs.livekit.io/home/quickstarts/react-native.md): Get started with LiveKit and React Native
- [Expo](https://docs.livekit.io/home/quickstarts/expo.md): Get started with LiveKit and Expo on React Native

### Server APIs

- [Token generation](https://docs.livekit.io/home/server/generating-tokens.md): Generate tokens for your frontend
- [Room management](https://docs.livekit.io/home/server/managing-rooms.md): Create, list, and delete Rooms from your backend server.
- [Participant management](https://docs.livekit.io/home/server/managing-participants.md): List, remove, and mute from your backend server.
- [Webhooks](https://docs.livekit.io/home/server/webhooks.md): Configure LiveKit to notify your server when room events take place.

### Recording & Composition

- [Overview](https://docs.livekit.io/home/egress/overview.md): Use LiveKit's egress service to record or livestream a room.
- [Composite & web recordings](https://docs.livekit.io/home/egress/composite-recording.md): LiveKit web-based recorder gives you flexible compositing options
- [Recording participants](https://docs.livekit.io/home/egress/participant.md): Record participants individually with the Egress API.
- [Recording individual tracks](https://docs.livekit.io/home/egress/track.md): Track egress allows you export a single track without transcoding.
- [Output and streaming options](https://docs.livekit.io/home/egress/outputs.md): Export content anywhere, in any format.
- [Auto Egress](https://docs.livekit.io/home/egress/autoegress.md): Automatically start recording with a room.
- [Custom recording templates](https://docs.livekit.io/home/egress/custom-template.md): Create your own recording layout to use with Room Composite Egress.
- [Egress API](https://docs.livekit.io/home/egress/api.md): Use LiveKit's egress service to record or livestream a Room.
- [Examples](https://docs.livekit.io/home/egress/examples.md): Usage examples for Egress APIs.

### Stream ingest

- [Overview](https://docs.livekit.io/home/ingress/overview.md): Use LiveKit's ingress service to bring live streams from non-WebRTC sources into LiveKit rooms.
- [Encoder configuration](https://docs.livekit.io/home/ingress/configure-streaming-software.md): How to configure streaming software to work with LiveKit Ingress.

### Cloud

- [Overview](https://docs.livekit.io/home/cloud.md): The fully-managed, globally distributed LiveKit deployment option.
- [Architecture](https://docs.livekit.io/home/cloud/architecture.md): LiveKit Cloud gives you the flexibility of LiveKit's WebRTC stack, combined with global, CDN-scale infrastructure offering 99.99% uptime.
- [Sandbox](https://docs.livekit.io/home/cloud/sandbox.md): Rapidly prototype your apps and share them with others, cutting out the boilerplate.
- [Quotas & limits](https://docs.livekit.io/home/cloud/quotas-and-limits.md): Guide to the quotas and limits for LiveKit Cloud plans.
- [Billing](https://docs.livekit.io/home/cloud/billing.md): Learn how LiveKit Cloud billing works.
- [Configuring firewalls](https://docs.livekit.io/home/cloud/firewall.md): Learn how to configure firewalls for LiveKit Cloud.
- [Analytics API](https://docs.livekit.io/home/cloud/analytics-api.md): Get information about your LiveKit sessions and participants
- [Enhanced noise cancellation](https://docs.livekit.io/home/cloud/noise-cancellation.md): LiveKit Cloud offers AI-powered noise cancellation for realtime audio.

### Self-hosting

- [Running locally](https://docs.livekit.io/home/self-hosting/local.md): This will get a LiveKit instance up and running, ready to receive audio and video streams from participants.
- [Deployment overview](https://docs.livekit.io/home/self-hosting/deployment.md): WebRTC servers can be tricky to deploy because of their use of UDP ports and having to know their own public IP address. This guide will help you get a secure LiveKit deployment up and running.
- [Virtual machine](https://docs.livekit.io/home/self-hosting/vm.md): This guide helps you to set up a production-ready LiveKit server on a cloud virtual machine.
- [Kubernetes](https://docs.livekit.io/home/self-hosting/kubernetes.md): Deploy LiveKit to Kubernetes.
- [Distributed multi-region](https://docs.livekit.io/home/self-hosting/distributed.md): LiveKit is architected to be distributed, with homogeneous instances running across many servers. In distributed mode, Redis is required as shared data store and message bus.
- [Firewall configuration](https://docs.livekit.io/home/self-hosting/ports-firewall.md): Reference for ports and suggested firewall rules for LiveKit.
- [Benchmarks](https://docs.livekit.io/home/self-hosting/benchmark.md): Guide to load-testing and benchmarking your LiveKit installation.
- [Egress](https://docs.livekit.io/home/self-hosting/egress.md): The Egress service uses redis messaging queues to load balance and communicate with your LiveKit server.
- [Ingress](https://docs.livekit.io/home/self-hosting/ingress.md): The Ingress service uses Redis messaging queues to communicate with your LiveKit server.
- [SIP server](https://docs.livekit.io/home/self-hosting/sip-server.md): Setting up and configuring a self-hosted SIP server for LiveKit telephony apps.

## Agents

### Getting started

- [Introduction](https://docs.livekit.io/agents.md): Realtime framework for production-grade multimodal and voice AI agents.
- [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md): Build a simple voice assistant with Python in less than 10 minutes.
- [Telephony integration](https://docs.livekit.io/agents/start/telephony.md): Enable your voice AI agent to make and receive phone calls.
- [Web & mobile frontends](https://docs.livekit.io/agents/start/frontend.md): Bring your agent to life through a web or mobile app.
- [Agents playground](https://docs.livekit.io/agents/start/playground.md): A virtual workbench to test your multimodal AI agent.
- [Migrating from v0.x](https://docs.livekit.io/agents/start/v0-migration.md): Migrate your Python-based agents from version v0.x to 1.0.

### Building voice agents

- [Overview](https://docs.livekit.io/agents/build.md): In-depth guide to voice AI with LiveKit Agents.
- [Workflows](https://docs.livekit.io/agents/build/workflows.md): How to model repeatable, accurate tasks with multiple agents.
- [Agent speech & audio](https://docs.livekit.io/agents/build/audio.md): Speech and audio capabilities for LiveKit agents.
- [Vision](https://docs.livekit.io/agents/build/vision.md): Enhance your agent with visual understanding from images and live video.
- [Tool definition & use](https://docs.livekit.io/agents/build/tools.md): Let your agents call external tools and more.
- [Pipeline nodes & hooks](https://docs.livekit.io/agents/build/nodes.md): Learn how to customize the behavior of your agent with nodes and hooks in the voice pipeline.
- [Text & transcriptions](https://docs.livekit.io/agents/build/text.md): Integrate realtime text features into your agent.

#### Turn detection & interruptions

- [Overview](https://docs.livekit.io/agents/build/turns.md): Guide to managing conversation turns in voice AI.
- [Turn detector plugin](https://docs.livekit.io/agents/build/turns/turn-detector.md): Open-weights model for contextually-aware voice AI turn detection.
- [Silero VAD plugin](https://docs.livekit.io/agents/build/turns/vad.md): High-performance voice activity detection for LiveKit Agents.
- [External data & RAG](https://docs.livekit.io/agents/build/external-data.md): Best practices for adding context and taking external actions.
- [Capturing metrics](https://docs.livekit.io/agents/build/metrics.md): Log performance and usage metrics on your agent for debugging and insights.
- [Events & error handling](https://docs.livekit.io/agents/build/events.md): Guides and reference for events and error handling in LiveKit Agents.

### Worker lifecycle

- [Overview](https://docs.livekit.io/agents/worker.md): How the worker coordinates with LiveKit server to manage agent jobs.
- [Agent dispatch](https://docs.livekit.io/agents/worker/agent-dispatch.md): Specifying how and when your agents are assigned to rooms.
- [Job lifecycle](https://docs.livekit.io/agents/worker/job.md): Learn more about the entrypoint function and how to end and clean up LiveKit sessions.
- [Worker options](https://docs.livekit.io/agents/worker/options.md): Learn about the options available for creating a worker.

### Deployment & operations

- [Deploying to production](https://docs.livekit.io/agents/ops/deployment.md): Guide to running LiveKit Agents in a production environment.
- [Session recording & transcripts](https://docs.livekit.io/agents/ops/recording.md): Export session data in video, audio, or text format.

### Partner spotlight

#### OpenAI

- [Overview](https://docs.livekit.io/agents/integrations/openai.md): Build world-class realtime AI apps with OpenAI and LiveKit Agents.
- [Realtime API](https://docs.livekit.io/agents/integrations/realtime/openai.md): How to use the OpenAI Realtime API with LiveKit Agents.
- [OpenAI LLM](https://docs.livekit.io/agents/integrations/llm/openai.md): How to use the OpenAI LLM plugin for LiveKit Agents.
- [OpenAI TTS](https://docs.livekit.io/agents/integrations/tts/openai.md): How to use the OpenAI TTS plugin for LiveKit Agents.
- [OpenAI STT](https://docs.livekit.io/agents/integrations/stt/openai.md): How to use the OpenAI STT plugin for LiveKit Agents.

#### Google

- [Overview](https://docs.livekit.io/agents/integrations/google.md): Build world-class realtime AI apps with Google AI and LiveKit Agents.
- [Gemini Live API](https://docs.livekit.io/agents/integrations/realtime/gemini.md): How to use the Gemini Live API with LiveKit Agents.
- [Gemini LLM](https://docs.livekit.io/agents/integrations/llm/gemini.md): A guide to using Google Gemini with LiveKit Agents.
- [Google Cloud TTS](https://docs.livekit.io/agents/integrations/tts/google.md): How to use the Google Cloud TTS plugin for LiveKit Agents.
- [Google Cloud STT](https://docs.livekit.io/agents/integrations/stt/google.md): How to use the Google Cloud STT plugin for LiveKit Agents.

#### Azure

- [Overview](https://docs.livekit.io/agents/integrations/azure.md): An overview of the Azure AI integrations with LiveKit Agents.
- [Azure AI Speech TTS](https://docs.livekit.io/agents/integrations/tts/azure.md): How to use the Azure Speech TTS plugin for LiveKit Agents.
- [Azure AI Speech STT](https://docs.livekit.io/agents/integrations/stt/azure.md): How to use the Azure Speech STT plugin for LiveKit Agents.
- [Azure OpenAI Realtime API](https://docs.livekit.io/agents/integrations/realtime/azure-openai.md): How to use the Azure OpenAI Realtime API with LiveKit Agents.
- [Azure OpenAI LLM](https://docs.livekit.io/agents/integrations/llm/azure-openai.md): How to use the Azure OpenAI LLM plugin for LiveKit Agents.
- [Azure OpenAI TTS](https://docs.livekit.io/agents/integrations/tts/azure-openai.md): How to use the Azure OpenAI TTS plugin for LiveKit Agents.
- [Azure OpenAI STT](https://docs.livekit.io/agents/integrations/stt/azure-openai.md): How to use the Azure OpenAI STT plugin for LiveKit Agents.

#### AWS

- [Overview](https://docs.livekit.io/agents/integrations/aws.md): An overview of the AWS AI integrations with LiveKit Agents.
- [Amazon Bedrock LLM](https://docs.livekit.io/agents/integrations/llm/aws.md): How to use the Amazon Bedrock LLM plugin for LiveKit Agents.
- [Amazon Polly TTS](https://docs.livekit.io/agents/integrations/tts/aws.md): How to use the Amazon Polly TTS plugin for LiveKit Agents.
- [Amazon Transcribe STT](https://docs.livekit.io/agents/integrations/stt/aws.md): How to use the Amazon Transcribe STT plugin for LiveKit Agents.

#### Groq

- [Overview](https://docs.livekit.io/agents/integrations/groq.md): Ship lightning-fast voice AI with Groq and LiveKit Agents.
- [Groq LLM](https://docs.livekit.io/agents/integrations/llm/groq.md): How to use the Groq LLM plugin for LiveKit Agents.
- [Groq TTS](https://docs.livekit.io/agents/integrations/tts/groq.md): How to use the Groq TTS plugin for LiveKit Agents.
- [Groq STT](https://docs.livekit.io/agents/integrations/stt/groq.md): How to use the Groq STT plugin for LiveKit Agents.
- [Cerebras](https://docs.livekit.io/agents/integrations/cerebras.md): Build voice AI on the world's fastest inference.
- [Llama](https://docs.livekit.io/agents/integrations/llama.md): Build voice AI on open source models from Meta AI.

### Integration guides

- [Overview](https://docs.livekit.io/agents/integrations.md): Guides for integrating supported AI providers into LiveKit Agents.

#### Realtime models

- [Overview](https://docs.livekit.io/agents/integrations/realtime.md): Guides for adding realtime model integrations to your agents.
- [Gemini Live API](https://docs.livekit.io/agents/integrations/realtime/gemini.md): How to use the Gemini Live API with LiveKit Agents.
- [OpenAI Realtime API](https://docs.livekit.io/agents/integrations/realtime/openai.md): How to use the OpenAI Realtime API with LiveKit Agents.
- [Azure OpenAI Realtime API](https://docs.livekit.io/agents/integrations/realtime/azure-openai.md): How to use the Azure OpenAI Realtime API with LiveKit Agents.

#### Large language models (LLM)

- [Overview](https://docs.livekit.io/agents/integrations/llm.md): Guides for adding LLM integrations to your agents.
- [Anthropic](https://docs.livekit.io/agents/integrations/llm/anthropic.md): How to use the Anthropic Claude LLM plugin for LiveKit Agents.
- [Amazon Bedrock](https://docs.livekit.io/agents/integrations/llm/aws.md): How to use the Amazon Bedrock LLM plugin for LiveKit Agents.
- [Cerebras](https://docs.livekit.io/agents/integrations/llm/cerebras.md): How to use the Cerebras inference with LiveKit Agents.
- [DeepSeek](https://docs.livekit.io/agents/integrations/llm/deepseek.md): How to use DeepSeek models with LiveKit Agents.
- [Fireworks](https://docs.livekit.io/agents/integrations/llm/fireworks.md): How to use Fireworks AI Llama models with LiveKit Agents.
- [Google Gemini](https://docs.livekit.io/agents/integrations/llm/gemini.md): A guide to using Google Gemini with LiveKit Agents.
- [Groq](https://docs.livekit.io/agents/integrations/llm/groq.md): How to use the Groq LLM plugin for LiveKit Agents.
- [Letta](https://docs.livekit.io/agents/integrations/llm/letta.md): How to use a Letta agent for your LLM with LiveKit Agents.
- [Ollama](https://docs.livekit.io/agents/integrations/llm/ollama.md): How to run models locally using Ollama with LiveKit Agents.
- [OpenAI](https://docs.livekit.io/agents/integrations/llm/openai.md): How to use the OpenAI LLM plugin for LiveKit Agents.
- [Azure OpenAI](https://docs.livekit.io/agents/integrations/llm/azure-openai.md): How to use the Azure OpenAI LLM plugin for LiveKit Agents.
- [Perplexity](https://docs.livekit.io/agents/integrations/llm/perplexity.md): How to use Perplexity LLM with LiveKit Agents.
- [Telnyx](https://docs.livekit.io/agents/integrations/llm/telnyx.md): How to use Telnyx inference with LiveKit Agents.
- [Together AI](https://docs.livekit.io/agents/integrations/llm/together.md): How to use Together AI Llama models with LiveKit Agents.
- [xAI](https://docs.livekit.io/agents/integrations/llm/xai.md): How to use xAI LLM with LiveKit Agents.

#### Speech-to-text (STT)

- [Overview](https://docs.livekit.io/agents/integrations/stt.md): Guides for adding STT integrations to your agents.
- [AssemblyAI](https://docs.livekit.io/agents/integrations/stt/assemblyai.md): How to use the AssemblyAI STT plugin for LiveKit Agents.
- [Amazon Transcribe](https://docs.livekit.io/agents/integrations/stt/aws.md): How to use the Amazon Transcribe STT plugin for LiveKit Agents.
- [Azure AI Speech](https://docs.livekit.io/agents/integrations/stt/azure.md): How to use the Azure Speech STT plugin for LiveKit Agents.
- [Azure OpenAI](https://docs.livekit.io/agents/integrations/stt/azure-openai.md): How to use the Azure OpenAI STT plugin for LiveKit Agents.
- [Clova](https://docs.livekit.io/agents/integrations/stt/clova.md): How to use the Clova STT plugin for LiveKit Agents.
- [Deepgram](https://docs.livekit.io/agents/integrations/stt/deepgram.md): How to use the Deepgram STT plugin for LiveKit Agents.
- [fal](https://docs.livekit.io/agents/integrations/stt/fal.md): How to use the fal STT plugin for LiveKit Agents.
- [Gladia](https://docs.livekit.io/agents/integrations/stt/gladia.md): How to use the Gladia STT plugin for LiveKit Agents.
- [Google Cloud](https://docs.livekit.io/agents/integrations/stt/google.md): How to use the Google Cloud STT plugin for LiveKit Agents.
- [Groq](https://docs.livekit.io/agents/integrations/stt/groq.md): How to use the Groq STT plugin for LiveKit Agents.
- [OpenAI](https://docs.livekit.io/agents/integrations/stt/openai.md): How to use the OpenAI STT plugin for LiveKit Agents.
- [Speechmatics](https://docs.livekit.io/agents/integrations/stt/speechmatics.md): How to use the Speechmatics STT plugin for LiveKit Agents.

#### Text-to-speech (TTS)

- [Overview](https://docs.livekit.io/agents/integrations/tts.md): Guides for adding TTS integrations to your agents.
- [Amazon Polly](https://docs.livekit.io/agents/integrations/tts/aws.md): How to use the Amazon Polly TTS plugin for LiveKit Agents.
- [Azure AI Speech](https://docs.livekit.io/agents/integrations/tts/azure.md): How to use the Azure Speech TTS plugin for LiveKit Agents.
- [Azure OpenAI](https://docs.livekit.io/agents/integrations/tts/azure-openai.md): How to use the Azure OpenAI TTS plugin for LiveKit Agents.
- [Cartesia](https://docs.livekit.io/agents/integrations/tts/cartesia.md): How to use the Cartesia TTS plugin for LiveKit Agents.
- [Deepgram](https://docs.livekit.io/agents/integrations/tts/deepgram.md): How to use the Deepgram TTS plugin for LiveKit Agents.
- [ElevenLabs](https://docs.livekit.io/agents/integrations/tts/elevenlabs.md): How to use the ElevenLabs TTS plugin for LiveKit Agents.
- [Google Cloud](https://docs.livekit.io/agents/integrations/tts/google.md): How to use the Google Cloud TTS plugin for LiveKit Agents.
- [Groq](https://docs.livekit.io/agents/integrations/tts/groq.md): How to use the Groq TTS plugin for LiveKit Agents.
- [Hume](https://docs.livekit.io/agents/integrations/tts/hume.md): How to use the Hume TTS plugin for LiveKit Agents.
- [Neuphonic](https://docs.livekit.io/agents/integrations/tts/neuphonic.md): How to use the Neuphonic TTS plugin for LiveKit Agents.
- [OpenAI](https://docs.livekit.io/agents/integrations/tts/openai.md): How to use the OpenAI TTS plugin for LiveKit Agents.
- [PlayHT](https://docs.livekit.io/agents/integrations/tts/playai.md): How to use the PlayHT TTS plugin for LiveKit Agents.
- [Resemble AI](https://docs.livekit.io/agents/integrations/tts/resemble.md): How to use the Resemble AI TTS plugin for LiveKit Agents.
- [Rime](https://docs.livekit.io/agents/integrations/tts/rime.md): How to use the Rime TTS plugin for LiveKit Agents.
- [Speechify](https://docs.livekit.io/agents/integrations/tts/speechify.md): How to use the Speechify TTS plugin for LiveKit Agents.

#### Virtual avatars

- [Overview](https://docs.livekit.io/agents/integrations/avatar.md): Guides for adding virtual avatars to your agents.
- [Beyond Presence](https://docs.livekit.io/agents/integrations/avatar/bey.md): How to use the Beyond Presence virtual avatar plugin for LiveKit Agents.
- [bitHuman](https://docs.livekit.io/agents/integrations/avatar/bithuman.md): How to use the bitHuman virtual avatar plugin for LiveKit Agents.
- [Tavus](https://docs.livekit.io/agents/integrations/avatar/tavus.md): How to use the Tavus virtual avatar plugin for LiveKit Agents.

## Telephony

### Getting started

- [Overview](https://docs.livekit.io/sip.md): Connect LiveKit to a telephone system using Session Initiation Protocol (SIP).
- [SIP trunk setup](https://docs.livekit.io/sip/quickstarts/configuring-sip-trunk.md): Guide to setting up SIP trunks for inbound and outbound calls with LiveKit.

### Provider-specific guides

- [Twilio](https://docs.livekit.io/sip/quickstarts/configuring-twilio-trunk.md): Step-by-step instructions for creating inbound and outbound SIP trunks using Twilio.
- [Telnyx](https://docs.livekit.io/sip/quickstarts/configuring-telnyx-trunk.md): Step-by-step instructions for creating inbound and outbound SIP trunks using Telnyx.
- [Plivo](https://docs.livekit.io/sip/quickstarts/configuring-plivo-trunk.md): Step-by-step instructions for creating inbound and outbound SIP trunks using Plivo.

### Accepting calls

- [Workflow](https://docs.livekit.io/sip/accepting-calls.md): Workflow and configuration guide for accepting inbound calls.
- [Inbound trunk](https://docs.livekit.io/sip/trunk-inbound.md): How to create and configure an inbound trunk to accept incoming calls.
- [Dispatch rule](https://docs.livekit.io/sip/dispatch-rule.md): How to create and configure a dispatch rule.
- [Inbound calls with Twilio Voice](https://docs.livekit.io/sip/accepting-calls-twilio-voice.md): How to use LiveKit SIP with TwiML and Twilio conferencing.

### Making calls

- [Workflow](https://docs.livekit.io/sip/making-calls.md): Workflow for making outbound calls.
- [Outbound trunk](https://docs.livekit.io/sip/trunk-outbound.md): How to create and configure a outbound trunk to make outgoing calls.
- [Make outbound calls](https://docs.livekit.io/sip/outbound-calls.md): Create a LiveKit SIP participant to make outbound calls.

### Features

- [DTMF](https://docs.livekit.io/sip/dtmf.md): Sending and receiving DTMF tones.
- [Cold transfer](https://docs.livekit.io/sip/transfer-cold.md): Using the TransferSIPParticipant API for cold transfers.
- [HD voice](https://docs.livekit.io/sip/hd-voice.md): LiveKit SIP supports high fidelity calls by enabling HD voice.

### Reference

- [SIP participant](https://docs.livekit.io/sip/sip-participant.md): Mapping a caller to a SIP participant.
- [SIP API](https://docs.livekit.io/sip/api.md): Use LiveKit's built-in SIP APIs to manage your SIP-based apps.

## Recipes

- **[Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md)**: Create a voice AI agent in less than 10 minutes.

- **[SwiftUI Voice Assistant](https://github.com/livekit-examples/voice-assistant-swift)**: A native iOS, macOS, and visionOS voice AI assistant built in SwiftUI.

- **[Next.js Voice Assistant](https://github.com/livekit-examples/voice-assistant-frontend)**: A web voice AI assistant built with React and Next.js.

- **[Flutter Voice Assistant](https://github.com/livekit-examples/voice-assistant-flutter)**: A cross-platform voice AI assistant app built with Flutter.

- **[React Native Voice Assistant](https://github.com/livekit-examples/voice-assistant-react-native)**: A native voice AI assistant app built with React Native and Expo.

- **[Android Voice Assistant](https://github.com/livekit-examples/android-voice-assistant)**: A native Android voice AI assistant app built with Kotlin and Jetpack Compose.

- **[Medical Office Triage](https://github.com/livekit-examples/python-agents-examples/tree/main/complex-agents/medical_office_triage)**: Agent that triages patients based on symptoms and medical history.

- **[Personal Shopper](https://github.com/livekit-examples/python-agents-examples/tree/main/complex-agents/personal_shopper)**: AI shopping assistant that helps find products based on user preferences.

- **[Restaurant Agent](https://github.com/livekit/agents/blob/main/examples/voice_agents/restaurant_agent.py)**: A restaurant front-of-house agent that can take orders, add items to a shared cart, and checkout.

- **[LivePaint](https://github.com/livekit-examples/livepaint)**: A realtime drawing game where players compete to complete a drawing prompt while being judged by a realtime AI agent.

- **[Push-to-Talk Agent](https://github.com/livekit/agents/blob/main/examples/voice_agents/push_to_talk.py)**: A voice AI agent that uses push-to-talk for controlled multi-participant conversations, only enabling audio input when explicitly triggered.

- **[Background Audio](https://github.com/livekit/agents/blob/main/examples/voice_agents/background_audio.py)**: A voice AI agent with background audio for thinking states and ambiance.

- **[Uninterruptable Agent](https://github.com/livekit-examples/python-agents-examples/tree/main/basics/uninterruptable.py)**: An agent that continues speaking without being interrupted.

- **[Change Language](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-tts/elevenlabs_change_language.py)**: Agent that can switch between different languages during conversation.

- **[TTS Comparison](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-tts/tts_comparison.py)**: Compare different text-to-speech providers side by side.

- **[Transcriber](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-stt/transcriber.py)**: Real-time speech transcription with high accuracy.

- **[Keyword Detection](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-stt/keyword_detection.py)**: Detect specific keywords in speech in real-time.

- **[Using Twilio Voice](https://docs.livekit.io/sip/accepting-calls-twilio-voice.md)**: Use TwiML to accept incoming calls and bridge Twilio conferencing to LiveKit via SIP.

- **[IVR Agent](https://docs.livekit.io/recipes/ivr-navigator.md)**: Build a voice agent that can call external voice lines and respond to IVR flows using DTMF tones.

- **[Company Directory](https://docs.livekit.io/recipes/company-directory.md)**: Build a AI company directory agent. The agent can respond to DTMF tones and voice prompts, then redirect callers.

- **[Phone Caller](https://github.com/livekit-examples/python-agents-examples/tree/main/telephony/make_call)**: Agent that can make outbound phone calls and handle conversations.

- **[SIP Warm Handoff](https://github.com/livekit-examples/python-agents-examples/tree/main/telephony/warm_handoff.py)**: Transfer calls from an AI agent to a human operator seamlessly.

- **[SIP Lifecycle](https://github.com/livekit-examples/python-agents-examples/tree/main/telephony/sip_lifecycle.py)**: Complete lifecycle management for SIP calls.

- **[Answer Incoming Calls](https://github.com/livekit-examples/python-agents-examples/tree/main/telephony/answer_call.py)**: Set up an agent to answer incoming SIP calls.

- **[Survey Caller](https://github.com/livekit-examples/python-agents-examples/tree/main/telephony/survey_caller/)**: Automated survey calling system.

- **[Chain-of-thought agent](https://docs.livekit.io/recipes/chain-of-thought.md)**: Build an agent for chain-of-thought reasoning using the `llm_node` to clean the text before TTS.

- **[LlamaIndex RAG](https://github.com/livekit/agents/tree/main/examples/voice_agents/llamaindex-rag)**: A voice AI agent that uses LlamaIndex for RAG to answer questions from a knowledge base.

- **[LiveKit Docs RAG](https://github.com/livekit-examples/python-agents-examples/tree/main/rag)**: An agent that can answer questions about LiveKit with lookups against the docs website.

- **[Moviefone](https://docs.livekit.io/recipes/moviefone.md)**: This agent uses function calling and the OpenAI API to search for movies and give you realtime information about showtimes.

- **[Context Variables](https://github.com/livekit-examples/python-agents-examples/tree/main/basics/context_variables.py)**: Maintain conversation context across interactions.

- **[Interrupt User](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-llm/interrupt_user.py)**: Example of how to implement user interruption in conversations.

- **[LLM Content Filter](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-llm/llm_powered_content_filter.py)**: Implement content filtering in the `llm_node`.

- **[Simple Content Filter](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-llm/simple_content_filter.py)**: Basic content filtering implementation.

- **[Replacing LLM Output](https://github.com/livekit-examples/python-agents-examples/tree/main/pipeline-llm/replacing_llm_output.py)**: Example of modifying LLM output before processing.

- **[Vision Assistant](https://github.com/livekit-examples/vision-demo)**: A voice AI agent with video input powered by Gemini Live.

- **[Raspberry Pi Transcriber](https://github.com/livekit-examples/python-agents-examples/tree/main/hardware/pi_zero_transcriber.py)**: Run transcription on Raspberry Pi hardware.

- **[Pipeline Translator](https://github.com/livekit-examples/python-agents-examples/tree/main/translators/pipeline_translator.py)**: Implement translation in the processing pipeline.

- **[TTS Translator](https://github.com/livekit-examples/python-agents-examples/tree/main/translators/tts_translator.py)**: Translation with text-to-speech capabilities.

- **[LLM Metrics](https://github.com/livekit-examples/python-agents-examples/tree/main/metrics/metrics_llm.py)**: Track and analyze LLM performance metrics.

- **[STT Metrics](https://github.com/livekit-examples/python-agents-examples/tree/main/metrics/metrics_stt.py)**: Track and analyze speech-to-text performance metrics.

- **[TTS Metrics](https://github.com/livekit-examples/python-agents-examples/tree/main/metrics/metrics_tts.py)**: Track and analyze text-to-speech performance metrics.

- **[VAD Metrics](https://github.com/livekit-examples/python-agents-examples/tree/main/metrics/metrics_vad.py)**: Track and analyze voice activity detection metrics.

- **[Playing Audio](https://github.com/livekit-examples/python-agents-examples/tree/main/basics/playing_audio.py)**: Play audio files during agent interactions.

- **[Sound Repeater](https://github.com/livekit-examples/python-agents-examples/tree/main/basics/repeater.py)**: Simple sound repeating demo for testing audio pipelines.

- **[MCP Agent](https://github.com/livekit-examples/python-agents-examples/tree/main/mcp)**: A voice AI agent with an integrated Model Context Protocol (MCP) server for the LiveKit API.

- **[Speedup Output Audio](https://github.com/livekit/agents/blob/main/examples/voice_agents/speedup_output_audio.py)**: Speed up the audio output of an agent.

- **[Structured Output](https://github.com/livekit/agents/blob/main/examples/voice_agents/structured_output.py)**: Handle structured output from the LLM by overriding the `llm_node` and `tts_node`.

- **[RPC + State Agent](https://github.com/livekit-examples/python-agents-examples/blob/main/rpc/rpc_agent.py)**: Voice agent with a state database updated through tool calling and queryable from the frontend with RPC.

- **[Tavus Avatar Agent](https://github.com/livekit-examples/python-agents-examples/blob/main/avatars/tavus)**: An educational AI agent that uses Tavus to create an interactive study partner.

- **[Rover Teleop](https://github.com/livekit-examples/rover-teleop)**: Build a high performance robot tele-op system using LiveKit.

- **[VR Spatial Video](https://github.com/livekit-examples/spatial-video)**: Stream spatial video from a stereoscopic camera to a Meta Quest using LiveKit.

- **[Echo Agent](https://github.com/livekit/agents/blob/main/examples/primitives/echo-agent.py)**: Echo user audio back to them.

- **[Sync TTS Transcription](https://github.com/livekit/agents/blob/main/examples/other/text-to-speech/sync_tts_transcription.py)**: Uses manual subscription, transcription forwarding, and manually publishes audio output.

---

This document was rendered at 2025-06-07T00:51:54.458Z.
For the latest version of this document, see [https://docs.livekit.io/llms.txt](https://docs.livekit.i