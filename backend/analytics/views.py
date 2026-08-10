from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
from incidents.models import Incident
from assignments.models import Assignment
from artisans.models import ArtisanProfile
from call_center.models import CallLog
from sla.models import SLATracker
from django.db import models

class KPIsView(APIView):
    """
    Advanced KPIs for executives and managers.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        now = timezone.now()

        # ─── Incident KPIs ─────────────────────────────────────
        incidents = Incident.objects.filter(created_at__gte=start_date)
        total_incidents = incidents.count()
        resolved = incidents.filter(status__name='RESOLVED').count()
        resolution_rate = round((resolved / total_incidents) * 100, 1) if total_incidents > 0 else 0

        avg_resolution = incidents.filter(
            resolved_at__isnull=False
        ).aggregate(
            avg_seconds=Avg(
                F('resolved_at') - F('created_at'),
                output_field=models.DurationField()
            )
        )
        avg_resolution_seconds = avg_resolution.get('avg_seconds')
        avg_resolution_hours = round(avg_resolution_seconds.total_seconds() / 3600, 2) if avg_resolution_seconds else 0

        incident_trend = incidents.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        # ─── SLA KPIs ──────────────────────────────────────────
        sla_trackers = SLATracker.objects.filter(
            created_at__gte=start_date
        )
        total_sla = sla_trackers.count()
        sla_breached = sla_trackers.filter(status='BREACHED').count()
        sla_on_track = sla_trackers.filter(status='ON_TRACK').count()
        sla_compliance = round((sla_on_track / total_sla) * 100, 1) if total_sla > 0 else 0

        # ─── Artisan KPIs ──────────────────────────────────────
        artisans = ArtisanProfile.objects.all()
        active_artisans = artisans.filter(is_available=True).count()
        total_artisans = artisans.count()
        avg_rating = artisans.aggregate(avg=Avg('average_rating'))['avg'] or 0

        # ─── Assignment KPIs ──────────────────────────────────
        assignments = Assignment.objects.filter(assigned_at__gte=start_date)
        total_assignments = assignments.count()
        completed_assignments = assignments.filter(status='COMPLETED').count()
        assignment_completion_rate = round(
            (completed_assignments / total_assignments) * 100, 1
        ) if total_assignments > 0 else 0

        # ─── Call Center KPIs ──────────────────────────────────
        calls = CallLog.objects.filter(started_at__gte=start_date)
        total_calls = calls.count()
        avg_call_duration = calls.aggregate(avg=Avg('duration_seconds'))['avg'] or 0
        fcr = calls.filter(disposition__in=['RESOLVED', 'INCIDENT_CREATED']).count()
        fcr_rate = round((fcr / total_calls) * 100, 1) if total_calls > 0 else 0

        # ─── Predictive KPIs ──────────────────────────────────
        avg_daily = total_incidents / days if days > 0 else 0
        projected_next_7 = round(avg_daily * 7, 1)

        data = {
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
            },
            'incidents': {
                'total': total_incidents,
                'resolved': resolved,
                'resolution_rate': resolution_rate,
                'avg_resolution_hours': avg_resolution_hours,
                'trend': list(incident_trend),
            },
            'sla': {
                'total': total_sla,
                'breached': sla_breached,
                'on_track': sla_on_track,
                'compliance': sla_compliance,
            },
            'artisans': {
                'total': total_artisans,
                'active': active_artisans,
                'avg_rating': round(avg_rating, 1),
            },
            'assignments': {
                'total': total_assignments,
                'completed': completed_assignments,
                'completion_rate': assignment_completion_rate,
            },
            'calls': {
                'total': total_calls,
                'avg_duration_seconds': round(avg_call_duration, 1),
                'fcr_rate': fcr_rate,
            },
            'forecast': {
                'projected_next_7_days': projected_next_7,
            },
            'updated_at': now.isoformat(),
        }
        return Response(data)
