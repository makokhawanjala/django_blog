from django.core.management.base import BaseCommand
from datetime import date


class Command(BaseCommand):
    help = 'Generate and email weekly analytics brief'

    def handle(self, *args, **options):
        from automation.models import WeeklyDigest
        from automation_scripts.analytics_fetcher import fetch_ga4_weekly_data
        from automation_scripts.claude_processor import generate_analytics_brief
        from automation_scripts.notifier import send_weekly_analytics_brief

        week_start = date.today().strftime('%Y-%m-%d')

        # Skip if already sent this week
        if WeeklyDigest.objects.filter(week_start=week_start).exists():
            self.stdout.write('Weekly digest already sent for this week')
            return

        self.stdout.write('Fetching GA4 data...')
        raw_data = fetch_ga4_weekly_data()

        if not raw_data:
            self.stdout.write(self.style.WARNING('No analytics data returned — skipping'))
            return

        self.stdout.write('Generating brief with Claude...')
        brief = generate_analytics_brief(raw_data)

        if brief:
            WeeklyDigest.objects.create(
                week_start=week_start,
                analytics_summary=brief,
                raw_data=raw_data
            )
            send_weekly_analytics_brief(brief, week_start)
            self.stdout.write(self.style.SUCCESS('Weekly brief sent'))
        else:
            self.stdout.write(self.style.ERROR('Claude returned empty brief'))