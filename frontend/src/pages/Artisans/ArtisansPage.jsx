import { ArtisanList } from '../../components/artisans/ArtisanList';

export const ArtisansPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Artisans</h1>
        {/* Optionally add "Add Artisan" button later */}
      </div>
      <ArtisanList />
    </div>
  );
};