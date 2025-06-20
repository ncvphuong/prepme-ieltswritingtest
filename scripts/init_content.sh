#!/bin/bash

# IELTS Writing Test - Initial Content Setup Script
# This script creates 20 initial practice tasks for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}IELTS Writing Test - Content Initialization${NC}"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: This script must be run from the Django project root directory${NC}"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not detected${NC}"
    echo "Attempting to activate virtual environment..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}Virtual environment activated${NC}"
    else
        echo -e "${RED}Error: Virtual environment not found. Please run setup_dev.sh first${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Creating initial content...${NC}"

# Create Django management command to populate content
cat > content_script.py << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

from practice.models import Topic, PracticeTask

# Create topics
topics_data = [
    {'name': 'Education', 'slug': 'education', 'description': 'Topics related to learning, schools, and academic pursuits'},
    {'name': 'Technology', 'slug': 'technology', 'description': 'Topics about technology, computers, and digital life'},
    {'name': 'Environment', 'slug': 'environment', 'description': 'Topics about nature, climate, and environmental issues'},
    {'name': 'Health', 'slug': 'health', 'description': 'Topics related to health, fitness, and medical issues'},
    {'name': 'Social Issues', 'slug': 'social-issues', 'description': 'Topics about society, culture, and social problems'},
    {'name': 'Work & Career', 'slug': 'work-career', 'description': 'Topics about employment, careers, and workplace'},
    {'name': 'Transportation', 'slug': 'transportation', 'description': 'Topics about travel, vehicles, and transportation systems'},
    {'name': 'Media', 'slug': 'media', 'description': 'Topics about news, entertainment, and communication'},
]

print("Creating topics...")
topics = {}
for topic_data in topics_data:
    topic, created = Topic.objects.get_or_create(
        name=topic_data['name'],
        defaults=topic_data
    )
    topics[topic.name] = topic
    if created:
        print(f"✓ Created topic: {topic.name}")
    else:
        print(f"- Topic already exists: {topic.name}")

# Create practice tasks
tasks_data = [
    # Academic Task 1 (Graphs/Charts)
    {
        'task_code': 'AC-T1-001',
        'title': 'University Enrollment Trends',
        'module_type': 'academic',
        'task_number': 1,
        'difficulty_level': 'intermediate',
        'topic': 'Education',
        'prompt': '''The graph below shows university enrollment numbers in three different subjects from 2010 to 2020.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Describe the overall trends shown in the graph
• Compare the three subjects
• Highlight significant changes or patterns
• Use appropriate vocabulary for describing data''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'AC-T1-002',
        'title': 'Smartphone Usage by Age Group',
        'module_type': 'academic',
        'task_number': 1,
        'difficulty_level': 'beginner',
        'topic': 'Technology',
        'prompt': '''The chart below shows smartphone usage hours per day by different age groups in 2023.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Identify the highest and lowest usage groups
• Compare usage patterns across age groups
• Mention any notable trends or differences
• Use precise vocabulary for data description''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'AC-T1-003',
        'title': 'Renewable Energy Production',
        'module_type': 'academic',
        'task_number': 1,
        'difficulty_level': 'advanced',
        'topic': 'Environment',
        'prompt': '''The graphs below show renewable energy production in four countries between 2015 and 2025.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Compare renewable energy production across countries
• Describe trends over the time period
• Identify the most significant changes
• Use appropriate academic vocabulary''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },

    # Academic Task 2 (Essays)
    {
        'task_code': 'AC-T2-001',
        'title': 'Online vs Traditional Education',
        'module_type': 'academic',
        'task_number': 2,
        'difficulty_level': 'intermediate',
        'topic': 'Education',
        'prompt': '''Some people believe that online education is as effective as traditional classroom learning, while others argue that face-to-face instruction is irreplaceable.

Discuss both views and give your own opinion.

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Present both sides of the argument
• Give your personal opinion with justification
• Use specific examples and evidence
• Structure your essay with clear paragraphs''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },
    {
        'task_code': 'AC-T2-002',
        'title': 'Social Media Impact on Society',
        'module_type': 'academic',
        'task_number': 2,
        'difficulty_level': 'advanced',
        'topic': 'Social Issues',
        'prompt': '''Social media platforms have fundamentally changed how people communicate and share information. However, concerns have been raised about their impact on mental health, privacy, and social relationships.

To what extent do you think the benefits of social media outweigh the drawbacks?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Evaluate both benefits and drawbacks
• Take a clear position on the extent question
• Support arguments with relevant examples
• Demonstrate critical thinking and analysis''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },
    {
        'task_code': 'AC-T2-003',
        'title': 'Artificial Intelligence in the Workplace',
        'module_type': 'academic',
        'task_number': 2,
        'difficulty_level': 'advanced',
        'topic': 'Technology',
        'prompt': '''Artificial intelligence and automation are increasingly replacing human workers in various industries. While this brings efficiency and cost savings, it also leads to unemployment and social challenges.

What are the advantages and disadvantages of this trend? What measures can be taken to address the negative effects?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Identify clear advantages and disadvantages
• Propose practical solutions to problems
• Use relevant examples from real situations
• Maintain a balanced and analytical approach''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },

    # General Training Task 1 (Letters)
    {
        'task_code': 'GT-T1-001',
        'title': 'Complaint Letter - Defective Product',
        'module_type': 'general',
        'task_number': 1,
        'difficulty_level': 'beginner',
        'topic': 'Work & Career',
        'prompt': '''You recently bought a laptop computer from an online store. However, when it arrived, you discovered several problems with it.

Write a letter to the customer service department. In your letter:
• Describe the problems with the laptop
• Explain how these problems are affecting you
• Say what you would like the company to do

Write at least 150 words.

You do NOT need to write any addresses.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Use appropriate formal letter format
• Address all three bullet points
• Use polite but firm tone
• Include specific details about the problems''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'GT-T1-002',
        'title': 'Request Letter - Course Information',
        'module_type': 'general',
        'task_number': 1,
        'difficulty_level': 'intermediate',
        'topic': 'Education',
        'prompt': '''You are interested in taking a short course at a college in another country.

Write a letter to the admissions office. In your letter:
• Explain why you want to take the course
• Ask about the course content and duration
• Inquire about accommodation and fees

Write at least 150 words.

You do NOT need to write any addresses.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Use appropriate formal letter format
• Clearly explain your motivation
• Ask specific and relevant questions
• Maintain a polite and professional tone''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'GT-T1-003',
        'title': 'Invitation Letter - Birthday Party',
        'module_type': 'general',
        'task_number': 1,
        'difficulty_level': 'beginner',
        'topic': 'Social Issues',
        'prompt': '''You are organizing a birthday party for a family member and want to invite your English-speaking friend.

Write a letter to your friend. In your letter:
• Explain the occasion and why it is important
• Give details about the time, date and location
• Say what you would like your friend to bring

Write at least 150 words.

You do NOT need to write any addresses.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Use informal, friendly tone
• Include all necessary party details
• Make the invitation sound appealing
• Show enthusiasm about the event''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },

    # General Training Task 2 (Essays)
    {
        'task_code': 'GT-T2-001',
        'title': 'Public Transportation vs Private Cars',
        'module_type': 'general',
        'task_number': 2,
        'difficulty_level': 'intermediate',
        'topic': 'Transportation',
        'prompt': '''In many cities, people prefer to use private cars rather than public transportation.

What are the reasons for this preference? What can be done to encourage people to use public transportation more?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Identify reasons for preferring private cars
• Suggest practical solutions to promote public transport
• Use examples from your experience or knowledge
• Structure your essay with clear introduction and conclusion''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },
    {
        'task_code': 'GT-T2-002',
        'title': 'Working from Home',
        'module_type': 'general',
        'task_number': 2,
        'difficulty_level': 'intermediate',
        'topic': 'Work & Career',
        'prompt': '''Many companies now allow their employees to work from home. This trend has become more common since the COVID-19 pandemic.

Do you think this is a positive or negative development? What are the advantages and disadvantages for both employees and employers?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Take a clear position (positive or negative)
• Discuss advantages and disadvantages
• Consider both employee and employer perspectives
• Use relevant examples from recent experience''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },
    {
        'task_code': 'GT-T2-003',
        'title': 'Healthy Lifestyle Choices',
        'module_type': 'general',
        'task_number': 2,
        'difficulty_level': 'beginner',
        'topic': 'Health',
        'prompt': '''Many people today struggle to maintain a healthy lifestyle due to busy work schedules and modern life pressures.

What are the main reasons why people find it difficult to stay healthy? What solutions can you suggest to help people lead healthier lives?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Identify main obstacles to healthy living
• Propose practical and realistic solutions
• Use examples from everyday life
• Write in a clear and accessible style''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },

    # Additional variety tasks
    {
        'task_code': 'AC-T1-004',
        'title': 'City Population Growth',
        'module_type': 'academic',
        'task_number': 1,
        'difficulty_level': 'intermediate',
        'topic': 'Social Issues',
        'prompt': '''The table below shows population growth in five major cities from 2000 to 2020.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Compare population growth rates between cities
• Identify which cities grew the fastest/slowest
• Mention specific figures and percentages
• Use appropriate vocabulary for describing changes''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'GT-T1-004',
        'title': 'Job Application Follow-up',
        'module_type': 'general',
        'task_number': 1,
        'difficulty_level': 'intermediate',
        'topic': 'Work & Career',
        'prompt': '''You applied for a job three weeks ago but have not heard back from the company.

Write a letter to the hiring manager. In your letter:
• Remind them about your application
• Express your continued interest in the position
• Ask about the status of your application

Write at least 150 words.

You do NOT need to write any addresses.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Use professional and polite tone
• Reference your original application clearly
• Show enthusiasm without being pushy
• Request specific information about timeline''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'AC-T2-004',
        'title': 'Space Exploration Investment',
        'module_type': 'academic',
        'task_number': 2,
        'difficulty_level': 'advanced',
        'topic': 'Technology',
        'prompt': '''Governments spend billions of dollars on space exploration while many people on Earth lack basic necessities like clean water, healthcare, and education.

Some argue that space exploration is essential for human progress, while others believe these funds should be redirected to solve earthly problems.

Discuss both views and give your own opinion.

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Present arguments for both space exploration and earthly priorities
• Consider long-term vs short-term benefits
• Provide specific examples of space benefits or earthly needs
• Reach a well-reasoned conclusion''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },
    {
        'task_code': 'GT-T2-004',
        'title': 'Traditional vs Modern Shopping',
        'module_type': 'general',
        'task_number': 2,
        'difficulty_level': 'intermediate',
        'topic': 'Social Issues',
        'prompt': '''Online shopping has become increasingly popular, leading to the closure of many traditional brick-and-mortar stores.

What are the advantages and disadvantages of this trend? How do you think shopping will change in the future?

Give reasons for your answer and include any relevant examples from your own knowledge or experience.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Discuss both positive and negative aspects of online shopping growth
• Consider the impact on traditional retailers
• Make predictions about future shopping trends
• Use examples from your own shopping experience''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    },
    {
        'task_code': 'AC-T1-005',
        'title': 'Energy Consumption Comparison',
        'module_type': 'academic',
        'task_number': 1,
        'difficulty_level': 'advanced',
        'topic': 'Environment',
        'prompt': '''The pie charts below show energy consumption by source in two countries, Country A and Country B, in 2023.

Summarize the information by selecting and reporting the main features, and make comparisons where relevant.

Write at least 150 words.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Compare energy sources between the two countries
• Identify the most and least used energy sources
• Highlight significant differences in consumption patterns
• Use precise vocabulary for percentages and proportions''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'GT-T1-005',
        'title': 'Neighborhood Noise Complaint',
        'module_type': 'general',
        'task_number': 1,
        'difficulty_level': 'intermediate',
        'topic': 'Social Issues',
        'prompt': '''You live in an apartment and are experiencing problems with noise from your upstairs neighbor.

Write a letter to your landlord. In your letter:
• Describe the noise problems
• Explain how it is affecting your daily life
• Suggest what action the landlord should take

Write at least 150 words.

You do NOT need to write any addresses.''',
        'instruction': '''You should spend about 20 minutes on this task.

• Be specific about the noise issues
• Explain the impact on your quality of life
• Propose reasonable solutions
• Maintain a respectful but firm tone''',
        'time_limit_minutes': 20,
        'word_limit_min': 150,
        'word_limit_max': 200,
    },
    {
        'task_code': 'GT-T2-005',
        'title': 'Technology and Children',
        'module_type': 'general',
        'task_number': 2,
        'difficulty_level': 'intermediate',
        'topic': 'Technology',
        'prompt': '''Children today spend increasing amounts of time using electronic devices such as smartphones, tablets, and computers.

Some people believe this technology use is beneficial for children's development, while others worry about negative effects on their physical and social development.

What is your opinion? Support your view with specific reasons and examples.

Write at least 250 words.''',
        'instruction': '''You should spend about 40 minutes on this task.

• Take a clear position on technology use by children
• Provide specific reasons for your viewpoint
• Use examples from education, development, or family experience
• Consider both benefits and potential risks''',
        'time_limit_minutes': 40,
        'word_limit_min': 250,
        'word_limit_max': 350,
    }
]

print("Creating practice tasks...")
created_count = 0
existing_count = 0

for task_data in tasks_data:
    topic_name = task_data.pop('topic')
    task_data['topic'] = topics[topic_name]
    
    task, created = PracticeTask.objects.get_or_create(
        task_code=task_data['task_code'],
        defaults=task_data
    )
    
    if created:
        print(f"✓ Created task: {task.task_code} - {task.title}")
        created_count += 1
    else:
        print(f"- Task already exists: {task.task_code} - {task.title}")
        existing_count += 1

print(f"\nContent initialization complete!")
print(f"Created: {created_count} new tasks")
print(f"Existing: {existing_count} tasks")
print(f"Total: {created_count + existing_count} tasks available")

EOF

# Run the content creation script
echo -e "${BLUE}Running content creation script...${NC}"
python content_script.py

# Clean up the temporary script
rm content_script.py

echo -e "${GREEN}✓ Initial content setup completed successfully!${NC}"
echo ""
echo "Summary:"
echo "- Created topics for different subject areas"
echo "- Added 20 practice tasks covering:"
echo "  • Academic Task 1 (Charts/Graphs): 5 tasks"
echo "  • Academic Task 2 (Essays): 4 tasks" 
echo "  • General Training Task 1 (Letters): 5 tasks"
echo "  • General Training Task 2 (Essays): 6 tasks"
echo "- Tasks span difficulty levels: beginner, intermediate, advanced"
echo "- Topics include: Education, Technology, Environment, Health, Social Issues, etc."
echo ""
echo -e "${BLUE}You can now access practice tasks at: /practice/${NC}"