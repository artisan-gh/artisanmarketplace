# dashboard/views.py
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Sum, Q, F, Max, Min
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
import json

from incidents.models import Incident
from assignments.models import Assignment
from artisans.models import ArtisanProfile
from customers.models import Customer
from call_center.models import CallLog


class DashboardSummaryView(APIView):
    """
    Advanced admin dashboard summary with role-based data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        start_of_year = now.replace(month=1, day=1)

        # ─── Role-based filters ──────────────────────────────
        is_admin = user.is_admin or user.is_staff
        is_artisan = user.is_artisan
        is_agent = user.is_agent
        is_dispatcher = user.is_dispatcher
        is_supervisor = user.is_supervisor

        # ─── Base Querysets ────────────────────────────────────
        incidents = Incident.objects.all()
        assignments = Assignment.objects.all()
        calls = CallLog.objects.all()

        if not is_admin:
            if is_artisan:
                incidents = incidents.filter(assigned_to=user)
                assignments = assignments.filter(artisan=user)
                calls = calls.filter(agent=user)
            elif is_agent:
                calls = calls.filter(agent=user)
            elif is_dispatcher:
                # Dispatcher sees all incidents and assignments
                pass
            elif is_supervisor:
                # Supervisor sees assigned incidents (if they have a team)
                pass
            else:
                # Fallback: only own data
                incidents = incidents.filter(created_by=user)
                calls = calls.filter(agent=user)

        # ─── Summary Cards ────────────────────────────────────
        total_incidents = incidents.count()
        open_incidents = incidents.filter(status__name='OPEN').count()
        resolved_incidents = incidents.filter(status__name='RESOLVED').count()
        closed_incidents = incidents.filter(status__name='CLOSED').count()
        total_assignments = assignments.count()
        pending_assignments = assignments.filter(status='PENDING').count()
        completed_assignments = assignments.filter(status='COMPLETED').count()

        # ─── Incident Status Distribution ─────────────────────
        status_distribution = incidents.values('status__name').annotate(
            count=Count('id')
        ).order_by('-count')

        # ─── Incident Priority Distribution ──────────────────
        priority_distribution = incidents.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')

        # ─── Incident Category Distribution ──────────────────
        category_distribution = incidents.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # ─── Daily Incident Trend (last 30 days) ─────────────
        daily_trend = incidents.filter(
            created_at__gte=last_30_days
        ).annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        # ─── Monthly Incident Trend (year to date) ───────────
        monthly_trend = incidents.filter(
            created_at__gte=start_of_year
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # ─── Call Volume (last 30 days) ──────────────────────
        call_volume = calls.filter(
            started_at__gte=last_30_days
        ).annotate(
            day=TruncDate('started_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        # ─── Call Disposition Distribution ────────────────────
        call_disposition = calls.values('disposition').annotate(
            count=Count('id')
        ).order_by('-count')

        # ─── Artisan Performance ─────────────────────────────
        artisan_performance = []
        if is_admin or is_dispatcher or is_supervisor:
            artisan_profiles = ArtisanProfile.objects.all()
            for ap in artisan_profiles:
                artisan_assignments = assignments.filter(artisan=ap.user)
                total = artisan_assignments.count()
                completed = artisan_assignments.filter(status='COMPLETED').count()
                if total > 0:
                    rate = round((completed / total) * 100, 1)
                else:
                    rate = 0
                artisan_performance.append({
                    'id': str(ap.id),
                    'name': ap.user.get_full_name(),
                    'total': total,
                    'completed': completed,
                    'rate': rate,
                })
            artisan_performance = sorted(
                artisan_performance,
                key=lambda x: x['rate'],
                reverse=True
            )[:5]

        # ─── Average Resolution Time ─────────────────────────
        avg_resolution = incidents.filter(
            resolved_at__isnull=False
        ).aggregate(
            avg_seconds=Avg(
                F('resolved_at') - F('created_at'),
                output_field=models.DurationField()
            )
        )
        avg_resolution_seconds = avg_resolution.get('avg_seconds')
        if avg_resolution_seconds:
            avg_resolution_hours = round(avg_resolution_seconds.total_seconds() / 3600, 1)
        else:
            avg_resolution_hours = None

        # ─── SLA Compliance ───────────────────────────────────
        sla_met = incidents.filter(
            resolved_at__lte=F('target_resolution')
        ).count() if incidents.count() > 0 else 0
        sla_missed = incidents.filter(
            resolved_at__gt=F('target_resolution')
        ).count() if incidents.count() > 0 else 0

        # ─── Profile picture URL for the current user ─────────
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)

        # ─── Response ─────────────────────────────────────────
        data = {
            'user': {
                'id': str(user.id),
                'full_name': user.get_full_name(),
                'email': user.email,
                'role': user.get_user_type_display() or 'Administrator',
                'profile_picture': profile_picture_url,
            },
            'summary': {
                'total_incidents': total_incidents,
                'open_incidents': open_incidents,
                'resolved_incidents': resolved_incidents,
                'closed_incidents': closed_incidents,
                'total_assignments': total_assignments,
                'pending_assignments': pending_assignments,
                'completed_assignments': completed_assignments,
                'avg_resolution_hours': avg_resolution_hours,
            },
            'sla': {
                'met': sla_met,
                'missed': sla_missed,
            },
            'distribution': {
                'status': list(status_distribution),
                'priority': list(priority_distribution),
                'category': list(category_distribution),
                'call_disposition': list(call_disposition),
            },
            'trends': {
                'incidents_daily': list(daily_trend),
                'incidents_monthly': list(monthly_trend),
                'calls_daily': list(call_volume),
            },
            'performance': {
                'top_artisans': artisan_performance,
            },
            'period': {
                'last_30_days': last_30_days.isoformat(),
            },
            'updated_at': now.isoformat(),
        }
        return Response(data)


class AgentDashboardView(APIView):
    """
    Dashboard for call center agents – now focused on incident metrics.
    Call stats are kept as secondary information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        last_7_days = now - timedelta(days=7)

        # ─── Calls (optional, kept for reference) ──────────────
        my_calls = CallLog.objects.filter(agent=user)
        calls_today = my_calls.filter(started_at__date=today).count()
        calls_week = my_calls.filter(started_at__gte=last_7_days).count()
        calls_resolved = my_calls.filter(disposition__in=['RESOLVED', 'INCIDENT_CREATED']).count()
        total_calls = my_calls.count()

        # ─── Incidents created by this agent ────────────────────
        my_incidents = Incident.objects.filter(created_by=user)
        total_incidents_created = my_incidents.count()
        incidents_created_today = my_incidents.filter(created_at__date=today).count()
        incidents_created_week = my_incidents.filter(created_at__gte=last_7_days).count()

        # ─── Incidents assigned to this agent (if applicable) ──
        assigned_incidents = Incident.objects.filter(assigned_to=user)
        total_assigned = assigned_incidents.count()
        assigned_open = assigned_incidents.filter(status__name='OPEN').count()
        assigned_resolved = assigned_incidents.filter(status__name='RESOLVED').count()

        # ─── Recent Incidents (instead of calls) ──────────────
        recent_incidents = my_incidents.order_by('-created_at')[:10]
        recent_incidents_data = [{
            'id': str(inc.id),
            'incident_number': inc.incident_number,
            'title': inc.title,
            'status': inc.status.name if inc.status else None,
            'created_at': inc.created_at.isoformat(),
        } for inc in recent_incidents]

        # ─── Profile picture URL ──────────────────────────────
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)

        # ─── Response ─────────────────────────────────────────
        data = {
            'agent': {
                'id': str(user.id),
                'full_name': user.get_full_name(),
                'email': user.email,
                'role': user.get_user_type_display() or 'Call Center Agent',
                'profile_picture': profile_picture_url,
            },
            'summary': {
                # Incident stats
                'total_incidents_created': total_incidents_created,
                'incidents_created_today': incidents_created_today,
                'incidents_created_week': incidents_created_week,
                'total_assigned': total_assigned,
                'assigned_open': assigned_open,
                'assigned_resolved': assigned_resolved,
                # Call stats (optional)
                'calls_today': calls_today,
                'calls_week': calls_week,
                'total_calls': total_calls,
                'calls_resolved': calls_resolved,
            },
            'recent_incidents': recent_incidents_data,
            'updated_at': now.isoformat(),
        }
        return Response(data)


class ArtisanDashboardView(APIView):
    """
    Dashboard for artisans – assignment‑centric.
    Includes current assignment, summary stats, and recent assignments.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()

        # ─── Assignments for this artisan ──────────────────────
        my_assignments = Assignment.objects.filter(artisan=user)
        total = my_assignments.count()
        pending = my_assignments.filter(status='PENDING').count()
        in_progress = my_assignments.filter(status='IN_PROGRESS').count()
        completed = my_assignments.filter(status='COMPLETED').count()
        today_assignments = my_assignments.filter(assigned_at__date=today).count()
        rate = round((completed / total) * 100, 1) if total > 0 else 0

        # ─── Current assignment ────────────────────────────────
        current = my_assignments.filter(
            status__in=['PENDING', 'ACCEPTED', 'IN_PROGRESS']
        ).select_related('incident', 'incident__customer').first()

        # ─── Recent assignments (last 5) ──────────────────────
        recent = my_assignments.order_by('-assigned_at')[:5]
        recent_data = [{
            'id': str(ass.id),
            'incident_id': str(ass.incident.id),
            'incident_number': ass.incident.incident_number,
            'customer': ass.incident.customer.name if ass.incident.customer else None,
            'status': ass.status,
            'assigned_at': ass.assigned_at.isoformat() if ass.assigned_at else None,
        } for ass in recent]

        # ─── Profile picture ────────────────────────────────────
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)

        # ─── Response ─────────────────────────────────────────
        data = {
            'artisan': {
                'id': str(user.id),
                'full_name': user.get_full_name(),
                'email': user.email,
                'profile_picture': profile_picture_url,
            },
            'summary': {
                'total_assignments': total,
                'pending': pending,
                'in_progress': in_progress,
                'completed': completed,
                'today_assignments': today_assignments,
                'completion_rate': rate,
            },
            'current_assignment': {
                'id': str(current.id) if current else None,
                'incident_number': current.incident.incident_number if current else None,
                'customer': current.incident.customer.name if current else None,
                'status': current.status if current else None,
                'assigned_at': current.assigned_at.isoformat() if current else None,
            } if current else None,
            'recent_assignments': recent_data,
            'updated_at': now.isoformat(),
        }
        return Response(data)


class SupervisorDashboardView(APIView):
    """
    Dashboard for supervisors – team incident oversight.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        today = now.date()
        last_7_days = now - timedelta(days=7)

        # Team performance (supervisors manage a team)
        team_incidents = Incident.objects.all()  # Filter by team in production
        team_assignments = Assignment.objects.all()
        team_calls = CallLog.objects.all()

        # Team stats
        total_incidents = team_incidents.count()
        open_incidents = team_incidents.filter(status__name='OPEN').count()
        resolved_today = team_incidents.filter(
            resolved_at__date=today
        ).count()

        # Assignment stats
        pending_assignments = team_assignments.filter(status='PENDING').count()
        completed_today = team_assignments.filter(
            completed_at__date=today
        ).count()

        # Artisan availability
        available_artisans = ArtisanProfile.objects.filter(is_available=True).count()

        # SLA compliance
        sla_met = team_incidents.filter(
            resolved_at__lte=F('target_resolution')
        ).count()
        sla_missed = team_incidents.filter(
            resolved_at__gt=F('target_resolution')
        ).count()

        # Recent activity
        recent_incidents = team_incidents.order_by('-created_at')[:10]
        recent_incidents_data = [{
            'id': str(inc.id),
            'incident_number': inc.incident_number,
            'title': inc.title,
            'status': inc.status.name if inc.status else None,
            'created_at': inc.created_at.isoformat(),
        } for inc in recent_incidents]

        # Profile picture
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)

        data = {
            'supervisor': {
                'id': str(user.id),
                'full_name': user.get_full_name(),
                'email': user.email,
                'profile_picture': profile_picture_url,
            },
            'summary': {
                'total_incidents': total_incidents,
                'open_incidents': open_incidents,
                'resolved_today': resolved_today,
                'pending_assignments': pending_assignments,
                'completed_today': completed_today,
                'available_artisans': available_artisans,
            },
            'sla': {
                'met': sla_met,
                'missed': sla_missed,
            },
            'recent_incidents': recent_incidents_data,
            'updated_at': now.isoformat(),
        }
        return Response(data)
