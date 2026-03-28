import LiveSection from '@/components/sections/LiveSection';
import UpcomingRacesSection from '@/components/sections/UpcomingRacesSection';
import RaceCalendarSection from '@/components/sections/RaceCalendarSection';
import QualifyingSection from '@/components/sections/QualifyingSection';
import TeamsSection from '@/components/sections/TeamsSection';
import LatestNewsSection from '@/components/sections/LatestNewsSection';
import NewsletterSection from '@/components/sections/NewsletterSection';
import Footer from '@/components/Footer';
import Navbar from '@/components/Navbar';

export default function Home() {
    return (
        <div className="bg-black text-white">
            <Navbar />
            <LiveSection />
            <UpcomingRacesSection />
            <RaceCalendarSection />
            <QualifyingSection />
            <TeamsSection />
            <LatestNewsSection />
            <NewsletterSection />
            <Footer />
        </div>
    );
}
