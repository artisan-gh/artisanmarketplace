from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth, ExtractWeek
from django.utils import timezone
from datetime import timedelta
import csv
from io import StringIO
from django.http import HttpResponse

from incidents.models import Incident
from assignments.models import Assignment
from artisans.models import ArtisanProfile
from call_center.models import CallLog
from customers.models import Customer
from django.db import models

class IncidentReportView(APIView):
    """
    Comprehensive incident report with filters.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get parameters
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        end_date = request.query_params.get('end_date')
        if end_date:
            try:
                start_date = timezone.datetime.fromisoformat(
                    request.query_params.get('start_date', '')
                )
                end_date = timezone.datetime.fromisoformat(end_date)
            except (ValueError, TypeError):
                pass

        # Base queryset
        incidents = Incident.objects.filter(created_at__gte=start_date)
        if end_date:
            incidents = incidents.filter(created_at__lte=end_date)

        # Filters
        status = request.query_params.get('status')
        if status:
            incidents = incidents.filter(status__name=status)

        priority = request.query_params.get('priority')
        if priority:
            incidents = incidents.filter(priority=priority)

        category = request.query_params.get('category')
        if category:
            incidents = incidents.filter(category__id=category)

        # ─── Reports ──────────────────────────────────────────

        # Incident Count by Status
        status_counts = incidents.values('status__name').annotate(
            count=Count('id')
        ).order_by('-count')

        # Incident Count by Priority
        priority_counts = incidents.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')

        # Incident Count by Category
        category_counts = incidents.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')

        # Daily Incident Count
        daily_counts = incidents.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        # Weekly Incident Count
        weekly_counts = incidents.annotate(
            week=ExtractWeek('created_at')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')

        # Average Resolution Time
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
            avg_resolution_hours = round(
                avg_resolution_seconds.total_seconds() / 3600, 1
            )
        else:
            avg_resolution_hours = None

        # SLA Compliance
        total = incidents.count()
        sla_met = incidents.filter(
            resolved_at__lte=F('target_resolution')
        ).count()
        sla_missed = incidents.filter(
            resolved_at__gt=F('target_resolution')
        ).count()
        sla_met_percent = round((sla_met / total) * 100, 1) if total > 0 else 0

        # Data
        data = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': (end_date or timezone.now()).isoformat(),
                'days': days,
            },
            'summary': {
                'total_incidents': total,
                'resolved': incidents.filter(status__name='RESOLVED').count(),
                'closed': incidents.filter(status__name='CLOSED').count(),
                'open': incidents.filter(status__name='OPEN').count(),
                'avg_resolution_hours': avg_resolution_hours,
            },
            'sla': {
                'met': sla_met,
                'missed': sla_missed,
                'met_percent': sla_met_percent,
            },
            'distribution': {
                'by_status': list(status_counts),
                'by_priority': list(priority_counts),
                'by_category': list(category_counts),
            },
            'trends': {
                'daily': list(daily_counts),
                'weekly': list(weekly_counts),
            },
        }

        return Response(data)


class ArtisanPerformanceReportView(APIView):
    """
    Artisan performance report with detailed metrics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        artisans = ArtisanProfile.objects.all()
        report = []

        for artisan in artisans:
            assignments = Assignment.objects.filter(
                artisan=artisan.user,
                assigned_at__gte=start_date
            )

            total = assignments.count()
            completed = assignments.filter(status='COMPLETED').count()
            in_progress = assignments.filter(status='IN_PROGRESS').count()
            pending = assignments.filter(status='PENDING').count()

            # Completion rate
            completion_rate = round((completed / total) * 100, 1) if total > 0 else 0

            # Average completion time
            completed_assignments = assignments.filter(status='COMPLETED')
            avg_time = None
            if completed > 0:
                total_seconds = sum(
                    (a.completed_at - a.assigned_at).total_seconds()
                    for a in completed_assignments
                    if a.completed_at and a.assigned_at
                )
                avg_time = round(total_seconds / completed, 1) if completed > 0 else 0

            # Rating (if available)
            avg_rating = artisan.average_rating

            report.append({
                'artisan_id': str(artisan.id),
                'artisan_name': artisan.user.get_full_name(),
                'email': artisan.user.email,
                'total_assignments': total,
                'pending': pending,
                'in_progress': in_progress,
                'completed': completed,
                'completion_rate': completion_rate,
                'avg_completion_time_seconds': avg_time,
                'avg_rating': avg_rating,
            })

        # Sort by completion rate (descending)
        report = sorted(report, key=lambda x: x['completion_rate'], reverse=True)

        return Response({
            'period_days': days,
            'start_date': start_date.isoformat(),
            'artisans': report,
        })


class CallCenterReportView(APIView):
    """
    Call center performance report.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        calls = CallLog.objects.filter(started_at__gte=start_date)

        # Overall stats
        total_calls = calls.count()
        inbound = calls.filter(direction='INBOUND').count()
        outbound = calls.filter(direction='OUTBOUND').count()

        # By disposition
        disposition_counts = calls.values('disposition').annotate(
            count=Count('id')
        ).order_by('-count')

        # Average call duration
        avg_duration = calls.aggregate(
            avg_seconds=Avg('duration_seconds')
        )
        avg_duration_seconds = avg_duration.get('avg_seconds') or 0

        # Agent performance
        agent_performance = calls.values('agent__email', 'agent__first_name', 'agent__last_name').annotate(
            total_calls=Count('id'),
            avg_duration=Avg('duration_seconds'),
        ).order_by('-total_calls')

        # Daily call volume
        daily_volume = calls.annotate(
            day=TruncDate('started_at')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        data = {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'summary': {
                'total_calls': total_calls,
                'inbound': inbound,
                'outbound': outbound,
                'avg_duration_seconds': round(avg_duration_seconds, 1),
            },
            'disposition': list(disposition_counts),
            'agent_performance': list(agent_performance),
            'daily_volume': list(daily_volume),
        }

        return Response(data)


class CustomerReportView(APIView):
    """
    Customer activity and incident report.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Customers with incidents
        customers = Customer.objects.filter(
            incidents__created_at__gte=start_date,
            is_deleted=False
        ).distinct()

        report = []
        for customer in customers:
            incidents = customer.incidents.filter(created_at__gte=start_date)
            resolved = incidents.filter(status__name='RESOLVED').count()
            open_incidents = incidents.filter(status__name='OPEN').count()

            calls = customer.call_logs.filter(started_at__gte=start_date)

            report.append({
                'customer_id': str(customer.id),
                'customer_name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'total_incidents': incidents.count(),
                'resolved': resolved,
                'open': open_incidents,
                'total_calls': calls.count(),
                'last_incident': incidents.order_by('-created_at').first().created_at.isoformat() if incidents.exists() else None,
            })

        # Sort by total incidents (descending)
        report = sorted(report, key=lambda x: x['total_incidents'], reverse=True)

        return Response({
            'period_days': days,
            'start_date': start_date.isoformat(),
            'customers': report,
        })


class ExportReportView(APIView):
    """
    Export report data as CSV.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        report_type = request.query_params.get('type', 'incidents')
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        if report_type == 'incidents':
            incidents = Incident.objects.filter(created_at__gte=start_date)
            writer.writerow(['Incident Number', 'Customer', 'Title', 'Priority', 'Status', 'Created At', 'Resolved At'])
            for inc in incidents:
                writer.writerow([
                    inc.incident_number,
                    inc.customer.name,
                    inc.title,
                    inc.priority,
                    inc.status.name if inc.status else '',
                    inc.created_at.isoformat(),
                    inc.resolved_at.isoformat() if inc.resolved_at else '',
                ])

        elif report_type == 'assignments':
            assignments = Assignment.objects.filter(assigned_at__gte=start_date)
            writer.writerow(['Incident', 'Artisan', 'Status', 'Assigned At', 'Completed At'])
            for ass in assignments:
                writer.writerow([
                    ass.incident.incident_number,
                    ass.artisan.get_full_name(),
                    ass.status,
                    ass.assigned_at.isoformat(),
                    ass.completed_at.isoformat() if ass.completed_at else '',
                ])

        elif report_type == 'calls':
            calls = CallLog.objects.filter(started_at__gte=start_date)
            writer.writerow(['Reference', 'Agent', 'Direction', 'Caller', 'Disposition', 'Started At', 'Duration'])
            for call in calls:
                writer.writerow([
                    call.reference,
                    call.agent.get_full_name() if call.agent else '',
                    call.direction,
                    call.caller_number,
                    call.disposition,
                    call.started_at.isoformat(),
                    call.duration_seconds or '',
                ])

        elif report_type == 'customers':
            customers = Customer.objects.filter(created_at__gte=start_date, is_deleted=False)
            writer.writerow(['Name', 'Phone', 'Email', 'Total Incidents', 'Created At'])
            for cust in customers:
                writer.writerow([
                    cust.name,
                    cust.phone,
                    cust.email,
                    cust.incidents.count(),
                    cust.created_at.isoformat(),
                ])

        # Response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
        return response
