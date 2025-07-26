# Study Buddy - AI-Powered Personalized Learning Platform

This project explores how AI can be integrated into the education sector to create a personalized learning experience for students by adapting to their individual learning styles using data (e.g., student performance, preferences, and behavior) to tailor learning materials, recommend resources, and provide feedback in real-time.

## Features

### 🎯 Core Features
- **Adaptive Learning Engine**: AI algorithms that adapt to individual learning styles and pace
- **Real-time Performance Analytics**: Track progress and identify areas for improvement
- **Personalized Content Recommendations**: AI-powered suggestions for study materials and resources
- **Interactive Learning Modules**: Engaging content delivery with various learning formats
- **Smart Assessment System**: Adaptive quizzes that adjust difficulty based on performance
- **Learning Style Detection**: Automatic identification of visual, auditory, kinesthetic, and reading/writing preferences

### 🤖 AI-Powered Features
- **Natural Language Processing**: Chat with your AI study companion
- **Content Analysis**: Automatic categorization and difficulty assessment of study materials
- **Progress Prediction**: ML models to forecast learning outcomes
- **Intelligent Scheduling**: Optimized study plans based on individual patterns
- **Automated Feedback**: Real-time suggestions and corrections

### 📊 Analytics & Insights
- **Learning Dashboard**: Visual representation of progress and performance
- **Weakness Identification**: AI-powered analysis of knowledge gaps
- **Study Pattern Analysis**: Insights into optimal learning times and methods
- **Comparative Analytics**: Benchmarking against similar learners (anonymized)

## Technology Stack

### Backend
- **Python 3.9+** with FastAPI for high-performance API
- **PostgreSQL** for structured data storage
- **Redis** for caching and session management
- **SQLAlchemy** for database ORM
- **Scikit-learn & TensorFlow** for machine learning models
- **OpenAI API** for advanced language processing
- **Celery** for background task processing

### Mobile Frontend
- **React Native** with TypeScript for cross-platform mobile development
- **Expo** for rapid development and deployment
- **React Navigation** for mobile navigation
- **NativeBase** or **React Native Elements** for UI components
- **React Native Chart Kit** for data visualization
- **Socket.io** for real-time updates

### AI & Machine Learning
- **Natural Language Processing**: OpenAI GPT for content analysis and chat
- **Recommendation System**: Collaborative filtering with content-based recommendations
- **Learning Style Classification**: ML models for pattern recognition
- **Performance Prediction**: Time series analysis for progress forecasting

## Project Structure

```
study-buddy/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── api/           # API routes
│   │   ├── ml/            # Machine learning models
│   │   └── utils/         # Utility functions
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── mobile/                # React Native mobile app
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── screens/       # Mobile screens
│   │   ├── navigation/    # Navigation configuration
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   ├── types/         # TypeScript definitions
│   │   ├── utils/         # Utility functions
│   │   └── store/         # State management (Redux/Zustand)
│   ├── assets/            # Images, fonts, etc.
│   └── package.json       # React Native dependencies
├── data/                  # Sample data and datasets
├── docs/                  # Documentation
└── docker-compose.yml     # Development environment setup
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- React Native CLI or Expo CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd study-buddy
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Mobile App Setup**
   ```bash
   cd mobile
   npm install
   # For iOS (macOS only)
   cd ios && pod install && cd ..
   ```

4. **Environment Configuration**
   ```bash
   cp backend/.env.example backend/.env
   cp mobile/.env.example mobile/.env
   # Edit the .env files with your configuration
   ```

5. **Database Setup**
   ```bash
   cd backend
   alembic upgrade head
   python scripts/seed_data.py
   ```

6. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload --port 8000

   # Terminal 2: Mobile App
   cd mobile
   # For Expo
   npx expo start
   # For React Native CLI
   npx react-native start
   ```

7. **Run Mobile App**
   ```bash
   # Android
   npx react-native run-android
   # or for Expo
   npx expo run:android

   # iOS (macOS only)
   npx react-native run-ios
   # or for Expo
   npx expo run:ios
   ```

8. **Access the Application**
   - Mobile App: On your device/emulator
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Key Components

### Learning Engine
The core AI engine that processes student data to provide personalized learning experiences:
- **Data Collection**: Tracks user interactions, performance metrics, and learning patterns
- **Style Analysis**: Identifies individual learning preferences through behavior analysis
- **Content Adaptation**: Dynamically adjusts content presentation based on learner profile
- **Progress Optimization**: Continuously refines learning paths for maximum effectiveness

### Assessment System
Intelligent assessment that adapts to student performance:
- **Adaptive Questioning**: Questions adjust in real-time based on responses
- **Comprehensive Analytics**: Detailed breakdown of strengths and weaknesses
- **Predictive Scoring**: ML models predict performance on future assessments
- **Automated Feedback**: Instant, personalized feedback and study recommendations

### Recommendation Engine
AI-powered system for suggesting optimal learning resources:
- **Content Matching**: Aligns materials with learning objectives and style
- **Difficulty Progression**: Ensures appropriate challenge level
- **Multi-modal Resources**: Recommends videos, articles, interactive content, and exercises
- **Peer Learning**: Suggests study groups and collaborative opportunities

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Phase 1: Core learning engine and basic UI
- [ ] Phase 2: Advanced AI features and personalization
- [ ] Phase 3: Advanced mobile features (offline sync, push notifications)
- [ ] Phase 4: Integration with educational platforms
- [ ] Phase 5: Advanced analytics and reporting

## Support

For support, email support@studybuddy.ai or join our [Discord community](https://discord.gg/studybuddy).