import { Flex, Box, Image } from '@mantine/core';
import { useState, useEffect } from "react";

import { ItemGallery } from './ItemGallery';
import { BattleSpinner } from './BattleSpinner';
import { LocationDetails } from './LocationDetails';

export function MainLayout({ apiEndpoint }) {

  console.log("MainLayout loaded");

  const [entry, setEntry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0); // 🔁 this triggers re-fetch
  const [isMoving, setIsMoving] = useState(false);

  const [galleryParams, setGalleryParams] = useState({
      apiEndpoint: "/api/location/items",
      actionPostUrl: "/api/take",
      actionButtonText: "Take"
  });

  useEffect(() => {
    setLoading(true);
    fetch(apiEndpoint)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch data');
        return res.json();
      })
      .then(data => {
        setEntry({
          name: data.name,
          description: data.description,
          imageSrc: `data:image/png;base64,${data.image}`
        });
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [apiEndpoint, refreshKey]); // 🔄 re-run when refreshKey changes

  if (loading) {
      return (
        <BattleSpinner />
      );
  }

  if (error) return <div>Error: {error}</div>;
  if (!entry) return null;

  const handleMove = (direction) => {
      setIsMoving(true);
      fetch('/api/move', {
        method: 'POST',
        body: direction
      })
        .then(res => res.json())
        .then(data => {
          if (data.result === 'OK') {
            setRefreshKey(prev => prev + 1); // ✅ reload data
          } else {
            console.warn('Move failed:', data);
          }
        })
        .catch(err => console.error('Error moving:', err))
        .finally(() => setIsMoving(false));// ✅ Done moving

  };

  return (
    <Flex 
        direction="row"
        style={{
          display: 'flex',
          flexDirection: 'row',
          height: '100vh'
        }}
    >
      {/* Left: Image */}
      <Box style={{ flex: 2 }}>
        <Image src={entry.imageSrc} alt={entry.name} fit="cover" style={{ height: '100%' }} />
      </Box>

      {/* Center: Title + Description + Button */}
      <Box style={{ flex: 1, padding: '2rem' }} bg="dark.7">
        <LocationDetails
          entry={entry}
          isMoving={isMoving}
          handleMove={handleMove}
          galleryParams={galleryParams}
          setGalleryParams={setGalleryParams}
        />
      </Box>

      {/* Right panel: ImageGallery */}
      <Box style={{ 
                flex: 1, 
                padding: '2rem', 
                overflowY: 'auto' // allow the panel independent scrolling
           }} 
           bg="dark.9"
      >
        <ItemGallery apiEndpoint={galleryParams.apiEndpoint} actionPostUrl={galleryParams.actionPostUrl} actionButtonText={galleryParams.actionButtonText} />
      </Box>
    </Flex>
  );
}
