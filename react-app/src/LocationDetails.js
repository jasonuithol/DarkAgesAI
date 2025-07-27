import { Box, Text, Button, Flex } from '@mantine/core';
import { DirectionalControls } from './DirectionalControls';

export function LocationDetails({
  entry,
  isMoving,
  handleMove,
  galleryParams,
  setGalleryParams
}) {
  return (
      <Box style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* Title + Description */}
        <Box>
          <Text size="xl" color="cyan" weight={700}>{entry.name}</Text>
          <Text size="md" color="dimmed" mt="md">{entry.description}</Text>
        </Box>

        {/* Spacer pushes controls and buttons downward */}
        <Box style={{ flexGrow: 1 }} />

        {/* Centered Directional Controls */}
        <Box style={{ display: 'flex', justifyContent: 'center' }}>
          <DirectionalControls isMoving={isMoving} onMove={handleMove} />
        </Box>

        {/* Item Toggle Buttons */}
        <Box mt="md" style={{ display: 'flex', justifyContent: 'center' }}>
          <Flex gap="sm">
            <Button
              onClick={() => setGalleryParams({
                apiEndpoint: "/api/location/items",
                actionPostUrl: "/api/take",
                actionButtonText: "Take"
              })}
              variant={galleryParams.apiEndpoint === "/api/location/items" ? "filled" : "light"}
              color={galleryParams.apiEndpoint === "/api/location/items" ? "cyan" : "gray"}
            >
              Local Items
            </Button>
            <Button
              onClick={() => setGalleryParams({
                apiEndpoint: "/api/inventory",
                actionPostUrl: "/api/drop",
                actionButtonText: "Drop"
              })}
              variant={galleryParams.apiEndpoint === "/api/inventory" ? "filled" : "light"}
              color={galleryParams.apiEndpoint === "/api/inventory" ? "cyan" : "gray"}
            >
              Inventory
            </Button>
          </Flex>
        </Box>
      </Box>
  );
}