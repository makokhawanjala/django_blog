import logging
from automation_scripts.config import GOOGLE_ANALYTICS_PROPERTY_ID

logger = logging.getLogger(__name__)


def fetch_ga4_weekly_data() -> dict:
    """
    Fetches last 7 days of data from GA4.
    Returns dict with sessions, page_views_by_page, engagement_time, top_sources.
    Requires GOOGLE_APPLICATION_CREDENTIALS env var pointing to a service account JSON,
    OR use the API key approach if running locally.
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Metric, Dimension
        )
        client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=GOOGLE_ANALYTICS_PROPERTY_ID,
            date_ranges=[DateRange(start_date='7daysAgo', end_date='today')],
            dimensions=[Dimension(name='pagePath'), Dimension(name='sessionDefaultChannelGroup')],
            metrics=[
                Metric(name='sessions'),
                Metric(name='activeUsers'),
                Metric(name='averageSessionDuration'),
                Metric(name='screenPageViews'),
            ]
        )
        response = client.run_report(request)
        rows = []
        for row in response.rows:
            rows.append({
                'page': row.dimension_values[0].value,
                'channel': row.dimension_values[1].value,
                'sessions': row.metric_values[0].value,
                'users': row.metric_values[1].value,
                'avg_duration': row.metric_values[2].value,
                'pageviews': row.metric_values[3].value,
            })
        return {'rows': rows, 'row_count': len(rows)}
    except Exception as e:
        logger.error(f'GA4 fetch error: {e}')
        return {}