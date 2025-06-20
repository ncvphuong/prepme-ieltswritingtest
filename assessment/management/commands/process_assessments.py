"""
Django management command to process assessment queue.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from assessment.services import assessment_service


class Command(BaseCommand):
    help = 'Process queued assessment requests using Claude AI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-requests',
            type=int,
            default=5,
            help='Maximum number of requests to process in this run'
        )
        
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run in daemon mode (continuous processing)'
        )
        
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval in seconds between processing cycles (daemon mode only)'
        )
    
    def handle(self, *args, **options):
        max_requests = options['max_requests']
        daemon_mode = options['daemon']
        interval = options['interval']
        
        if daemon_mode:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Starting assessment processor in daemon mode '
                    f'(max_requests={max_requests}, interval={interval}s)'
                )
            )
            
            import time
            try:
                while True:
                    processed = assessment_service.process_assessment_queue(max_requests)
                    
                    if processed > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'[{timezone.now()}] Processed {processed} assessments'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'[{timezone.now()}] No assessments to process'
                            )
                        )
                    
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.SUCCESS('Assessment processor stopped by user')
                )
        else:
            self.stdout.write('Processing assessment queue...')
            
            try:
                processed = assessment_service.process_assessment_queue(max_requests)
                
                if processed > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully processed {processed} assessments'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('No assessments found in queue')
                    )
                    
            except Exception as e:
                raise CommandError(f'Assessment processing failed: {e}')