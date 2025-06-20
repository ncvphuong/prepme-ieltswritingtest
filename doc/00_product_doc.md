# IELTS Writing Test Preparation Platform
## Product Document v1.0

---

## 1. Product Overview

### 1.1 Vision
Provide a comprehensive digital platform for IELTS Writing test preparation, offering personalized practice experiences with AI-powered feedback to help students achieve their target band scores.

### 1.2 Mission
To democratize access to high-quality IELTS Writing preparation through intelligent practice sessions and detailed feedback, enabling students worldwide to improve their writing skills effectively.

### 1.3 Target Audience
- **Primary**: IELTS test candidates preparing for Academic and General Training modules
- **Secondary**: English language teachers and tutors seeking practice materials
- **Tertiary**: Educational institutions offering IELTS preparation courses

---

## 2. Core Features

### 2.1 Practice Test Library
- **600+ Writing Tasks**: Comprehensive collection covering both Task 1 and Task 2
- **Academic Module**: 
  - Task 1: Data interpretation (graphs, charts, diagrams, processes)
  - Task 2: Essay writing (argumentative, discussion, problem-solution)
- **General Training Module**:
  - Task 1: Letter writing (formal, semi-formal, informal)
  - Task 2: Essay writing (opinion, discussion, problem-solution)
- **Topic Diversity**: Wide range of subjects including education, technology, environment, health, social issues

### 2.2 Intelligent Assessment System
- **AI-Powered Marking**: Integration with Claude SDK for automated scoring
- **IELTS Band Scoring**: Accurate assessment based on official IELTS criteria
- **Four Assessment Criteria**:
  - Task Achievement/Response
  - Coherence and Cohesion
  - Lexical Resource
  - Grammatical Range and Accuracy

### 2.3 Detailed Feedback & Improvement
- **Comprehensive Reports**: Overall band score with criterion-specific breakdown
- **Inline Comments**: Contextual feedback directly within the text
- **Improvement Suggestions**: Specific recommendations for enhancement
- **Progress Tracking**: Historical performance analysis and improvement trends

### 2.4 Subscription & Usage Management
- **Flexible Subscription Plans**: Multiple pricing tiers to suit different needs
- **Usage Tracking**: Real-time monitoring of test feedback consumption
- **Transparent Billing**: Clear usage dashboards and billing history
- **Simple Payment Processing**: Secure Stripe integration with payment links

### 2.5 User Experience Features
- **Practice Selection**: Filter by module, task type, topic, and difficulty
- **Timed Practice**: Realistic test conditions with countdown timers
- **Draft Saving**: Auto-save functionality for incomplete responses
- **Performance Dashboard**: Visual progress tracking and statistics

---

## 3. User Stories & Workflows

### 3.1 Primary User Journey
1. **Registration & Profile Setup**
   - User creates account with target band score
   - Selects module type (Academic/General Training)
   - Chooses subscription plan based on needs
   - Completes payment through Stripe

2. **Practice Selection**
   - Browse practice library by filters
   - Select specific writing task
   - Review task instructions and requirements
   - Check remaining feedback credits

3. **Writing Session**
   - Complete writing task within time limit
   - Use built-in text editor with word count
   - Save drafts and submit final response

4. **Feedback & Review**
   - Receive AI-generated assessment and band score (deducts from subscription)
   - Review inline comments and suggestions
   - Analyze performance across four criteria
   - Plan next practice session

### 3.2 Secondary Workflows
- **Progress Monitoring**: Track improvement over time
- **Weak Area Focus**: Practice specific skills based on feedback
- **Mock Test Mode**: Full test simulation experience
- **Subscription Management**: Upgrade/downgrade plans, view billing history
- **Usage Monitoring**: Track feedback consumption and remaining credits

---

## 4. Technical Architecture

### 4.1 Technology Stack
- **Backend**: Python Django Framework
- **Database**: PostgreSQL
- **AI Integration**: Claude SDK (Anthropic)
- **Payment Processing**: Stripe API with payment links and webhooks
- **Frontend**: Django Templates with modern CSS/JavaScript
- **Deployment**: Gunicorn

### 4.2 System Architecture
```
                                                           
   Frontend             Django API           AI Service    
   (Templates)   �  �   (Backend)     �  �   (Claude SDK)  
                                                           
                              
                              �
                                     
                       PostgreSQL    
                       (Database)    
                                     
```

### 4.3 Core Components
- **User Management**: Authentication, profiles, progress tracking
- **Practice Engine**: Task delivery, submission handling, timer management
- **Assessment Service**: Claude SDK integration, scoring algorithms
- **Subscription System**: Plan management, usage tracking, billing integration
- **Payment Processing**: Stripe integration, webhook handling, transaction management
- **Content Management**: Practice library, categorization, metadata
- **Analytics Module**: Performance tracking, reporting, insights

---

## 5. Database Schema Overview

### 5.1 Core Models
- **User**: Profile, preferences, target scores
- **Practice**: Task content, type, difficulty, topics
- **Submission**: User responses, timestamps, status
- **Assessment**: Scores, feedback, criteria breakdown
- **Progress**: Historical performance, improvement tracking
- **SubscriptionPlan**: Plan details, pricing, test limits
- **UserSubscription**: Active subscriptions, usage tracking
- **Payment**: Transaction history, Stripe integration
- **UsageTracking**: Detailed usage monitoring

### 5.2 Key Relationships
- User → Submissions (One-to-Many)
- User → Subscriptions (One-to-Many)
- Subscription → Payments (One-to-Many)
- Submission → Assessment (One-to-One)
- Assessment → Usage Tracking (One-to-One)
- Practice → Submissions (One-to-Many)
- User → Progress (One-to-Many)

---

## 6. Success Metrics

### 6.1 User Engagement
- Daily/Weekly active users
- Average session duration
- Practice completion rates
- Return user percentage

### 6.2 Learning Outcomes
- Band score improvement over time
- Weak area identification accuracy
- User satisfaction with feedback quality
- Target score achievement rate

### 6.3 Business Performance
- Monthly recurring revenue (MRR)
- Customer acquisition cost (CAC)
- Customer lifetime value (CLV)
- Subscription churn rate
- Average revenue per user (ARPU)
- Conversion rate from trial to paid

### 6.4 Technical Performance
- Response time for AI assessment
- System uptime and availability
- Error rates and resolution time
- Scalability metrics
- Payment processing success rate

---

## 7. Development Phases

### Phase 1: MVP (Minimum Viable Product)
- Basic user authentication
- Core practice library (100 tasks)
- Simple AI integration
- Basic feedback system
- Subscription system with Stripe integration
- Usage tracking and limits

### Phase 2: Enhanced Features
- Comprehensive practice library (600 tasks)
- Advanced feedback with inline comments
- Progress tracking dashboard
- Improved UI/UX
- Advanced subscription management
- Payment history and billing

### Phase 3: Advanced Analytics
- Detailed performance analytics
- Personalized recommendations
- Mock test simulations
- Revenue analytics dashboard
- Advanced usage insights

---

## 8. Technical Considerations

### 8.1 Scalability
- Database optimization for concurrent users
- Caching strategies for frequently accessed content
- Load balancing for high-traffic periods

### 8.2 Security
- Secure user authentication
- Data encryption at rest and in transit
- API rate limiting
- Input validation and sanitization

### 8.3 Integration Requirements
- Claude SDK setup and configuration
- Error handling for AI service failures
- Fallback mechanisms for service disruptions
- Cost optimization for API usage
- Stripe webhook security and reliability
- Payment processing error handling
- Subscription lifecycle management

---

## 9. Future Enhancements

### 9.1 Advanced Features
- Speaking test preparation integration
- Peer review and collaboration features
- Mobile application development
- Multi-language support

### 9.2 AI Improvements
- More sophisticated feedback algorithms
- Personalized learning path recommendations
- Predictive scoring for practice improvement
- Advanced natural language processing

---

## 10. Subscription Plans & Pricing

### 10.1 Pricing Strategy
The platform operates on a subscription-based model with transparent, usage-based pricing:

### 10.2 Available Plans
- **Basic Monthly**: $19/month - 40 AI feedback sessions
- **Pro Monthly**: $39/month - 99 AI feedback sessions  
- **Basic 3-Month**: $54 (save 5%) - 40 sessions/month for 3 months
- **Pro 3-Month**: $108 (save 8%) - 99 sessions/month for 3 months
- **Basic 6-Month**: $99 (save 13%) - 40 sessions/month for 6 months
- **Pro 6-Month**: $198 (save 15%) - 99 sessions/month for 6 months

### 10.3 Payment Processing
- **Stripe Integration**: Secure payment processing with payment links
- **Webhook Handling**: Real-time subscription status updates
- **Usage Enforcement**: Automatic tracking and limit enforcement
- **Billing Transparency**: Clear usage dashboards and billing history

---

## 11. Conclusion

This IELTS Writing Test Preparation Platform represents a comprehensive solution for students seeking to improve their writing skills through intelligent practice and feedback. By leveraging Django's robust framework, PostgreSQL's reliability, Claude's advanced AI capabilities, and Stripe's secure payment processing, the platform will provide an effective, scalable, and financially sustainable learning experience.

The subscription-based model ensures sustainable revenue while providing clear value to users through unlimited practice opportunities and AI-powered feedback within their chosen plan limits. The phased development approach ensures rapid time-to-market while allowing for continuous improvement and feature expansion based on user feedback and market demands.

---

## Appendix A: Feature Clarifications

### Progress Dashboard vs Practice History

The platform includes two distinct features that serve different purposes in the user journey:

#### **Practice History** (`/practice/history/`)
- **Purpose**: Chronological record-keeping and session management
- **Focus**: "What you did" - comprehensive log of all practice sessions
- **Content**:
  - Complete list of all practice sessions with timestamps
  - Task details (title, code, module type, task number)
  - Submission status (draft, submitted, assessed)
  - Quick access to restart tasks or view results
  - Search and filter functionality by date, task type, status
  - Basic metrics like word count and submission date

#### **Progress Dashboard** (`/progress/dashboard/`)
- **Purpose**: Performance analytics and improvement tracking
- **Focus**: "How you're progressing" - insights and trends analysis
- **Content**:
  - Score trends over time with interactive charts and graphs
  - Performance analysis by IELTS criteria (Task Achievement, Coherence & Cohesion, Lexical Resource, Grammar)
  - Weak areas identification with targeted improvement suggestions
  - Goal tracking (target band score vs. current performance trajectory)
  - Achievement system with milestones and streaks
  - Comparative analysis showing improvement patterns
  - Personalized recommendations for next practice sessions
  - Study statistics (total practice time, sessions per week, consistency metrics)

#### **Key Differences**:
1. **Data Presentation**: Practice History shows raw chronological data; Progress Dashboard shows processed analytics
2. **User Intent**: History for reviewing past work; Progress for understanding improvement trajectory
3. **Actionability**: History enables task repetition; Progress guides learning strategy
4. **Time Perspective**: History is retrospective; Progress is forward-looking with predictions
5. **Cognitive Load**: History is simple browsing; Progress requires analysis and interpretation

Both features complement each other: users check Practice History to see what they've done and use Progress Dashboard to understand how to improve their performance systematically.