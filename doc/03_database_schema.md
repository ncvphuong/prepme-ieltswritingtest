# Database Schema Design
## PostgreSQL Database Structure for IELTS Writing Test Platform

---

## Database Overview

The database schema is designed to support comprehensive IELTS writing practice with AI-powered assessment, progress tracking, subscription management, and personalized learning paths. The schema follows Django ORM conventions and includes proper relationships, indexes, and constraints.

---

## Core Models

### 1. User Management

#### CustomUser Model
**App**: `accounts`
**Purpose**: Extended Django User model with IELTS-specific fields

```sql
CREATE TABLE accounts_customuser (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) UNIQUE NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- IELTS-specific fields
    target_band_score DECIMAL(2,1) CHECK (target_band_score >= 1.0 AND target_band_score <= 9.0),
    current_level VARCHAR(20) DEFAULT 'beginner',
    test_date DATE,
    module_type VARCHAR(20) NOT NULL DEFAULT 'academic' CHECK (module_type IN ('academic', 'general')),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language_background VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customuser_email ON accounts_customuser(email);
CREATE INDEX idx_customuser_module_type ON accounts_customuser(module_type);
CREATE INDEX idx_customuser_target_score ON accounts_customuser(target_band_score);
```

#### UserPreferences Model
**App**: `accounts`
**Purpose**: User preferences and settings

```sql
CREATE TABLE accounts_userpreferences (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    
    -- Practice preferences
    preferred_practice_time INTEGER DEFAULT 60, -- minutes
    auto_save_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    difficulty_preference VARCHAR(20) DEFAULT 'mixed',
    
    -- Display preferences
    theme VARCHAR(10) DEFAULT 'light' CHECK (theme IN ('light', 'dark')),
    font_size VARCHAR(10) DEFAULT 'medium',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    UNIQUE(user_id)
);
```

---

### 2. Practice Content

#### Topic Model
**App**: `practice`
**Purpose**: Categorization of writing tasks by topic

```sql
CREATE TABLE practice_topic (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- 'education', 'technology', 'environment', etc.
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_topic_category ON practice_topic(category);
CREATE INDEX idx_topic_active ON practice_topic(is_active);
```

#### PracticeTask Model
**App**: `practice`
**Purpose**: Individual writing tasks/questions

```sql
CREATE TABLE practice_practicetask (
    id BIGSERIAL PRIMARY KEY,
    
    -- Task identification
    task_code VARCHAR(20) NOT NULL UNIQUE, -- e.g., 'AC_T1_001', 'GT_T2_045'
    title VARCHAR(200) NOT NULL,
    
    -- Task classification
    module_type VARCHAR(20) NOT NULL CHECK (module_type IN ('academic', 'general')),
    task_number INTEGER NOT NULL CHECK (task_number IN (1, 2)),
    difficulty_level VARCHAR(20) DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    
    -- Task content
    instruction TEXT NOT NULL,
    prompt TEXT NOT NULL,
    additional_materials JSONB, -- For charts, graphs, diagrams (Task 1)
    word_limit_min INTEGER NOT NULL DEFAULT 150,
    word_limit_max INTEGER NOT NULL DEFAULT 250,
    time_limit_minutes INTEGER NOT NULL DEFAULT 20,
    
    -- Metadata
    topic_id BIGINT REFERENCES practice_topic(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    average_score DECIMAL(3,1),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_practicetask_module_task ON practice_practicetask(module_type, task_number);
CREATE INDEX idx_practicetask_difficulty ON practice_practicetask(difficulty_level);
CREATE INDEX idx_practicetask_topic ON practice_practicetask(topic_id);
CREATE INDEX idx_practicetask_active ON practice_practicetask(is_active);
```

---

### 3. User Submissions

#### Submission Model
**App**: `practice`
**Purpose**: User's writing submissions

```sql
CREATE TABLE practice_submission (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    task_id BIGINT NOT NULL REFERENCES practice_practicetask(id) ON DELETE CASCADE,
    
    -- Submission content
    content TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    
    -- Session information
    time_spent_seconds INTEGER, -- Actual time spent writing
    session_id VARCHAR(100), -- For tracking multi-part sessions
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'assessed')),
    is_practice_mode BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_submission_user ON practice_submission(user_id);
CREATE INDEX idx_submission_task ON practice_submission(task_id);
CREATE INDEX idx_submission_status ON practice_submission(status);
CREATE INDEX idx_submission_submitted_at ON practice_submission(submitted_at);
```

---

### 4. AI Assessment

#### Assessment Model
**App**: `assessment`
**Purpose**: AI-generated assessments and scores

```sql
CREATE TABLE assessment_assessment (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    submission_id BIGINT NOT NULL REFERENCES practice_submission(id) ON DELETE CASCADE,
    
    -- Overall scores
    overall_band_score DECIMAL(2,1) NOT NULL CHECK (overall_band_score >= 1.0 AND overall_band_score <= 9.0),
    
    -- Criterion-specific scores
    task_achievement_score DECIMAL(2,1) NOT NULL CHECK (task_achievement_score >= 1.0 AND task_achievement_score <= 9.0),
    coherence_cohesion_score DECIMAL(2,1) NOT NULL CHECK (coherence_cohesion_score >= 1.0 AND coherence_cohesion_score <= 9.0),
    lexical_resource_score DECIMAL(2,1) NOT NULL CHECK (lexical_resource_score >= 1.0 AND lexical_resource_score <= 9.0),
    grammar_accuracy_score DECIMAL(2,1) NOT NULL CHECK (grammar_accuracy_score >= 1.0 AND grammar_accuracy_score <= 9.0),
    
    -- AI processing metadata
    ai_model_version VARCHAR(50),
    processing_time_seconds DECIMAL(5,2),
    confidence_score DECIMAL(3,2), -- AI confidence in assessment
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'manual_review')),
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    UNIQUE(submission_id)
);

CREATE INDEX idx_assessment_overall_score ON assessment_assessment(overall_band_score);
CREATE INDEX idx_assessment_status ON assessment_assessment(status);
```

#### Feedback Model
**App**: `assessment`
**Purpose**: Detailed feedback and comments

```sql
CREATE TABLE assessment_feedback (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    assessment_id BIGINT NOT NULL REFERENCES assessment_assessment(id) ON DELETE CASCADE,
    
    -- Feedback content
    criterion VARCHAR(30) NOT NULL CHECK (criterion IN ('task_achievement', 'coherence_cohesion', 'lexical_resource', 'grammar_accuracy', 'overall')),
    feedback_text TEXT NOT NULL,
    strengths TEXT,
    improvements TEXT,
    suggestions TEXT,
    
    -- Inline comments (JSON array of objects with position and comment)
    inline_comments JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_assessment ON assessment_feedback(assessment_id);
CREATE INDEX idx_feedback_criterion ON assessment_feedback(criterion);
```

---

### 5. Progress Tracking

#### ProgressEntry Model
**App**: `progress`
**Purpose**: Track user progress over time

```sql
CREATE TABLE progress_progressentry (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    assessment_id BIGINT NOT NULL REFERENCES assessment_assessment(id) ON DELETE CASCADE,
    
    -- Progress metrics
    band_score_improvement DECIMAL(3,2), -- Improvement from previous attempt
    consistency_score DECIMAL(3,2), -- How consistent scores are
    weak_areas JSONB, -- Array of identified weak areas
    strong_areas JSONB, -- Array of identified strengths
    
    -- Practice statistics
    practice_streak INTEGER DEFAULT 0,
    total_practices INTEGER NOT NULL DEFAULT 1,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_progress_user ON progress_progressentry(user_id);
CREATE INDEX idx_progress_created ON progress_progressentry(created_at);
```

#### UserGoal Model
**App**: `progress`
**Purpose**: User-defined goals and targets

```sql
CREATE TABLE progress_usergoal (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    
    -- Goal details
    goal_type VARCHAR(30) NOT NULL CHECK (goal_type IN ('band_score', 'practice_count', 'consistency', 'skill_improvement')),
    target_value DECIMAL(5,2) NOT NULL,
    current_value DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Goal metadata
    description TEXT,
    target_date DATE,
    is_achieved BOOLEAN NOT NULL DEFAULT FALSE,
    achieved_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usergoal_user ON progress_usergoal(user_id);
CREATE INDEX idx_usergoal_type ON progress_usergoal(goal_type);
```

---

### 6. Subscription & Payment Management

#### SubscriptionPlan Model
**App**: `subscriptions`
**Purpose**: Define available subscription plans and pricing

```sql
CREATE TABLE subscriptions_subscriptionplan (
    id BIGSERIAL PRIMARY KEY,
    
    -- Plan identification
    name VARCHAR(100) NOT NULL UNIQUE, -- 'Basic Monthly', 'Pro Monthly', 'Premium 3-Month', etc.
    slug VARCHAR(100) NOT NULL UNIQUE,
    
    -- Plan details
    description TEXT,
    test_feedback_count INTEGER NOT NULL, -- 40 or 99 tests
    duration_months INTEGER NOT NULL, -- 1, 3, 6 months
    price_usd DECIMAL(10,2) NOT NULL, -- $19.00, $39.00, etc.
    
    -- Stripe integration
    stripe_price_id VARCHAR(100), -- Stripe price ID
    stripe_product_id VARCHAR(100), -- Stripe product ID
    
    -- Plan status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subscriptionplan_active ON subscriptions_subscriptionplan(is_active);
CREATE INDEX idx_subscriptionplan_featured ON subscriptions_subscriptionplan(is_featured);
```

#### UserSubscription Model
**App**: `subscriptions`
**Purpose**: Track user subscription status and usage

```sql
CREATE TABLE subscriptions_usersubscription (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    plan_id BIGINT NOT NULL REFERENCES subscriptions_subscriptionplan(id) ON DELETE PROTECT,
    
    -- Subscription details
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'paused')),
    
    -- Usage tracking
    test_feedback_used INTEGER NOT NULL DEFAULT 0,
    test_feedback_limit INTEGER NOT NULL, -- From plan
    
    -- Subscription period
    start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Stripe integration
    stripe_subscription_id VARCHAR(100) UNIQUE,
    stripe_customer_id VARCHAR(100),
    
    -- Metadata
    auto_renew BOOLEAN NOT NULL DEFAULT TRUE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usersubscription_user ON subscriptions_usersubscription(user_id);
CREATE INDEX idx_usersubscription_status ON subscriptions_usersubscription(status);
CREATE INDEX idx_usersubscription_end_date ON subscriptions_usersubscription(end_date);
CREATE INDEX idx_usersubscription_stripe_id ON subscriptions_usersubscription(stripe_subscription_id);
```

#### Payment Model
**App**: `subscriptions`
**Purpose**: Track payment transactions and history

```sql
CREATE TABLE subscriptions_payment (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    subscription_id BIGINT REFERENCES subscriptions_usersubscription(id) ON DELETE SET NULL,
    plan_id BIGINT NOT NULL REFERENCES subscriptions_subscriptionplan(id) ON DELETE PROTECT,
    
    -- Payment details
    amount_usd DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    payment_method VARCHAR(50), -- 'card', 'paypal', etc.
    
    -- Stripe integration
    stripe_payment_intent_id VARCHAR(100) UNIQUE,
    stripe_charge_id VARCHAR(100),
    stripe_invoice_id VARCHAR(100),
    
    -- Payment status
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'succeeded', 'failed', 'cancelled', 'refunded')),
    
    -- Webhook tracking
    webhook_received BOOLEAN NOT NULL DEFAULT FALSE,
    webhook_processed_at TIMESTAMP WITH TIME ZONE,
    webhook_data JSONB,
    
    -- Metadata
    description TEXT,
    failure_reason TEXT,
    refund_amount DECIMAL(10,2),
    refunded_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_user ON subscriptions_payment(user_id);
CREATE INDEX idx_payment_subscription ON subscriptions_payment(subscription_id);
CREATE INDEX idx_payment_status ON subscriptions_payment(status);
CREATE INDEX idx_payment_stripe_intent ON subscriptions_payment(stripe_payment_intent_id);
CREATE INDEX idx_payment_created ON subscriptions_payment(created_at);
```

#### UsageTracking Model
**App**: `subscriptions`
**Purpose**: Detailed tracking of test feedback usage

```sql
CREATE TABLE subscriptions_usagetracking (
    id BIGSERIAL PRIMARY KEY,
    
    -- References
    user_id BIGINT NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    subscription_id BIGINT NOT NULL REFERENCES subscriptions_usersubscription(id) ON DELETE CASCADE,
    assessment_id BIGINT NOT NULL REFERENCES assessment_assessment(id) ON DELETE CASCADE,
    
    -- Usage details
    usage_type VARCHAR(20) NOT NULL DEFAULT 'test_feedback' CHECK (usage_type IN ('test_feedback', 'bonus_feedback')),
    cost_count INTEGER NOT NULL DEFAULT 1, -- How many "credits" this used
    
    -- Metadata
    description TEXT,
    is_refunded BOOLEAN NOT NULL DEFAULT FALSE,
    refunded_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usagetracking_user ON subscriptions_usagetracking(user_id);
CREATE INDEX idx_usagetracking_subscription ON subscriptions_usagetracking(subscription_id);
CREATE INDEX idx_usagetracking_assessment ON subscriptions_usagetracking(assessment_id);
CREATE INDEX idx_usagetracking_created ON subscriptions_usagetracking(created_at);
```

---

## Relationship Summary

### Primary Relationships
1. **User → Submissions** (One-to-Many)
2. **PracticeTask → Submissions** (One-to-Many)
3. **Submission → Assessment** (One-to-One)
4. **Assessment → Feedback** (One-to-Many)
5. **User → Progress** (One-to-Many)
6. **Topic → PracticeTasks** (One-to-Many)
7. **User → Subscriptions** (One-to-Many)
8. **SubscriptionPlan → UserSubscriptions** (One-to-Many)
9. **User → Payments** (One-to-Many)
10. **Assessment → UsageTracking** (One-to-One)

### Key Foreign Keys
- `practice_submission.user_id` → `accounts_customuser.id`
- `practice_submission.task_id` → `practice_practicetask.id`
- `assessment_assessment.submission_id` → `practice_submission.id`
- `assessment_feedback.assessment_id` → `assessment_assessment.id`
- `progress_progressentry.user_id` → `accounts_customuser.id`
- `subscriptions_usersubscription.user_id` → `accounts_customuser.id`
- `subscriptions_usersubscription.plan_id` → `subscriptions_subscriptionplan.id`
- `subscriptions_payment.user_id` → `accounts_customuser.id`
- `subscriptions_payment.subscription_id` → `subscriptions_usersubscription.id`
- `subscriptions_usagetracking.assessment_id` → `assessment_assessment.id`

---

## Database Constraints and Indexes

### Performance Indexes
```sql
-- Composite indexes for common queries
CREATE INDEX idx_submission_user_status ON practice_submission(user_id, status);
CREATE INDEX idx_assessment_user_score ON assessment_assessment(submission_id, overall_band_score);
CREATE INDEX idx_progress_user_date ON progress_progressentry(user_id, created_at DESC);

-- Subscription and payment indexes
CREATE INDEX idx_usersubscription_user_status ON subscriptions_usersubscription(user_id, status);
CREATE INDEX idx_usersubscription_user_active ON subscriptions_usersubscription(user_id, status) WHERE status = 'active';
CREATE INDEX idx_payment_user_status ON subscriptions_payment(user_id, status);
CREATE INDEX idx_usagetracking_subscription_date ON subscriptions_usagetracking(subscription_id, created_at DESC);

-- Full-text search indexes
CREATE INDEX idx_practicetask_search ON practice_practicetask USING GIN(to_tsvector('english', title || ' ' || prompt));
```

### Data Integrity Constraints
```sql
-- Ensure assessment scores are within valid IELTS range
ALTER TABLE assessment_assessment ADD CONSTRAINT check_score_range 
CHECK (overall_band_score BETWEEN 1.0 AND 9.0);

-- Ensure word counts are reasonable
ALTER TABLE practice_submission ADD CONSTRAINT check_word_count 
CHECK (word_count >= 0 AND word_count <= 2000);

-- Ensure time spent is reasonable
ALTER TABLE practice_submission ADD CONSTRAINT check_time_spent 
CHECK (time_spent_seconds >= 0 AND time_spent_seconds <= 7200); -- Max 2 hours

-- Ensure subscription usage doesn't exceed limits
ALTER TABLE subscriptions_usersubscription ADD CONSTRAINT check_usage_limit 
CHECK (test_feedback_used >= 0 AND test_feedback_used <= test_feedback_limit);

-- Ensure subscription dates are logical
ALTER TABLE subscriptions_usersubscription ADD CONSTRAINT check_subscription_dates 
CHECK (end_date > start_date);

-- Ensure payment amounts are positive
ALTER TABLE subscriptions_payment ADD CONSTRAINT check_payment_amount 
CHECK (amount_usd >= 0);
```

---

## Database Views for Analytics

### User Performance View
```sql
CREATE VIEW user_performance_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.target_band_score,
    COUNT(s.id) as total_submissions,
    AVG(a.overall_band_score) as average_score,
    MAX(a.overall_band_score) as best_score,
    COUNT(CASE WHEN s.status = 'assessed' THEN 1 END) as completed_assessments,
    MAX(s.submitted_at) as last_practice_date
FROM accounts_customuser u
LEFT JOIN practice_submission s ON u.id = s.user_id
LEFT JOIN assessment_assessment a ON s.id = a.submission_id
GROUP BY u.id, u.username, u.target_band_score;
```

### Task Difficulty Analysis View
```sql
CREATE VIEW task_difficulty_analysis AS
SELECT 
    pt.id,
    pt.task_code,
    pt.difficulty_level,
    COUNT(s.id) as attempt_count,
    AVG(a.overall_band_score) as average_score,
    STDDEV(a.overall_band_score) as score_variance
FROM practice_practicetask pt
LEFT JOIN practice_submission s ON pt.id = s.task_id
LEFT JOIN assessment_assessment a ON s.id = a.submission_id
WHERE a.status = 'completed'
GROUP BY pt.id, pt.task_code, pt.difficulty_level;
```

### Subscription Analytics View
```sql
CREATE VIEW subscription_analytics AS
SELECT 
    sp.name as plan_name,
    sp.price_usd,
    sp.test_feedback_count as plan_limit,
    COUNT(us.id) as active_subscriptions,
    SUM(us.test_feedback_used) as total_usage,
    AVG(us.test_feedback_used) as avg_usage_per_user,
    SUM(CASE WHEN us.test_feedback_used = us.test_feedback_limit THEN 1 ELSE 0 END) as users_at_limit
FROM subscriptions_subscriptionplan sp
LEFT JOIN subscriptions_usersubscription us ON sp.id = us.plan_id AND us.status = 'active'
GROUP BY sp.id, sp.name, sp.price_usd, sp.test_feedback_count;
```

### Revenue Analytics View
```sql
CREATE VIEW revenue_analytics AS
SELECT 
    DATE_TRUNC('month', p.created_at) as month,
    COUNT(p.id) as total_payments,
    SUM(p.amount_usd) as total_revenue,
    AVG(p.amount_usd) as avg_payment_amount,
    COUNT(DISTINCT p.user_id) as paying_users,
    SUM(CASE WHEN p.status = 'succeeded' THEN p.amount_usd ELSE 0 END) as successful_revenue
FROM subscriptions_payment p
GROUP BY DATE_TRUNC('month', p.created_at)
ORDER BY month DESC;
```

---

## Migration Strategy

### Initial Data Requirements
1. **Topics**: Load standard IELTS topics (50-100 topics)
2. **Practice Tasks**: Load initial 600 writing tasks
3. **User Roles**: Create standard user groups and permissions
4. **System Configuration**: Default settings and preferences
5. **Subscription Plans**: Create initial subscription plans with Stripe integration
6. **Payment Configuration**: Set up Stripe webhook endpoints

### Data Seeding Commands
```python
# Django management commands to create
python manage.py load_topics
python manage.py load_practice_tasks
python manage.py create_sample_users --count=100
python manage.py setup_default_preferences
python manage.py setup_subscription_plans
python manage.py configure_stripe_webhooks
```

### Subscription Plan Initial Data
```sql
-- Initial subscription plans
INSERT INTO subscriptions_subscriptionplan (name, slug, description, test_feedback_count, duration_months, price_usd, is_active, is_featured, sort_order) VALUES
('Basic Monthly', 'basic-monthly', '40 AI feedback sessions per month', 40, 1, 19.00, true, false, 1),
('Pro Monthly', 'pro-monthly', '99 AI feedback sessions per month', 99, 1, 39.00, true, true, 2),
('Basic 3-Month', 'basic-3month', '40 AI feedback sessions per month (3 months)', 40, 3, 54.00, true, false, 3),
('Pro 3-Month', 'pro-3month', '99 AI feedback sessions per month (3 months)', 99, 3, 108.00, true, false, 4),
('Basic 6-Month', 'basic-6month', '40 AI feedback sessions per month (6 months)', 40, 6, 99.00, true, false, 5),
('Pro 6-Month', 'pro-6month', '99 AI feedback sessions per month (6 months)', 99, 6, 198.00, true, false, 6);
```

This database schema provides a robust foundation for the IELTS Writing Test platform with comprehensive subscription management, payment processing, usage tracking, and proper normalization with performance optimization and data integrity constraints.