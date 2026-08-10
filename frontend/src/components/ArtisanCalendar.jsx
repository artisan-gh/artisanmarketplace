// components/ArtisanCalendar.jsx
import { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import { getArtisanAvailability } from '../api/artisansAPI';
import toast from 'react-hot-toast';
import './ArtisanCalendar.css';

export default function ArtisanCalendar({ onDateSelect }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const fetchAvailability = async () => {
      setLoading(true);
      try {
        const dateStr = currentDate.toISOString().split('T')[0];
        const data = await getArtisanAvailability({ date: dateStr });
        // Transform data into FullCalendar events
        const formattedEvents = data.map(item => ({
          title: item.is_available ? 'Available' : 'Booked',
          start: item.date,
          allDay: true,
          color: item.is_available ? '#22c55e' : '#ef4444',
        }));
        setEvents(formattedEvents);
      } catch (error) {
        console.error('Failed to load availability:', error);
        toast.error('Could not load artisan availability');
      } finally {
        setLoading(false);
      }
    };
    fetchAvailability();
  }, [currentDate]);

  const handleDateClick = (info) => {
    // This is the correct way to handle date clicks
    const date = info.dateStr;
    if (onDateSelect) {
      onDateSelect(date);
    }
  };

  const handleDatesSet = (info) => {
    // When the view changes, we can fetch data for the new month
    const newDate = info.start;
    setCurrentDate(newDate);
  };

  return (
    <div className="artisan-calendar-container">
      {loading && <div className="loading-spinner">Loading…</div>}
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={events}
        dateClick={handleDateClick}   // ✅ correct
        datesSet={handleDatesSet}
        height="auto"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,dayGridWeek',
        }}
        selectable={true}
        selectMirror={true}
        dayMaxEvents={true}
        weekends={true}
      />
    </div>
  );
}