"""
Django management command to test Claude assessment with sample submission.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from practice.models import PracticeTask, Submission
from assessment.services import assessment_service

User = get_user_model()


class Command(BaseCommand):
    help = 'Test Claude assessment with a sample submission'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--task-code',
            type=str,
            required=True,
            help='Task code to create test submission for'
        )
        
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for test submission (will be created if not exists)'
        )
    
    def handle(self, *args, **options):
        task_code = options['task_code']
        username = options['username']
        
        try:
            # Get or create test user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@test.com',
                    'target_band_score': 7.0,
                    'module_type': 'academic',
                    'current_level': 'intermediate'
                }
            )
            
            if created:
                user.set_password('testpassword123')
                user.save()
                self.stdout.write(f'Created test user: {username}')
            
            # Get the practice task
            try:
                task = PracticeTask.objects.get(task_code=task_code)
            except PracticeTask.DoesNotExist:
                raise CommandError(f'Task with code "{task_code}" not found')
            
            # Create sample submission content based on task type
            if task.task_number == 1:
                if task.module_type == 'academic':
                    # Academic Task 1 sample
                    content = """The graph shows university enrollment trends from 2010 to 2020 for three different subjects: Engineering, Business, and Arts.

Overall, Engineering experienced the most significant growth, while Arts showed a declining trend throughout the period. Business enrollment remained relatively stable with minor fluctuations.

In 2010, Engineering had approximately 15,000 enrolled students, which increased steadily to reach 25,000 by 2020, representing the highest growth among all subjects. Business started with around 20,000 students in 2010 and maintained similar levels throughout the decade, with a slight increase to 22,000 by 2020.

In contrast, Arts enrollment declined consistently from 18,000 students in 2010 to 12,000 in 2020, showing the most significant decrease. The steepest decline occurred between 2015 and 2018, where enrollment dropped from 16,000 to 13,000.

By 2020, Engineering had become the most popular subject with 25,000 students, followed by Business with 22,000, and Arts with 12,000 students respectively."""
                else:
                    # General Task 1 sample (letter)
                    content = """Dear Customer Service Manager,

I am writing to complain about a laptop computer I recently purchased from your online store on December 15th, 2023, order number #12345.

When the laptop arrived, I discovered several serious problems. Firstly, the screen has a large crack across the top corner, which makes it difficult to see part of the display clearly. Secondly, the keyboard is missing three keys, and several other keys are loose and do not respond properly when pressed. Finally, the battery does not hold a charge for more than one hour, which is far below the advertised 8-hour battery life.

These problems are significantly affecting my work and studies. I am a university student who relies on my laptop for assignments and research. The damaged screen makes it impossible to view documents properly, and the faulty keyboard prevents me from typing efficiently. The poor battery life means I cannot use the laptop away from a power source.

I would like you to replace the laptop with a new one immediately. Alternatively, I would accept a full refund if a replacement is not available. I have enclosed photographs of the damage and my receipt as proof of purchase.

I look forward to your prompt response and a quick resolution to this matter.

Yours faithfully,
John Smith"""
            else:  # Task 2
                content = """The rise of social media platforms has fundamentally transformed how people communicate and share information in the 21st century. While these platforms offer numerous benefits, they also present significant challenges that affect individuals and society as a whole.

On the positive side, social media has revolutionized global communication. People can now instantly connect with friends and family across the world, share experiences, and maintain relationships regardless of geographical distance. Additionally, these platforms have democratized information sharing, allowing individuals to access news, educational content, and diverse perspectives from around the globe. For businesses and professionals, social media provides unprecedented opportunities for marketing, networking, and career development.

However, the drawbacks of social media are equally significant. Privacy concerns have become paramount as personal data is collected and potentially misused by companies and malicious actors. Mental health issues, particularly among young people, have been linked to excessive social media use, leading to problems such as anxiety, depression, and low self-esteem caused by constant comparison with others. Furthermore, the spread of misinformation and fake news through these platforms has undermined public trust and contributed to social division.

In my opinion, while the benefits of social media are substantial, the negative consequences are becoming increasingly serious and require urgent attention. The potential for social media to enhance human connection and knowledge sharing is enormous, but this must be balanced against the very real risks to privacy, mental health, and social cohesion.

To maximize benefits while minimizing harm, I believe we need stronger regulation of data privacy, better education about responsible social media use, and improved content moderation to combat misinformation. Only through such measures can we ensure that social media serves humanity's best interests."""
            
            # Create test submission
            submission = Submission.objects.create(
                user=user,
                task=task,
                content=content,
                word_count=len(content.split()),
                status='submitted',
                submitted_at=timezone.now()
            )
            
            self.stdout.write(f'Created test submission: {submission.id}')
            self.stdout.write(f'Word count: {submission.word_count}')
            
            # Process assessment
            self.stdout.write(self.style.WARNING('Starting assessment...'))
            
            assessment = assessment_service.assess_submission(submission)
            
            # Display results
            self.stdout.write(self.style.SUCCESS('Assessment completed!'))
            self.stdout.write(f'Overall Band Score: {assessment.overall_band_score}')
            self.stdout.write(f'Task Achievement: {assessment.task_achievement_score}')
            self.stdout.write(f'Coherence & Cohesion: {assessment.coherence_cohesion_score}')
            self.stdout.write(f'Lexical Resource: {assessment.lexical_resource_score}')
            self.stdout.write(f'Grammar & Accuracy: {assessment.grammar_accuracy_score}')
            self.stdout.write(f'Processing Time: {assessment.processing_time_seconds}s')
            self.stdout.write(f'AI Model: {assessment.ai_model_used}')
            
            # Display feedback
            feedback_items = assessment.feedback_items.all()
            self.stdout.write(f'\nFeedback Items: {feedback_items.count()}')
            
            for feedback in feedback_items:
                self.stdout.write(f'\n{feedback.get_feedback_type_display()}: {feedback.title}')
                self.stdout.write(f'  {feedback.content[:100]}...')
                
        except Exception as e:
            raise CommandError(f'Test assessment failed: {e}')